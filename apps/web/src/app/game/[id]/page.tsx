import { Shell } from "@/components/shell";
import { PickCard } from "@/components/pick-card";
import { currentUser } from "@/lib/auth";
import { serverApi } from "@/lib/api";
import { localTime, pct } from "@/lib/format";
import type { Pick } from "@/lib/types";

export const metadata = { title: "Game Intelligence" };

type GameDetail = {
  game: { id: string; away_team: string; home_team: string; commence_time: string; venue: string; away_pitcher: string | null; home_pitcher: string | null; metadata: Record<string, any> };
  projection: null | { away_runs: number; home_runs: number; away_win_probability: number; home_win_probability: number; total_mean: number; data_quality: number; confidence: number; reasons: string[]; inputs: Record<string, any> };
  markets: Pick[];
};

export default async function GamePage({ params }: { params: Promise<{ id: string }> }) {
  await currentUser();
  const { id } = await params;
  const data = await serverApi<GameDetail>(`/dashboard/games/${encodeURIComponent(id)}`);
  const p = data.projection;
  return (
    <Shell>
      <section className="gameHero"><div><span className="eyebrow">GAME INTELLIGENCE · {localTime(data.game.commence_time)}</span><h1>{data.game.away_team}<em> at </em>{data.game.home_team}</h1><p>{data.game.venue} · {data.game.away_pitcher ?? "Away starter TBD"} vs. {data.game.home_pitcher ?? "Home starter TBD"}</p></div>{p && <div className="scoreProjection"><span>PROJECTED SCORE</span><strong>{p.away_runs.toFixed(1)} <i>–</i> {p.home_runs.toFixed(1)}</strong><small>{pct(p.home_win_probability)} home win probability</small></div>}</section>
      <section className="dashboardBody">
        {p ? <>
          <div className="intelligenceGrid">
            <article><span>Away win</span><strong>{pct(p.away_win_probability)}</strong><small>{data.game.away_team}</small></article>
            <article><span>Home win</span><strong>{pct(p.home_win_probability)}</strong><small>{data.game.home_team}</small></article>
            <article><span>Projected total</span><strong>{p.total_mean.toFixed(1)}</strong><small>Monte Carlo mean</small></article>
            <article><span>Confidence</span><strong>{pct(p.confidence, 0)}</strong><small>Quality {p.data_quality}/100</small></article>
          </div>
          <div className="splitPanels">
            <section className="panel"><div className="sectionHead"><div><span className="eyebrow">WHY THE MODEL MOVED</span><h2>Projection reasoning</h2></div></div><ul className="deepReasonList">{p.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></section>
            <section className="panel"><div className="sectionHead"><div><span className="eyebrow">CONDITIONS</span><h2>Game environment</h2></div></div><dl className="dataList"><div><dt>Weather</dt><dd>{data.game.metadata?.weather?.summary ?? "Unavailable"}</dd></div><div><dt>Temperature</dt><dd>{data.game.metadata?.weather?.temperature ?? "—"}°F</dd></div><div><dt>Wind</dt><dd>{data.game.metadata?.weather?.wind_speed ?? "—"} mph</dd></div><div><dt>Park factor</dt><dd>{data.game.metadata?.park_factor?.toFixed?.(3) ?? data.game.metadata?.park_factor ?? "—"}</dd></div><div><dt>Rest</dt><dd>Away {data.game.metadata?.rest?.away ?? "—"} · Home {data.game.metadata?.rest?.home ?? "—"}</dd></div><div><dt>Umpire</dt><dd>{data.game.metadata?.umpire ?? "Not assigned"}</dd></div></dl></section>
          </div>
        </> : <div className="emptyState"><strong>Projection unavailable.</strong><span>The data refresh may still be running.</span></div>}
        <section className="panel"><div className="sectionHead"><div><span className="eyebrow">MARKET BOARD</span><h2>Evaluated prices</h2></div><span>{data.markets.length} outcomes</span></div><div className="pickList">{data.markets.map((pick) => <PickCard key={pick.id} pick={pick} />)}</div></section>
      </section>
    </Shell>
  );
}
