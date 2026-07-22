import Link from "next/link";
import { Shell } from "@/components/shell";
import { MetricCard } from "@/components/metric-card";
import { PickCard } from "@/components/pick-card";
import { currentUser } from "@/lib/auth";
import { serverApi } from "@/lib/api";
import { localTime, pct, units } from "@/lib/format";
import type { Dashboard } from "@/lib/types";

export const metadata = { title: "Dashboard" };

export default async function DashboardPage() {
  const user = await currentUser();
  const data = await serverApi<Dashboard>("/dashboard/today");
  const paid = user?.role === "admin" || user?.tier === "pro" || user?.tier === "elite";
  return (
    <Shell>
      <section className="dashboardHero"><div><span className="eyebrow">MLB · TODAY'S BOARD</span><h1>Good evening, {user?.display_name.split(" ")[0]}.</h1><p>Last rendered {localTime(data.as_of)}. Prices are limited to FanDuel and DraftKings.</p></div><div className="dashboardStatus"><i /><span>MODEL ONLINE</span><b>{data.tier.toUpperCase()} ACCESS</b></div></section>
      <section className="dashboardBody">
        <div className="metricsGrid compact">
          <MetricCard label="Record" value={`${data.record.wins}–${data.record.losses}–${data.record.pushes}`} note={`${data.record.pending} pending`} />
          <MetricCard label="Units" value={units(data.record.units)} note={`${data.record.units_risked.toFixed(2)}u risked`} tone={data.record.units >= 0 ? "positiveTone" : "negativeTone"} />
          <MetricCard label="ROI" value={pct(data.record.roi)} note="Official plays" />
          <MetricCard label="CLV" value={pct(data.record.average_clv)} note="Average close" />
        </div>

        {!paid && <div className="upgradeBanner"><div><span className="eyebrow">FREE ACCESS</span><h2>One pick is visible. The full card is behind the membership.</h2><p>Unlock complete reasons, every official play, all games, and the performance center.</p></div><Link className="button" href="/pricing">Compare plans</Link></div>}

        <section className="panel"><div className="sectionHead"><div><span className="eyebrow">OFFICIAL CARD</span><h2>Today's tracked plays</h2></div><span>{data.official.length} visible</span></div>
          {data.official.length ? <div className="pickList">{data.official.map((pick) => <PickCard key={pick.id} pick={pick} locked={!paid} />)}</div> : <div className="emptyState"><strong>No official play yet.</strong><span>The model will not force a bet when the price does not clear its thresholds.</span></div>}
        </section>

        {data.watchlist.length > 0 && <section className="panel"><div className="sectionHead"><div><span className="eyebrow">ELITE WATCHLIST</span><h2>Qualified prices below the official cutoff</h2></div></div><div className="pickList">{data.watchlist.map((pick) => <PickCard key={pick.id} pick={pick} />)}</div></section>}

        <section className="panel"><div className="sectionHead"><div><span className="eyebrow">GAME BOARD</span><h2>Every modeled matchup</h2></div><span>{data.games.length} games</span></div><div className="gameGrid">
          {data.games.map((game) => <Link className="gameCard" href={paid ? `/game/${encodeURIComponent(game.id)}` : "/pricing"} key={game.id}><div><span>{localTime(game.commence_time)}</span><b>{game.matchup}</b><small>{game.away_pitcher ?? "TBD"} · {game.home_pitcher ?? "TBD"}</small></div><div className="gameProjection"><span>Projected</span><b>{game.projected_score.away == null ? "—" : `${game.projected_score.away.toFixed(1)}–${game.projected_score.home?.toFixed(1)}`}</b><small>{game.home_win_probability == null ? "Upgrade to unlock" : `${pct(game.home_win_probability)} home`}</small></div></Link>)}
        </div></section>
      </section>
    </Shell>
  );
}
