import Link from "next/link";
import { Shell } from "@/components/shell";
import { MetricCard } from "@/components/metric-card";
import { PickCard } from "@/components/pick-card";
import { serverApi } from "@/lib/api";
import { pct, units } from "@/lib/format";
import type { Pick, RecordSummary } from "@/lib/types";

async function publicData() {
  try {
    const [record, free] = await Promise.all([
      serverApi<RecordSummary>("/public/record"),
      serverApi<{ pick: Pick | null }>("/public/free-pick")
    ]);
    return { record, pick: free.pick };
  } catch {
    return {
      record: { wins: 0, losses: 0, pushes: 0, pending: 0, units: 0, units_risked: 0, roi: 0, win_rate: 0, average_clv: null, total_official: 0 },
      pick: null
    };
  }
}

export default async function Home() {
  const { record, pick } = await publicData();
  return (
    <Shell>
      <section className="heroSection">
        <div className="heroGlow" />
        <div className="heroCopy">
          <span className="liveTag"><i /> MLB MODEL · FANDUEL + DRAFTKINGS</span>
          <h1>See the edge.<br /><em>Know the risk.</em></h1>
          <p>EdgeBoard turns prices, pitching, form, weather, park effects, and market information into a transparent daily betting card—then tracks every official play.</p>
          <div className="heroActions">
            <Link className="button" href="/register">Start with a free account</Link>
            <Link className="button buttonGhost" href="/pricing">View membership</Link>
          </div>
          <div className="trustRow"><span>✓ No hidden record resets</span><span>✓ Official picks frozen</span><span>✓ CLV and ROI tracked</span></div>
        </div>
        <div className="terminalCard">
          <div className="terminalTop"><span>EDGEBOARD MODEL TERMINAL</span><b>LIVE</b></div>
          <div className="terminalMatchup"><small>TONIGHT · 7:05 PM ET</small><strong>Market-aware projections</strong><p>Every recommendation is measured against the actual price—not a vague prediction.</p></div>
          <div className="terminalStats"><div><span>Inputs</span><b>Pitching · Form · Park</b></div><div><span>Markets</span><b>ML · RL · Totals</b></div><div><span>Tracking</span><b>ROI · Units · CLV</b></div></div>
          <div className="scanLine" />
        </div>
      </section>

      <section className="proofSection">
        <div className="sectionIntro"><span className="eyebrow">VERIFIED PERFORMANCE</span><h2>The record is part of the product.</h2><p>Official picks are stored at the recommended sportsbook and price, graded after final scores, and never silently removed.</p></div>
        <div className="metricsGrid">
          <MetricCard label="Official record" value={`${record.wins}–${record.losses}–${record.pushes}`} note={`${record.pending} pending`} />
          <MetricCard label="Net units" value={units(record.units)} note={`${record.units_risked.toFixed(2)}u risked`} tone={record.units >= 0 ? "positiveTone" : "negativeTone"} />
          <MetricCard label="ROI" value={pct(record.roi)} note="Official picks only" />
          <MetricCard label="Average CLV" value={pct(record.average_clv)} note="Closing implied probability" />
        </div>
      </section>

      <section className="featureSection">
        <div className="sectionIntro centered"><span className="eyebrow">ONE OPERATING SYSTEM</span><h2>Everything a disciplined bettor needs.</h2></div>
        <div className="featureGrid">
          <article><span className="featureNumber">01</span><h3>Daily official card</h3><p>Ranked bets with price, fair line, edge, EV, confidence, stake, and the reasons behind the projection.</p></article>
          <article><span className="featureNumber">02</span><h3>Game intelligence</h3><p>Projected score, starting pitchers, recent form, park, weather, market anchor, data quality, and model disagreement.</p></article>
          <article><span className="featureNumber">03</span><h3>Performance center</h3><p>Units, ROI, CLV, market splits, grade splits, and a permanent history of every official recommendation.</p></article>
          <article><span className="featureNumber">04</span><h3>Built to expand</h3><p>The platform is structured for NFL and NBA modules, alerts, mobile apps, and additional licensed data feeds.</p></article>
        </div>
      </section>

      <section className="freePickSection">
        <div><span className="eyebrow">TODAY'S FEATURED PLAY</span><h2>Evaluate the work before you subscribe.</h2><p>Free members receive one featured official pick. Paid members unlock the full card and game intelligence.</p></div>
        {pick ? <PickCard pick={pick} locked /> : <div className="emptyState"><strong>Today's card is still forming.</strong><span>Prices and starting-pitcher information are refreshed automatically.</span></div>}
      </section>

      <section className="ctaSection"><span className="eyebrow">DISCIPLINE OVER HYPE</span><h2>Build your process around transparent numbers.</h2><p>No guarantees. No anonymous “locks.” Just a model, a price, a recorded decision, and the result.</p><Link className="button" href="/register">Create your account</Link></section>
    </Shell>
  );
}
