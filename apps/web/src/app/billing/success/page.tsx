import Link from "next/link";
import { Shell } from "@/components/shell";

export const metadata = { title: "Membership active" };
export default function BillingSuccessPage() { return <Shell><section className="successPage"><span className="successIcon">✓</span><span className="eyebrow">PAYMENT RECEIVED</span><h1>Your EdgeBoard membership is being activated.</h1><p>Stripe will confirm the subscription through a signed webhook. Access usually updates within seconds.</p><Link className="button" href="/dashboard">Open dashboard</Link></section></Shell>; }
