import Link from "next/link";
import { currentUser } from "@/lib/auth";
import { Logo } from "./logo";
import { LogoutButton } from "./logout-button";

export async function Shell({ children }: { children: React.ReactNode }) {
  const user = await currentUser(true);
  return (
    <>
      <nav className="siteNav">
        <Logo />
        <div className="navLinks">
          <Link href="/pricing">Pricing</Link>
          {user && <Link href="/dashboard">Dashboard</Link>}
          {user && <Link href="/account">Account</Link>}
          {user && user.tier !== "free" && <Link href="/performance">Performance</Link>}
          {user?.role === "admin" && <Link href="/live-odds">System Health</Link>}
          {user?.role === "admin" && <Link href="/admin">Admin</Link>}
        </div>
        <div className="navActions">
          {user ? (
            <>
              <span className="tierPill">{user.role === "admin" ? "ADMIN" : user.tier.toUpperCase()}</span>
              <LogoutButton />
            </>
          ) : (
            <>
              <Link className="navButton" href="/login">Log in</Link>
              <Link className="button buttonSmall" href="/register">Start free</Link>
            </>
          )}
        </div>
      </nav>
      <main>{children}</main>
      <footer className="footer">
        <Logo />
        <p>Analytics, not guarantees. Bet responsibly and only where legal.</p>
        <div><Link href="/pricing">Pricing</Link><span>© 2026 EdgeBoard</span></div>
      </footer>
    </>
  );
}
