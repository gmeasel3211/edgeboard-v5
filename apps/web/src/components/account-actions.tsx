"use client";

import Link from "next/link";
import { useState } from "react";
import { clientApi } from "@/lib/api";

export function AccountActions({ paid }: { paid: boolean }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function portal() {
    setBusy(true);
    setError("");
    try {
      const data = await clientApi<{ url: string }>("/billing/portal", { method: "POST" });
      window.location.href = data.url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Billing portal unavailable");
      setBusy(false);
    }
  }

  return <div className="accountActions">{paid ? <button className="button" disabled={busy} onClick={portal}>{busy ? "Opening portal…" : "Manage billing"}</button> : <Link className="button" href="/pricing">Upgrade membership</Link>}{error && <p className="formError">{error}</p>}</div>;
}
