import { Shell } from "@/components/shell";
import { serverApi } from "@/lib/api";
import { currentUser } from "@/lib/auth";
import { redirect } from "next/navigation";

type Status = {
  checked_at: string;
  services: Record<string, string>;
  counts: Record<string, number>;
  freshness: { latest_odds_at: string | null; odds_age_minutes: number | null };
  recent_runs: Array<{ id: string; operation: string; status: string; started_at: string; triggered_by: string; summary: Record<string, unknown>; error: string | null }>;
};

export const metadata = { title: "System Health" };

export default async function LiveOddsPage() {
  const user = await currentUser();
  if (user?.role !== "admin") redirect("/dashboard");
  const data = await serverApi<Status>("/system/status");
  return <Shell>
    <section className="pageHero"><span className="eyebrow">OPERATIONS</span><h1>System Health</h1><p>Live status for EdgeBoard data providers, database activity, and scheduled refreshes.</p></section>
    <section className="dashboardBody healthStack">
      <div className="healthGrid">{Object.entries(data.services).map(([name, state]) => <article className="panel healthCard" key={name}><span>{name.replaceAll("_", " ")}</span><strong className={`status ${state === "healthy" ? "success" : "failed"}`}>{state}</strong></article>)}</div>
      <div className="healthGrid">{Object.entries(data.counts).map(([name, value]) => <article className="panel healthCard" key={name}><span>{name.replaceAll("_", " ")}</span><strong>{value.toLocaleString()}</strong></article>)}</div>
      <section className="panel operationPanel"><div className="sectionHead"><div><span className="eyebrow">PIPELINE</span><h2>Recent refreshes</h2></div><p>Latest odds: {data.freshness.latest_odds_at ? new Date(data.freshness.latest_odds_at).toLocaleString() : "None yet"}</p></div>
      <div className="tableWrap"><table><thead><tr><th>Status</th><th>Started</th><th>Trigger</th><th>Duration</th><th>Details</th></tr></thead><tbody>{data.recent_runs.map(run => <tr key={run.id}><td><span className={`status ${run.status}`}>{run.status}</span></td><td>{new Date(run.started_at).toLocaleString()}</td><td>{run.triggered_by}</td><td>{typeof run.summary.duration_ms === "number" ? `${run.summary.duration_ms} ms` : "—"}</td><td><details><summary>{run.error ?? "View summary"}</summary><pre className="operationMessage">{JSON.stringify(run.summary, null, 2)}</pre></details></td></tr>)}</tbody></table></div></section>
    </section>
  </Shell>;
}
