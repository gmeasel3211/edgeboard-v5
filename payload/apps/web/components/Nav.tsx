"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API_URL, authHeaders } from "@/lib/api";

export function Nav() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("edgeboard_token");
    if (!token) return;
    fetch(`${API_URL}/api/v1/auth/me`, { headers: authHeaders() })
      .then(async response => response.ok ? response.json() : null)
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  function logout() {
    localStorage.removeItem("edgeboard_token");
    localStorage.removeItem("edgeboard_view_as");
    window.location.href = "/";
  }

  return (
    <nav className="nav">
      <div className="container nav-inner">
        <Link href="/" className="brand">Edge<span>Board</span></Link>
        <div className="nav-links">
          <Link href="/dashboard">Card</Link>
          <Link href="/games">Games</Link>
          <Link href="/live-odds">Live Odds</Link>
          {user?.is_admin && <Link href="/admin">Admin</Link>}
          <Link href="/pricing">Pricing</Link>
          {user ? (
            <button className="button" onClick={logout}>Log out</button>
          ) : (
            <Link href="/login" className="button">Log in</Link>
          )}
        </div>
      </div>
    </nav>
  );
}
