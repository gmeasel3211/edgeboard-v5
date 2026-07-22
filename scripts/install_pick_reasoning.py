from pathlib import Path
import re
import sys

project = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
pipeline_path = project / "apps/api/app/services/pipeline.py"
pickcard_path = project / "apps/web/components/PickCard.tsx"

if not pipeline_path.exists() or not pickcard_path.exists():
    raise SystemExit("Run this from the edgeboard-v3 repository root, or pass that folder path.")

pipeline = pipeline_path.read_text(encoding="utf-8")

new_rebuild = """    def rebuild_card(self) -> dict:
        with SessionLocal() as db:
            db.execute(delete(Pick).where(Pick.status == "pending"))
            games = list(db.scalars(select(Game).where(Game.starts_at >= datetime.now(timezone.utc))).all())
            created = 0
            skipped_missing_team_data = 0

            for game in games:
                latest_time = db.scalar(
                    select(OddsSnapshot.captured_at)
                    .where(
                        OddsSnapshot.game_external_id == game.external_id,
                        OddsSnapshot.market == "h2h",
                    )
                    .order_by(OddsSnapshot.captured_at.desc())
                    .limit(1)
                )
                if not latest_time:
                    continue

                odds = list(db.scalars(select(OddsSnapshot).where(
                    OddsSnapshot.game_external_id == game.external_id,
                    OddsSnapshot.market == "h2h",
                    OddsSnapshot.captured_at == latest_time,
                )).all())

                by_book = defaultdict(list)
                for odd in odds:
                    by_book[odd.bookmaker].append(odd)

                season = date.today().year
                captured = date.today().isoformat()

                home_team = db.scalar(select(TeamSnapshot).where(
                    TeamSnapshot.season == season,
                    TeamSnapshot.captured_date == captured,
                    TeamSnapshot.team_name == game.home_team,
                ))
                away_team = db.scalar(select(TeamSnapshot).where(
                    TeamSnapshot.season == season,
                    TeamSnapshot.captured_date == captured,
                    TeamSnapshot.team_name == game.away_team,
                ))

                mlb_game = db.scalar(
                    select(Game)
                    .where(
                        Game.home_team == game.home_team,
                        Game.away_team == game.away_team,
                        Game.mlb_game_pk.is_not(None),
                    )
                    .order_by(Game.starts_at.asc())
                    .limit(1)
                )

                home_pitcher_id = game.home_probable_pitcher_id or (mlb_game.home_probable_pitcher_id if mlb_game else None)
                away_pitcher_id = game.away_probable_pitcher_id or (mlb_game.away_probable_pitcher_id if mlb_game else None)
                home_pitcher_name = game.home_probable_pitcher or (mlb_game.home_probable_pitcher if mlb_game else "")
                away_pitcher_name = game.away_probable_pitcher or (mlb_game.away_probable_pitcher if mlb_game else "")

                home_pitcher = db.scalar(select(PitcherSnapshot).where(
                    PitcherSnapshot.pitcher_id == home_pitcher_id,
                    PitcherSnapshot.season == season,
                    PitcherSnapshot.captured_date == captured,
                )) if home_pitcher_id else None
                away_pitcher = db.scalar(select(PitcherSnapshot).where(
                    PitcherSnapshot.pitcher_id == away_pitcher_id,
                    PitcherSnapshot.season == season,
                    PitcherSnapshot.captured_date == captured,
                )) if away_pitcher_id else None

                if not home_team or not away_team:
                    skipped_missing_team_data += 1
                    continue

                best_by_selection = {}

                for bookmaker, outcomes in by_book.items():
                    home_outcome = next((x for x in outcomes if x.selection == game.home_team), None)
                    away_outcome = next((x for x in outcomes if x.selection == game.away_team), None)
                    if not home_outcome or not away_outcome:
                        continue

                    nv_home, nv_away = no_vig_probabilities([home_outcome.american_odds, away_outcome.american_odds])
                    home_model, factors = projected_home_probability(home_team, away_team, home_pitcher, away_pitcher, nv_home)

                    for outcome, model_prob, market_prob in [
                        (home_outcome, home_model, nv_home),
                        (away_outcome, 1 - home_model, nv_away),
                    ]:
                        metrics = evaluate_moneyline(outcome.selection, outcome.american_odds, model_prob, market_prob)
                        if metrics["edge_percent"] < 1.5 or metrics["expected_value_percent"] < 1.0:
                            continue
                        existing = best_by_selection.get(outcome.selection)
                        if existing is None or outcome.american_odds > existing["outcome"].american_odds:
                            best_by_selection[outcome.selection] = {
                                "outcome": outcome,
                                "model_prob": model_prob,
                                "market_prob": market_prob,
                                "metrics": metrics,
                            }

                for selection, candidate in best_by_selection.items():
                    outcome = candidate["outcome"]
                    model_prob = candidate["model_prob"]
                    market_prob = candidate["market_prob"]
                    metrics = candidate["metrics"]

                    is_home = selection == game.home_team
                    selected_team = home_team if is_home else away_team
                    opponent_team = away_team if is_home else home_team
                    selected_pitcher = home_pitcher if is_home else away_pitcher
                    opponent_pitcher = away_pitcher if is_home else home_pitcher
                    selected_pitcher_name = home_pitcher_name if is_home else away_pitcher_name
                    opponent_pitcher_name = away_pitcher_name if is_home else home_pitcher_name

                    implied = american_to_implied(outcome.american_odds) * 100
                    probability_gap = (model_prob - market_prob) * 100

                    explanation_lines = [
                        f"VALUE|{outcome.bookmaker.title()} offers the best tracked price at {outcome.american_odds:+d}. The line requires about {implied:.1f}% to break even, while EdgeBoard estimates {model_prob * 100:.1f}%.",
                        f"WHY|The no-vig market baseline is {market_prob * 100:.1f}%. EdgeBoard is {probability_gap:.1f} percentage points higher on {selection}, creating {metrics['expected_value_percent']:.1f}% estimated EV.",
                        f"WHY|Season run differential: {selection} {selected_team.run_differential_per_game:+.2f} runs per game versus {opponent_team.team_name} {opponent_team.run_differential_per_game:+.2f}. Records: {selected_team.wins}-{selected_team.losses} versus {opponent_team.wins}-{opponent_team.losses}.",
                    ]

                    if selected_pitcher and opponent_pitcher:
                        explanation_lines.append(
                            f"WHY|Probable pitching matchup: {selected_pitcher_name or selected_pitcher.pitcher_name} ({selected_pitcher.era:.2f} ERA, {selected_pitcher.whip:.2f} WHIP) against {opponent_pitcher_name or opponent_pitcher.pitcher_name} ({opponent_pitcher.era:.2f} ERA, {opponent_pitcher.whip:.2f} WHIP)."
                        )
                        explanation_lines.append("DATA|Team and probable-pitcher data were available for this projection.")
                        explanation_lines.append("RISK|Starting pitchers can change before first pitch. Bullpen availability, confirmed lineups, injuries, and late weather changes are not yet fully modeled.")
                    else:
                        explanation_lines.append("DATA|Probable-pitcher statistics were incomplete when this card was built. This recommendation is supported by team performance and market value, but pitching uncertainty lowers its strength.")
                        explanation_lines.append("RISK|The largest risk is incomplete probable-pitcher information. Confirm both starters and recheck the price before betting.")
                        metrics["confidence"] = min(metrics["confidence"], 62.0)
                        metrics["units"] = min(metrics["units"], 0.25)

                    db.add(Pick(
                        sport="MLB",
                        game_id=game.external_id,
                        matchup=f"{game.away_team} @ {game.home_team}",
                        market="moneyline",
                        selection=selection,
                        sportsbook=outcome.bookmaker.title(),
                        american_odds=outcome.american_odds,
                        model_probability=model_prob,
                        market_probability=market_prob,
                        starts_at=game.starts_at,
                        status="pending",
                        explanation="\\n".join(explanation_lines),
                        **metrics,
                    ))
                    created += 1

            db.commit()

        return {
            "picks": created,
            "skipped_missing_team_data": skipped_missing_team_data,
            "note": "One best-price pick per selection; market-only projections are not published.",
        }

"""

