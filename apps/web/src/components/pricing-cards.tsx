"use client";

import Link from "next/link";
import { useState } from "react";
import { clientApi } from "@/lib/api";

const plans = [
  { id: "free", name: "Free", price: 0, description: "A transparent look at the model.", features: ["Public verified record", "One featured official pick", "Weekly performance recap"] },
  { id: "pro", name: "Pro", price: 29, description: "The complete daily betting card.", features: ["Every official pick", "Model probability and fair odds", "Game intelligence pages", "Full performance center"] },
  { id: "elite", name: "Elite", price: 59, description: "For serious bettors who want the whole board.", features: ["Everything in Pro", "Qualified watchlist", "Advanced market filters", "CSV exports and priority alerts"] }
];

export function PricingCards({ authenticated = false }: { authenticated?: boolean }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function checkout(plan: "pro" | "elite") {
    setBusy(plan);
    setError("");
    try {
      const data = await clientApi<{ url: string }>("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan })
      });
      window.location.href = data.url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout could not be started.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <div className="pricingGrid">
        {plans.map((plan) => (
          <article className={`pricingCard ${plan.id === "pro" ? "featured" : ""}`} key={plan.id}>
            {plan.id === "pro" && <span className="popular">MOST POPULAR</span>}
            <span className="eyebrow">{plan.name}</span>
            <div className="planPrice"><strong>${plan.price}</strong><span>{plan.price ? "/month" : "forever"}</span></div>
            <p>{plan.description}</p>
            <ul>{plan.features.map((feature) => <li key={feature}>✓ {feature}</li>)}</ul>
            {plan.id === "free" ? (
              <Link className="button buttonGhost" href={authenticated ? "/dashboard" : "/register"}>Start free</Link>
            ) : authenticated ? (
              <button className="button" onClick={() => checkout(plan.id as "pro" | "elite")} disabled={busy !== null}>
                {busy === plan.id ? "Opening checkout…" : `Choose ${plan.name}`}
              </button>
            ) : (
              <Link className="button" href="/register">Create account</Link>
            )}
          </article>
        ))}
      </div>
      {error && <p className="formError">{error}</p>}
    </>
  );
}
