import { Shell } from "@/components/shell";
import { AuthForm } from "@/components/auth-form";

export const metadata = { title: "Create account" };
export default function RegisterPage() { return <Shell><section className="authPage"><div className="authCopy"><span className="eyebrow">START FREE</span><h1>Build a sharper process.</h1><p>Create your account to see the featured pick and verified performance. Upgrade only when the product earns it.</p></div><AuthForm mode="register" /></section></Shell>; }
