"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

const pretty = (value?: string) =>
  value ? value.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase()) : "Waiting";

export default function LiveOddsPage() {
  const [data, setData] = useState<any>(null);
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    const load = () => fetch(`${API_URL}/api/v1/system/status`).then(r => r.json()).then(setData);
    load();
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <main className="section container">
      <div className="eyebrow">Milestone 3.1 operations</div>
      <h1 style={{fontSize:"58px", textAlign:"left", marginLeft:0}}>System health</h1>
      <p className="section-lead">Provider health, data freshness, refresh results, and safe recovery information.</p>

      <div className="grid grid-3">
        {Object.entries(data?.services ?? {}).map(([name, service]: [string, any]) => (
          <div className="card" key={name}>
            <div className="pick-top">
              <strong style={{textTransform:"uppercase"}}>{name}</strong>
              <span className="badge">{pretty(service.status)}</span>
            </div>
            {service.last_run_minutes_ago != null && <p className="muted">Last run {service.last_run_minutes_ago}m ago</p>}
            {service.last_data_minutes_ago != null && <p className="muted">Freshest data {service.last_data_minutes_ago}m ago</p>}
            {service.interval_minutes != null && <p className="muted">Every {service.interval_minutes} minutes</p>}
          </div>
        ))}
      </div>

      <section className="section">
        <h2>Current data</h2>
        <div className="grid grid-3">
          <div className="card"><div className="stat">{data?.counts?.upcoming_games ?? 0}</div><div className="muted">Upcoming games</div></div>
          <div className="card"><div className="stat">{data?.counts?.odds_snapshots ?? 0}</div><div className="muted">Odds snapshots</div></div>
          <div className="card"><div className="stat">{data?.counts?.active_picks ?? 0}</div><div className="muted">Active picks</div></div>
        </div>
      </section>

      <section className="section">
        <h2>Recent pipeline runs</h2>
        <div className="grid">
          {(data?.recent_runs ?? []).map((run: any, index: number) => (
            <article className="card" key={index}>
              <div className="pick-top">
                <div>
                  <strong style={{textTransform:"uppercase"}}>{run.job}</strong>
                  <p className="muted">{run.duration_ms != null ? `${run.duration_ms} ms` : "Duration unavailable"}</p>
                </div>
                <span className="badge">{pretty(run.status)}</span>
              </div>

              {run.error && (
                <div className="metric" style={{marginTop:16}}>
                  <strong>What happened</strong>
                  <span className="muted">{run.error.message}</span>
                  <span className="muted">EdgeBoard will retry recoverable failures automatically.</span>
                </div>
              )}

              <button className="button" style={{marginTop:16}} onClick={() => setOpen(open === index ? null : index)}>
                {open === index ? "Hide job details" : "View job details"}
              </button>

              {open === index && (
                <pre className="muted" style={{whiteSpace:"pre-wrap", overflow:"auto", marginTop:16}}>
                  {JSON.stringify({summary: run.summary, error: run.error}, null, 2)}
                </pre>
              )}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
