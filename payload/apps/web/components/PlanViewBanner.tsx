"use client";

import { useEffect, useState } from "react";
import { getPlanView, PlanView, setPlanView } from "@/lib/api";

export function PlanViewBanner() {
  const [view, setView] = useState<PlanView>("actual");

  useEffect(() => {
    const sync = () => setView(getPlanView());
    sync();
    window.addEventListener("edgeboard-view-change", sync);
    return () => window.removeEventListener("edgeboard-view-change", sync);
  }, []);

  if (view === "actual") return null;

  return (
    <div style={{
      position: "sticky", top: 0, zIndex: 1000, padding: "10px 16px",
      textAlign: "center", background: "#f5b942", color: "#111", fontWeight: 800
    }}>
      ADMIN PREVIEW: Viewing EdgeBoard as {view.toUpperCase()}
      <button
        onClick={() => { setPlanView("actual"); window.location.reload(); }}
        style={{marginLeft: 16, padding: "5px 10px", cursor: "pointer"}}
      >
        Return to actual admin view
      </button>
    </div>
  );
}
