"use client";

import { FormEvent, useState } from "react";
import { clientApi } from "@/lib/api";

type Overview = {
  policy: Record<string, number>;
  operations: Array<{
    id: string;
    operation: string;
    status: string;
    started_at: string;
    triggered_by: string;
    summary: Record<string, unknown>;
    error: string | null;
  }>;
};

export function AdminConsole({ initial }: { initial: Overview }) {
  const [overview, setOverview] = useState(initial);
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");

  async function reload() {
    setOverview(await clientApi<Overview>("/admin/overview"));
  }

  async function run(action: "refresh" | "force" | "grade") {
    setBusy(action);
    setMessage("");
    try {
      const path = action === "grade" ? "/admin/grade" : "/admin/refresh";
      const body = action === "grade" ? undefined : JSON.stringify({ force_official: action === "force" });
      const result = await clientApi<Record<string, unknown>>(path, { method: "POST", body });
      setMessage(JSON.stringify(result));
      await reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Operation failed");
    } finally {
      setBusy("");
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("settings");
    const form = new FormData(event.currentTarget);
    const values = Object.fromEntries(Array.from(form.entries()).map(([key, value]) => [key, Number(value)]));
    try {
      await clientApi("/admin/settings", { method: "POST", body: JSON.stringify({ values }) });
      setMessage("Model policy saved.");
      await reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Settings failed");
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="adminGrid">
      <section className="panel adminActions">
        <div className="sectionHead"><div><span className="eyebrow">OPERATIONS</span><h2>Model controls</h2></div></div>
        <div className="actionGrid">
          <button className="button" onClick={() => run("refresh")} disabled={!!busy}>{busy === "refresh" ? "Refreshing…" : "Refresh data"}</button>
          <button className="button buttonWarn" onClick={() => run("force")} disabled={!!busy}>{busy === "force" ? "Building…" : "Regenerate official card"}</button>
          <button className="button buttonGhost" onClick={() => run("grade")} disabled={!!busy}>{busy === "grade" ? "Grading…" : "Grade completed games"}</button>
          <a className="button buttonGhost" href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/admin/export/today.csv`} target="_blank">Export today CSV</a>
        </div>
        {message && <pre className="operationMessage">{message}</pre>}
      </section>

      <section className="panel">
        <div className="sectionHead"><div><span className="eyebrow">RISK ENGINE</span><h2>Model policy</h2></div></div>
        <form className="settingsForm" onSubmit={save}>
          {Object.entries(overview.policy).map(([key, value]) => (
            <label key={key}><span>{key.replaceAll("_", " ")}</span><input name={key} type="number" step="any" defaultValue={value} /></label>
          ))}
          <button className="button" disabled={!!busy}>{busy === "settings" ? "Saving…" : "Save policy"}</button>
        </form>
      </section>

      <section className="panel operationPanel">
        <div className="sectionHead"><div><span className="eyebrow">AUDIT TRAIL</span><h2>Recent operations</h2></div></div>
        <div className="tableWrap"><table><thead><tr><th>Status</th><th>Operation</th><th>Started</th><th>Trigger</th><th>Summary</th></tr></thead><tbody>
          {overview.operations.map((row) => <tr key={row.id}><td><span className={`status ${row.status}`}>{row.status}</span></td><td>{row.operation}</td><td>{new Date(row.started_at).toLocaleString()}</td><td>{row.triggered_by}</td><td><code>{row.error ?? JSON.stringify(row.summary)}</code></td></tr>)}
        </tbody></table></div>
      </section>
    </div>
  );
}
