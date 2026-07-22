"use client";

import { useEffect, useState } from "react";
import { API_URL, authHeaders, getPlanView, PlanView, setPlanView } from "@/lib/api";

const actions = [
  ["Full refresh", "/api/v1/admin/refresh/full"],
  ["MLB data", "/api/v1/admin/refresh/mlb"],
  ["Odds + model", "/api/v1/admin/refresh/odds"],
  ["Weather", "/api/v1/admin/refresh/weather"],
  ["Rebuild card", "/api/v1/admin/rebuild-card"],
];

export default function AdminPage() {
  const [output, setOutput] = useState("Select an operation.");
  const [view, setView] = useState<PlanView>("actual");
  const [tier, setTier] = useState("pro");
  const [days, setDays] = useState(30);
  const [label, setLabel] = useState("Friends beta");
  const [invite, setInvite] = useState("");

  useEffect(() => setView(getPlanView()), []);

  async function run(path: string) {
    setOutput("Running...");
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: authHeaders(),
    });
    const data = await response.json();
    setOutput(JSON.stringify(data, null, 2));
  }

  function applyView(next: PlanView) {
    setView(next);
    setPlanView(next);
  }

  async function generateInvite() {
    setInvite("Generating...");
    const response = await fetch(`${API_URL}/api/v1/admin/invites`, {
      method: "POST",
      headers: {"Content-Type": "application/json", ...authHeaders()},
      body: JSON.stringify({tier, days_valid: days, label}),
    });
    const data = await response.json();
    if (!response.ok) return setInvite(data.detail ?? "Unable to generate code");
    setInvite(data.code);
  }

  async function copyInvite() {
    await navigator.clipboard.writeText(invite);
    setOutput("Invite code copied to clipboard.");
  }

  return (
    <main className="section container">
      <div className="eyebrow">Administrator</div>
      <h1 style={{fontSize:"58px", textAlign:"left", marginLeft:0}}>Control center</h1>

      <section className="card" style={{marginBottom:24}}>
        <h2>Preview subscription views</h2>
        <p className="muted">Switch the site into a simulated customer plan. Your real account remains an administrator.</p>
        <div className="actions" style={{justifyContent:"flex-start"}}>
          {(["actual", "free", "pro", "elite"] as PlanView[]).map(option => (
            <button
              key={option}
              className={view === option ? "button primary" : "button"}
              onClick={() => applyView(option)}
            >
              {option === "actual" ? "Actual Admin" : option.toUpperCase()}
            </button>
          ))}
        </div>
        <p style={{marginTop:14}}><strong>Current preview:</strong> {view}</p>
      </section>

      <section className="card" style={{marginBottom:24}}>
        <h2>Friend invite code</h2>
        <p className="muted">Generate a simple beta code that grants Pro or Elite when a new friend registers.</p>
        <div className="form" style={{maxWidth:520}}>
          <label>Access level
            <select className="input" value={tier} onChange={e => setTier(e.target.value)}>
              <option value="pro">Pro</option>
              <option value="elite">Elite</option>
            </select>
          </label>
          <label>Valid for
            <select className="input" value={days} onChange={e => setDays(Number(e.target.value))}>
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </label>
          <label>Label
            <input className="input" value={label} onChange={e => setLabel(e.target.value)} />
          </label>
          <button className="button primary" onClick={generateInvite}>Generate invite code</button>
        </div>
        {invite && (
          <div style={{marginTop:18}}>
            <textarea className="input" readOnly value={invite} rows={5} style={{width:"100%"}} />
            {invite.startsWith("EB-") && <button className="button" onClick={copyInvite}>Copy code</button>}
          </div>
        )}
      </section>

      <section className="card">
        <h2>Data operations</h2>
        <div className="actions" style={{justifyContent:"flex-start"}}>
          {actions.map(([actionLabel, path]) => (
            <button className="button primary" onClick={() => run(path)} key={path}>{actionLabel}</button>
          ))}
        </div>
        <pre style={{marginTop:"24px", whiteSpace:"pre-wrap", overflow:"auto"}}>{output}</pre>
      </section>
    </main>
  );
}
