import { Shell } from "@/components/shell";
import { AuthForm } from "@/components/auth-form";

export const metadata = { title: "Log in" };
export default function LoginPage() { return <Shell><section className="authPage"><div className="authCopy"><span className="eyebrow">WELCOME BACK</span><h1>Return to the board.</h1><p>Your official card, performance history, and membership are waiting.</p></div><AuthForm mode="login" /></section></Shell>; }
