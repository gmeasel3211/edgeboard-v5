"use client";

import { FormEvent, useState } from "react";
import { useSearchParams } from "next/navigation";
import { clientApi } from "@/lib/api";

export function TokenForm({ mode }: { mode: "verify" | "reset" }) {
  const params = useSearchParams();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const token = params.get("token") ?? String(form.get("token") ?? "");
    const payload = mode === "verify" ? { token } : { token, password: form.get("password") };
    try {
      const result = await clientApi<{ message: string }>(mode === "verify" ? "/auth/verify-email" : "/auth/reset-password", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setMessage(result.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The link could not be processed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="authForm" onSubmit={submit}>
      {!params.get("token") && <label>Secure token<input name="token" required /></label>}
      {mode === "reset" && <label>New password<input name="password" type="password" minLength={12} required /></label>}
      {error && <p className="formError">{error}</p>}
      {message && <p className="formSuccess">{message}</p>}
      <button className="button" disabled={busy}>{busy ? "Working…" : mode === "verify" ? "Verify email" : "Reset password"}</button>
    </form>
  );
}
