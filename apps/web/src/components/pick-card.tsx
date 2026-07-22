import Link from "next/link";
import type { Pick } from "@/lib/types";
import { localTime, marketName, odds, pct } from "@/lib/format";

export function PickCard({ pick, locked = false }: { pick: Pick; locked?: boolean }) {
  const breakEven = pick.price > 0 ? 100 / (pick.price + 100) : Math.abs(pick.price) / (Math.abs(pick.price) + 100);
  return (
    <article className="pickCard">
      <div className="pickTop">
        <span className={`grade grade${pick.grade.replace("+", "Plus")}`}>{pick.grade}</span>
        <div>
          <span className="eyebrow">{marketName(pick.market)} · {pick.bookmaker}</span>
          <h3>{pick.selection}{pick.line == null ? "" : ` ${pick.line > 0 ? "+" : ""}${pick.line}`}</h3>
          <p>{pick.matchup} · {localTime(pick.commence_time)}</p>
        </div>
        <strong className="price">{odds(pick.price)}</strong>
      </div>
      <div className="pickGrid">
        <div><span>Model</span><b>{pct(pick.model_probability)}</b></div>
        <div><span>Edge</span><b className="positive">+{pct(pick.edge)}</b></div>
        <div><span>EV</span><b className="positive">+{pct(pick.expected_value)}</b></div>
        <div><span>Fair</span><b>{odds(pick.fair_odds)}</b></div>
        <div><span>Stake</span><b>{pick.units.toFixed(2)}u</b></div>
        <div><span>Confidence</span><b>{pct(pick.confidence, 0)}</b></div>
      </div>
      <div className="confidenceTrack"><i style={{ width: `${pick.confidence * 100}%` }} /></div>
      {locked ? (
        <div className="lockedNote">Upgrade to unlock complete reasoning and every official play.</div>
      ) : (
        <>
          <details className="reasonDetails" open>
            <summary>Why this bet</summary>
            <ul className="reasonList">
              {pick.reasons.filter((reason) => !reason.toLowerCase().startsWith("risk:")).slice(0, 6).map((reason) => <li key={reason}>{reason}</li>)}
            </ul>
          </details>
          {pick.reasons.some((reason) => reason.toLowerCase().startsWith("risk:")) && <details className="reasonDetails"><summary>Primary risks</summary><ul className="reasonList">{pick.reasons.filter((reason) => reason.toLowerCase().startsWith("risk:")).map((reason) => <li key={reason}>{reason.replace(/^Risk:\s*/i, "")}</li>)}</ul></details>}
          <div className="pickMeta"><span>Break-even {(breakEven * 100).toFixed(1)}%</span><span>Data quality {pick.data_quality}/100</span><span>Best book {pick.bookmaker}</span></div>
          <Link className="textLink" href={`/game/${encodeURIComponent(pick.game_id)}`}>Open full game intelligence →</Link>
        </>
      )}
    </article>
  );
}
