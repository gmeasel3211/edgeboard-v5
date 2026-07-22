"use client";

import { FormEvent, useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export default function Register() {
  const [message, setMessage] = useState("");
  const [inviteCode, setInviteCode] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setInviteCode(params.get("code") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        display_name: form.get("display_name"),
        email: form.get("email"),
        password: form.get("password"),
        invite_code: form.get("invite_code") || null,
      })
    });
    const data = await response.json();
    if (!response.ok) return setMessage(data.detail ?? "Registration failed");
    localStorage.setItem("edgeboard_token", data.access_token);
    window.location.href = "/dashboard";
  }

  return (
    <main className="container">
      <form className="card form" onSubmit={submit}>
        <div className="eyebrow">Create account</div>
        <h2>Start with EdgeBoard</h2>
        <label>Name<input className="input" name="display_name" required /></label>
        <label>Email<input className="input" name="email" type="email" required /></label>
        <label>Password<input className="input" name="password" type="password" minLength={8} required /></label>
        <label>Friend invite code <span className="muted">(optional)</span>
          <textarea
            className="input"
            name="invite_code"
            rows={4}
            value={inviteCode}
            onChange={e => setInviteCode(e.target.value)}
            placeholder="Paste the EdgeBoard invite code here"
          />
        </label>
        <button className="button primary" style={{width:"100%"}}>Create account</button>
        {message && <p className="muted">{message}</p>}
      </form>
    </main>
  );
}
