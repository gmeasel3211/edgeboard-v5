import { Shell } from "@/components/shell";
import { PricingCards } from "@/components/pricing-cards";
import { currentUser } from "@/lib/auth";

export const metadata = { title: "Pricing" };

export default async function PricingPage() {
  const user = await currentUser(true);
  return (
    <Shell>
      <section className="pageHero centered"><span className="eyebrow">MEMBERSHIP</span><h1>A plan for every level of process.</h1><p>Start free. Upgrade when you want the entire daily card and deeper analysis.</p></section>
      <section className="pageSection"><PricingCards authenticated={!!user} /></section>
      <section className="faqSection"><div className="sectionIntro centered"><span className="eyebrow">QUESTIONS</span><h2>Know exactly what you are buying.</h2></div><div className="faqGrid">
        <article><h3>Are profits guaranteed?</h3><p>No. Sports betting involves risk and variance. EdgeBoard provides analytics and a transparent record, not guaranteed outcomes.</p></article>
        <article><h3>Which sportsbooks are supported?</h3><p>The MLB launch model uses FanDuel and DraftKings prices only.</p></article>
        <article><h3>Can I cancel?</h3><p>Yes. Subscribers manage payment methods, invoices, and cancellation through Stripe's customer portal.</p></article>
        <article><h3>Will more sports be added?</h3><p>The platform is designed for future NFL and NBA modules without replacing the account or subscription system.</p></article>
      </div></section>
    </Shell>
  );
}