pattern = re.compile(
    r"    def rebuild_card\(self\) -> dict:\n.*?(?=    def _start_run\(self, job_name: str\) -> int:)",
    re.S,
)
if not pattern.search(pipeline):
    raise SystemExit("Could not locate rebuild_card() in pipeline.py.")

pipeline_path.write_text(pattern.sub(new_rebuild, pipeline), encoding="utf-8")

pickcard = """"use client";

import { useMemo, useState } from "react";
import type { Pick } from "@/lib/api";

type ExplanationSection = {
  value: string[];
  reasons: string[];
  data: string[];
  risks: string[];
  fallback: string[];
};

function parseExplanation(explanation: string): ExplanationSection {
  const sections: ExplanationSection = {
    value: [],
    reasons: [],
    data: [],
    risks: [],
    fallback: [],
  };

  for (const rawLine of (explanation || "").split("\\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    const divider = line.indexOf("|");
    if (divider === -1) {
      sections.fallback.push(line);
      continue;
    }
    const type = line.slice(0, divider);
    const text = line.slice(divider + 1);
    if (type === "VALUE") sections.value.push(text);
    else if (type === "WHY") sections.reasons.push(text);
    else if (type === "DATA") sections.data.push(text);
    else if (type === "RISK") sections.risks.push(text);
    else sections.fallback.push(text);
  }
  return sections;
}

export function PickCard({ pick }: { pick: Pick }) {
  const [expanded, setExpanded] = useState(true);
  const sections = useMemo(() => parseExplanation(pick.explanation), [pick.explanation]);
  const breakEven = pick.american_odds > 0
    ? 100 / (pick.american_odds + 100)
    : Math.abs(pick.american_odds) / (Math.abs(pick.american_odds) + 100);

  return (
    <article className="card">
      <div className="pick-top">
        <div>
          <div className="eyebrow">BEST LINE - {pick.sportsbook}</div>
          <h3>{pick.matchup}</h3>
          <div className="muted">
            {pick.selection} - {pick.american_odds > 0 ? "+" : ""}{pick.american_odds}
          </div>
        </div>
        <span className="badge">{pick.confidence.toFixed(0)} confidence</span>
      </div>

      <div className="metrics">
        <div className="metric"><span className="muted">Edge</span><strong>{pick.edge_percent.toFixed(1)}%</strong></div>
        <div className="metric"><span className="muted">EV</span><strong>{pick.expected_value_percent.toFixed(1)}%</strong></div>
        <div className="metric"><span className="muted">Model</span><strong>{(pick.model_probability * 100).toFixed(1)}%</strong></div>
        <div className="metric"><span className="muted">Break-even</span><strong>{(breakEven * 100).toFixed(1)}%</strong></div>
        <div className="metric"><span className="muted">Stake</span><strong>{pick.units.toFixed(2)}u</strong></div>
      </div>

      <button className="button" style={{marginTop: 18}} onClick={() => setExpanded(current => !current)}>
        {expanded ? "Hide reasoning" : "Why EdgeBoard likes this pick"}
      </button>

      {expanded && (
        <div style={{marginTop: 18}}>
          {sections.value.map((text, index) => (
            <div className="metric" style={{marginBottom: 12}} key={`value-${index}`}>
              <strong>Best-line value</strong>
              <span className="muted">{text}</span>
            </div>
          ))}

          {sections.reasons.length > 0 && (
            <section style={{marginTop: 18}}>
              <h4 style={{marginBottom: 10}}>Why this bet</h4>
              <ul style={{display: "grid", gap: 9, paddingLeft: 20}}>
                {sections.reasons.map((text, index) => <li key={`reason-${index}`}>{text}</li>)}
              </ul>
            </section>
          )}

          {sections.data.map((text, index) => (
            <div className="metric" style={{marginTop: 16}} key={`data-${index}`}>
              <strong>Data quality</strong>
              <span className="muted">{text}</span>
            </div>
          ))}

          {sections.risks.length > 0 && (
            <section style={{marginTop: 18}}>
              <h4 style={{marginBottom: 8}}>Primary risks</h4>
              {sections.risks.map((text, index) => <p className="muted" key={`risk-${index}`}>{text}</p>)}
            </section>
          )}

          {sections.fallback.map((text, index) => <p className="muted" key={`fallback-${index}`}>{text}</p>)}
        </div>
      )}
    </article>
  );
}
"""

pickcard_path.write_text(pickcard, encoding="utf-8")
print("Hotfix installed successfully.")
print("Commit and push, wait for Render, then click Admin > Rebuild card.")
