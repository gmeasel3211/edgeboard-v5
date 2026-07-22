"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { clientApi } from "@/lib/api";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const payload = mode === "login"
      ? { email: form.get("email"), password: form.get("password") }
      : { email: form.get("email"), password: form.get("password"), display_name: form.get("display_name") };
    try {
      await clientApi(`/auth/${mode}`, { method: "POST", body: JSON.stringify(payload) });
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to continue.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="authForm" onSubmit={submit}>
      {mode === "register" && <label>Display name<input name="display_name" minLength={2} maxLength={120} required autoComplete="name" /></label>}
      <label>Email<input name="email" type="email" required autoComplete="email" /></label>
      <label>Password<input name="password" type="password" minLength={12} required autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
      {mode === "register" && <small>Use 12+ characters with uppercase, lowercase, a number, and a symbol.</small>}
      {error && <p className="formError">{error}</p>}
      <button className="button" disabled={busy}>{busy ? "Working…" : mode === "login" ? "Log in" : "Create account"}</button>
      <p className="formSwitch">
        {mode === "login" ? <>New to EdgeBoard? <Link href="/register">Create an account</Link></> : <>Already a member? <Link href="/login">Log in</Link></>}
      </p>
    </form>
  );
}
