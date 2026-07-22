import { Shell } from "@/components/shell";
import { LineChart } from "@/components/line-chart";
import { MetricCard } from "@/components/metric-card";
import { currentUser } from "@/lib/auth";
import { serverApi } from "@/lib/api";
import { pct, units } from "@/lib/format";
import type { RecordSummary } from "@/lib/types";

export const metadata = { title: "Performance" };

type Performance = {
  summary: RecordSummary;
  daily: Array<{ date: string; wins: number; losses: number; pushes: number; units: number; risked: number; roi: number; cumulative_units: number }>;
  by_market: Array<{ market: string; wins: number; losses: number; pushes: number; units: number; risked: number; roi: number }>;
  by_grade: Array<{ grade: string; wins: number; losses: number; pushes: number; units: number; risked: number; roi: number }>;
};

export default async function PerformancePage() {
  await currentUser();
  const data = await serverApi<Performance>("/dashboard/performance");
  return (
    <Shell>
      <section className="pageHero"><span className="eyebrow">PERFORMANCE CENTER</span><h1>Every result. Every unit. Every close.</h1><p>The model is judged by its frozen official card—not screenshots, deleted losses, or retroactive prices.</p></section>
      <section className="dashboardBody">
        <div className="metricsGrid compact">
          <MetricCard label="Official record" value={`${data.summary.wins}–${data.summary.losses}–${data.summary.pushes}`} note={`${data.summary.total_official} total picks`} />
          <MetricCard label="Net units" value={units(data.summary.units)} note={`${data.summary.units_risked.toFixed(2)}u risked`} tone={data.summary.units >= 0 ? "positiveTone" : "negativeTone"} />
          <MetricCard label="ROI" value={pct(data.summary.roi)} note="Official picks only" />
          <MetricCard label="Average CLV" value={pct(data.summary.average_clv)} note="Closing implied probability" />
        </div>
        <section className="panel"><div className="sectionHead"><div><span className="eyebrow">CUMULATIVE RESULTS</span><h2>Units over time</h2></div></div><LineChart data={data.daily} /></section>
        <div className="splitPanels">
          <section className="panel"><div className="sectionHead"><div><span className="eyebrow">MARKET SPLITS</span><h2>By bet type</h2></div></div><div className="tableWrap"><table><thead><tr><th>Market</th><th>Record</th><th>Units</th><th>ROI</th></tr></thead><tbody>{data.by_market.map((row) => <tr key={row.market}><td>{row.market}</td><td>{row.wins}–{row.losses}–{row.pushes}</td><td className={row.units >= 0 ? "positive" : "negative"}>{units(row.units)}</td><td>{pct(row.roi)}</td></tr>)}</tbody></table></div></section>
          <section className="panel"><div className="sectionHead"><div><span className="eyebrow">GRADE SPLITS</span><h2>By confidence tier</h2></div></div><div className="tableWrap"><table><thead><tr><th>Grade</th><th>Record</th><th>Units</th><th>ROI</th></tr></thead><tbody>{data.by_grade.map((row) => <tr key={row.grade}><td>{row.grade}</td><td>{row.wins}–{row.losses}–{row.pushes}</td><td className={row.units >= 0 ? "positive" : "negative"}>{units(row.units)}</td><td>{pct(row.roi)}</td></tr>)}</tbody></table></div></section>
        </div>
        <section className="panel"><div className="sectionHead"><div><span className="eyebrow">DAILY LEDGER</span><h2>Auditable history</h2></div></div><div className="tableWrap"><table><thead><tr><th>Date</th><th>Record</th><th>Risked</th><th>Units</th><th>ROI</th><th>Cumulative</th></tr></thead><tbody>{[...data.daily].reverse().map((row) => <tr key={row.date}><td>{row.date}</td><td>{row.wins}–{row.losses}–{row.pushes}</td><td>{row.risked.toFixed(2)}u</td><td className={row.units >= 0 ? "positive" : "negative"}>{units(row.units)}</td><td>{pct(row.roi)}</td><td>{units(row.cumulative_units)}</td></tr>)}</tbody></table></div></section>
      </section>
    </Shell>
  );
}
