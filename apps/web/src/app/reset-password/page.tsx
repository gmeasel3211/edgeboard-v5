import { Suspense } from "react";
import { Shell } from "@/components/shell";
import { TokenForm } from "@/components/token-form";

export const metadata = { title: "Reset password" };
export default function ResetPage() { return <Shell><section className="authPage"><div className="authCopy"><span className="eyebrow">ACCOUNT RECOVERY</span><h1>Choose a new password.</h1><p>All existing sessions will be revoked after the password changes.</p></div><Suspense fallback={<div className="authForm">Loading…</div>}><TokenForm mode="reset" /></Suspense></section></Shell>; }
