import { Shell } from "@/components/shell";
import { AdminConsole } from "@/components/admin-console";
import { currentUser } from "@/lib/auth";
import { serverApi } from "@/lib/api";
import { redirect } from "next/navigation";

export const metadata = { title: "Admin" };

type Overview = {
  policy: Record<string, number>;
  operations: Array<{ id: string; operation: string; status: string; started_at: string; triggered_by: string; summary: Record<string, unknown>; error: string | null }>;
};

export default async function AdminPage() {
  const user = await currentUser();
  if (user?.role !== "admin") redirect("/dashboard");
  const overview = await serverApi<Overview>("/admin/overview");
  return <Shell><section className="pageHero"><span className="eyebrow">ADMIN OPERATIONS</span><h1>Control the platform without touching production code.</h1><p>Refresh data, regenerate the card, grade results, tune model policy, and inspect the audit trail.</p></section><section className="dashboardBody"><AdminConsole initial={overview} /></section></Shell>;
}
