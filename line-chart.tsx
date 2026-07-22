import { Suspense } from "react";
import { Shell } from "@/components/shell";
import { TokenForm } from "@/components/token-form";

export const metadata = { title: "Verify email" };
export default function VerifyPage() { return <Shell><section className="authPage"><div className="authCopy"><span className="eyebrow">ACCOUNT SECURITY</span><h1>Verify your email.</h1><p>Verification protects subscriber access and account recovery.</p></div><Suspense fallback={<div className="authForm">Loading…</div>}><TokenForm mode="verify" /></Suspense></section></Shell>; }
