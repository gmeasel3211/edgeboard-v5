import { Shell } from "@/components/shell";
import { AccountActions } from "@/components/account-actions";
import { currentUser } from "@/lib/auth";

export const metadata = { title: "Account" };

export default async function AccountPage() {
  const user = await currentUser();
  const paid = user?.role === "admin" || user?.tier === "pro" || user?.tier === "elite";
  return <Shell><section className="pageHero"><span className="eyebrow">ACCOUNT</span><h1>Membership and security.</h1><p>Review your access level and open Stripe's secure customer portal to manage billing.</p></section><section className="pageSection"><div className="accountGrid"><section className="panel"><div className="sectionHead"><div><span className="eyebrow">PROFILE</span><h2>{user?.display_name}</h2></div><span className="tierPill">{user?.role === "admin" ? "ADMIN" : user?.tier.toUpperCase()}</span></div><dl className="dataList"><div><dt>Email</dt><dd>{user?.email}</dd></div><div><dt>Email verified</dt><dd>{user?.is_verified ? "Yes" : "Pending"}</dd></div><div><dt>Membership</dt><dd>{user?.tier}</dd></div><div><dt>Account status</dt><dd>{user?.is_active ? "Active" : "Disabled"}</dd></div></dl></section><section className="panel"><div className="sectionHead"><div><span className="eyebrow">BILLING</span><h2>Subscription controls</h2></div></div><p className="panelCopy">Payment methods, invoices, upgrades, and cancellations are handled by Stripe's hosted customer portal.</p>{user?.role === "admin" ? <p className="panelCopy">Administrator access is not tied to a customer subscription.</p> : <AccountActions paid={!!paid} />}</section></div></section></Shell>;
}
