:root {
  --bg: #050914;
  --bg2: #08101e;
  --panel: rgba(13, 24, 42, .88);
  --panel-solid: #0d182a;
  --panel2: #111f35;
  --line: rgba(126, 151, 188, .20);
  --line-strong: rgba(126, 151, 188, .34);
  --text: #f6f9ff;
  --muted: #91a3bd;
  --accent: #59e2b9;
  --accent2: #67a9ff;
  --gold: #f5c967;
  --red: #ff7f8c;
  --shadow: 0 24px 70px rgba(0, 0, 0, .32);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  color: var(--text);
  background:
    radial-gradient(circle at 18% 4%, rgba(49, 115, 176, .20), transparent 28%),
    radial-gradient(circle at 82% 20%, rgba(36, 163, 126, .10), transparent 25%),
    linear-gradient(180deg, #040813 0%, var(--bg) 48%, #030711 100%);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: .035;
  background-image: linear-gradient(rgba(255,255,255,.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.8) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: linear-gradient(to bottom, black, transparent 80%);
}

a { color: inherit; text-decoration: none; }
button, input { font: inherit; }
button { color: inherit; }

.siteNav {
  position: sticky;
  top: 0;
  z-index: 50;
  height: 76px;
  display: flex;
  align-items: center;
  gap: 28px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 0 28px;
  border-bottom: 1px solid var(--line);
  background: rgba(5, 9, 20, .80);
  backdrop-filter: blur(18px);
}
.brand { display: flex; align-items: center; gap: 11px; margin-right: auto; }
.brandMark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: #032117;
  font-size: 1.1rem;
  font-weight: 950;
  background: linear-gradient(145deg, #80f5d1, #28be91);
  box-shadow: 0 8px 30px rgba(55, 211, 164, .23);
}
.brand b { display: block; font-size: .98rem; letter-spacing: -.02em; }
.brand small { display: block; margin-top: 2px; color: var(--muted); font-size: .54rem; letter-spacing: .18em; }
.navLinks, .navActions { display: flex; align-items: center; gap: 8px; }
.navLinks a, .navButton {
  padding: 9px 12px;
  border: 0;
  border-radius: 9px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  font-size: .86rem;
  font-weight: 750;
}
.navLinks a:hover, .navButton:hover { color: var(--text); background: rgba(255,255,255,.05); }
.tierPill {
  padding: 7px 10px;
  border: 1px solid rgba(89, 226, 185, .30);
  border-radius: 999px;
  color: var(--accent);
  font-size: .65rem;
  font-weight: 900;
  letter-spacing: .12em;
}

.button {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 19px;
  border: 1px solid transparent;
  border-radius: 11px;
  color: #042218;
  background: linear-gradient(145deg, #72efc9, #31c596);
  box-shadow: 0 10px 30px rgba(43, 202, 151, .15);
  cursor: pointer;
  font-size: .88rem;
  font-weight: 900;
  transition: transform .18s ease, filter .18s ease, border-color .18s ease;
}
.button:hover { transform: translateY(-1px); filter: brightness(1.05); }
.button:disabled { opacity: .58; cursor: wait; transform: none; }
.buttonSmall { min-height: 38px; padding: 0 14px; font-size: .78rem; }
.buttonGhost { color: var(--text); background: rgba(255,255,255,.035); border-color: var(--line-strong); box-shadow: none; }
.buttonWarn { color: #241a02; background: linear-gradient(145deg, #ffdd88, #e8b94f); }
.textLink { color: var(--accent); font-size: .84rem; font-weight: 800; }

.eyebrow { color: var(--accent); font-size: .68rem; font-weight: 900; letter-spacing: .18em; }
.positive { color: var(--accent) !important; }
.negative { color: var(--red) !important; }

.heroSection {
  position: relative;
  min-height: 720px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 92px 40px 74px;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, .95fr);
  align-items: center;
  gap: 72px;
  overflow: hidden;
}
.heroGlow { position: absolute; width: 560px; height: 560px; left: -210px; top: 30px; border-radius: 50%; background: rgba(61, 127, 203, .10); filter: blur(80px); }
.heroCopy { position: relative; z-index: 1; }
.liveTag { display: inline-flex; align-items: center; gap: 8px; color: #bbcae1; font-size: .69rem; font-weight: 850; letter-spacing: .13em; }
.liveTag i, .dashboardStatus i { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 16px var(--accent); }
.heroCopy h1, .pageHero h1, .authCopy h1, .gameHero h1, .successPage h1 {
  margin: 23px 0 22px;
  font-size: clamp(3.4rem, 6.8vw, 6.8rem);
  line-height: .92;
  letter-spacing: -.075em;
  font-weight: 900;
}
.heroCopy h1 em { color: transparent; background: linear-gradient(90deg, #8ff5d8, #68aaff); -webkit-background-clip: text; background-clip: text; font-style: normal; }
.heroCopy > p { max-width: 680px; color: #aebed3; font-size: 1.13rem; line-height: 1.75; }
.heroActions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 34px; }
.trustRow { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 28px; color: #7f91aa; font-size: .76rem; }

.terminalCard {
  position: relative;
  min-height: 500px;
  padding: 24px;
  border: 1px solid rgba(110, 151, 209, .30);
  border-radius: 24px;
  background: linear-gradient(150deg, rgba(15, 31, 54, .96), rgba(7, 15, 28, .96));
  box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.05);
  overflow: hidden;
}
.terminalCard::before { content: ""; position: absolute; inset: 0; opacity: .09; background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,255,255,.09) 4px); pointer-events: none; }
.terminalTop { position: relative; display: flex; justify-content: space-between; color: #8fa4bf; font-size: .67rem; letter-spacing: .16em; font-weight: 850; }
.terminalTop b { color: var(--accent); }
.terminalMatchup { position: relative; margin-top: 76px; padding: 28px; border: 1px solid var(--line); border-radius: 18px; background: rgba(4, 10, 20, .56); }
.terminalMatchup small { color: var(--accent2); font-size: .66rem; letter-spacing: .14em; font-weight: 900; }
.terminalMatchup strong { display: block; margin: 16px 0 12px; font-size: 2rem; letter-spacing: -.045em; }
.terminalMatchup p { margin: 0; color: var(--muted); line-height: 1.65; }
.terminalStats { position: relative; display: grid; gap: 10px; margin-top: 16px; }
.terminalStats div { display: flex; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid var(--line); }
.terminalStats span { color: var(--muted); font-size: .75rem; }
.terminalStats b { font-size: .78rem; }
.scanLine { position: absolute; left: 0; right: 0; top: 20%; height: 1px; background: linear-gradient(90deg, transparent, rgba(89,226,185,.75), transparent); box-shadow: 0 0 18px rgba(89,226,185,.5); animation: scan 5s linear infinite; }
@keyframes scan { from { transform: translateY(-40px); } to { transform: translateY(430px); } }

.proofSection, .featureSection, .freePickSection, .pageSection, .faqSection, .dashboardBody {
  max-width: 1400px;
  margin: 0 auto;
  padding: 82px 28px;
}
.sectionIntro { max-width: 720px; }
.sectionIntro.centered, .pageHero.centered { margin-left: auto; margin-right: auto; text-align: center; }
.sectionIntro h2, .freePickSection h2, .ctaSection h2, .sectionHead h2, .upgradeBanner h2 {
  margin: 10px 0 12px;
  font-size: clamp(1.9rem, 3.4vw, 3.3rem);
  line-height: 1.05;
  letter-spacing: -.05em;
}
.sectionIntro p, .freePickSection > div > p, .ctaSection p, .pageHero p, .upgradeBanner p { margin: 0; color: var(--muted); line-height: 1.7; }
.metricsGrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 38px; }
.metricsGrid.compact { margin-top: 0; margin-bottom: 20px; }
.metricCard {
  min-height: 150px;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: linear-gradient(150deg, rgba(16,29,49,.90), rgba(9,18,32,.88));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.035);
}
.metricCard span { display: block; color: var(--muted); font-size: .73rem; font-weight: 750; }
.metricCard strong { display: block; margin: 15px 0 9px; font-size: 2.2rem; letter-spacing: -.055em; }
.metricCard small { color: #6f829e; font-size: .72rem; }
.metricCard.positiveTone strong { color: var(--accent); }
.metricCard.negativeTone strong { color: var(--red); }

.featureSection { padding-top: 105px; padding-bottom: 105px; }
.featureGrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 42px; }
.featureGrid article { position: relative; min-height: 240px; padding: 30px; border: 1px solid var(--line); border-radius: 18px; background: rgba(10,20,36,.70); overflow: hidden; }
.featureGrid article::after { content: ""; position: absolute; width: 180px; height: 180px; right: -80px; bottom: -80px; border-radius: 50%; background: rgba(88, 165, 255, .07); }
.featureNumber { color: var(--accent2); font-size: .68rem; letter-spacing: .18em; font-weight: 900; }
.featureGrid h3 { margin: 58px 0 12px; font-size: 1.45rem; letter-spacing: -.035em; }
.featureGrid p { margin: 0; max-width: 520px; color: var(--muted); line-height: 1.7; }

.freePickSection { display: grid; grid-template-columns: .8fr 1.2fr; gap: 58px; align-items: start; }
.ctaSection { max-width: 1140px; margin: 70px auto 120px; padding: 72px 34px; text-align: center; border: 1px solid rgba(89,226,185,.22); border-radius: 28px; background: radial-gradient(circle at top, rgba(58,164,131,.12), transparent 55%), rgba(10,20,35,.72); }
.ctaSection p { max-width: 670px; margin: 0 auto 28px; }

.panel {
  padding: 24px;
  margin-bottom: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--panel);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.035);
}
.sectionHead { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.sectionHead h2 { margin-bottom: 0; font-size: 1.75rem; }
.sectionHead > span { color: var(--muted); font-size: .76rem; }
.pickList { display: grid; gap: 14px; }
.pickCard { padding: 22px; border: 1px solid var(--line); border-radius: 16px; background: linear-gradient(145deg, rgba(13,27,47,.94), rgba(8,16,29,.92)); }
.pickTop { display: grid; grid-template-columns: auto 1fr auto; gap: 16px; align-items: center; }
.pickTop h3 { margin: 7px 0 6px; font-size: 1.45rem; letter-spacing: -.035em; }
.pickTop p { margin: 0; color: var(--muted); font-size: .78rem; }
.grade { width: 48px; height: 48px; display: grid; place-items: center; border-radius: 13px; color: var(--accent); background: rgba(89,226,185,.10); border: 1px solid rgba(89,226,185,.25); font-weight: 950; }
.gradePass { color: var(--muted); background: rgba(255,255,255,.03); border-color: var(--line); }
.price { font-size: 1.5rem; }
.pickGrid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-top: 20px; }
.pickGrid div { padding: 12px; border-radius: 10px; background: rgba(3,9,18,.50); }
.pickGrid span { display: block; color: var(--muted); font-size: .65rem; }
.pickGrid b { display: block; margin-top: 6px; font-size: .92rem; }
.confidenceTrack { height: 4px; margin: 18px 0; border-radius: 999px; background: #132237; overflow: hidden; }
.confidenceTrack i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent2), var(--accent)); }
.reasonList, .deepReasonList { margin: 0 0 16px; padding-left: 18px; color: #a9b9cd; font-size: .79rem; line-height: 1.65; }
.deepReasonList { font-size: .88rem; }
.lockedNote { padding: 13px 15px; border-radius: 10px; color: var(--gold); background: rgba(245,201,103,.08); font-size: .78rem; }
.emptyState, .emptyChart { min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 7px; padding: 24px; text-align: center; border: 1px dashed var(--line-strong); border-radius: 14px; color: var(--muted); }
.emptyState strong { color: var(--text); }

.pageHero, .dashboardHero, .gameHero {
  max-width: 1400px;
  margin: 0 auto;
  padding: 86px 28px 35px;
}
.pageHero h1 { max-width: 980px; margin-top: 15px; font-size: clamp(3rem, 5.3vw, 5.5rem); }
.pageHero p { max-width: 760px; font-size: 1.02rem; }
.pricingGrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.pricingCard { position: relative; min-height: 500px; padding: 28px; display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 20px; background: rgba(10,20,36,.78); }
.pricingCard.featured { border-color: rgba(89,226,185,.42); transform: translateY(-10px); box-shadow: 0 30px 70px rgba(28, 154, 117, .10); }
.popular { position: absolute; top: 18px; right: 18px; padding: 6px 8px; border-radius: 999px; color: #06241a; background: var(--accent); font-size: .58rem; font-weight: 950; letter-spacing: .10em; }
.planPrice { display: flex; align-items: baseline; gap: 7px; margin: 24px 0 14px; }
.planPrice strong { font-size: 3.8rem; letter-spacing: -.07em; }
.planPrice span, .pricingCard p { color: var(--muted); }
.pricingCard p { line-height: 1.65; }
.pricingCard ul { flex: 1; margin: 28px 0; padding: 0; list-style: none; }
.pricingCard li { padding: 10px 0; border-bottom: 1px solid var(--line); color: #b7c5d8; font-size: .84rem; }
.faqGrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 40px; }
.faqGrid article { padding: 25px; border: 1px solid var(--line); border-radius: 16px; background: rgba(10,20,36,.66); }
.faqGrid h3 { margin-top: 0; }
.faqGrid p { color: var(--muted); line-height: 1.65; }

.authPage { min-height: calc(100vh - 76px); max-width: 1180px; margin: 0 auto; padding: 95px 28px; display: grid; grid-template-columns: 1fr 460px; gap: 80px; align-items: center; }
.authCopy h1 { font-size: clamp(3rem, 5vw, 5rem); }
.authCopy p { max-width: 580px; color: var(--muted); line-height: 1.75; }
.authForm { padding: 30px; border: 1px solid var(--line); border-radius: 20px; background: rgba(11,22,39,.88); box-shadow: var(--shadow); }
.authForm label { display: block; margin-bottom: 16px; color: #c1cee0; font-size: .78rem; font-weight: 800; }
.authForm input { width: 100%; height: 48px; margin-top: 7px; padding: 0 13px; border: 1px solid var(--line-strong); border-radius: 10px; outline: none; color: var(--text); background: rgba(3,9,18,.65); }
.authForm input:focus { border-color: var(--accent2); box-shadow: 0 0 0 3px rgba(103,169,255,.10); }
.authForm small { display: block; margin: -4px 0 17px; color: var(--muted); line-height: 1.5; }
.authForm .button { width: 100%; }
.formError, .formSuccess { padding: 11px 12px; border-radius: 9px; font-size: .78rem; }
.formError { color: #ffd2d6; background: rgba(255,127,140,.10); border: 1px solid rgba(255,127,140,.24); }
.formSuccess { color: #c8ffed; background: rgba(89,226,185,.10); border: 1px solid rgba(89,226,185,.24); }
.formSwitch { margin: 17px 0 0; color: var(--muted); text-align: center; font-size: .78rem; }
.formSwitch a { color: var(--accent); }

.dashboardHero { display: flex; justify-content: space-between; align-items: flex-end; gap: 30px; }
.dashboardHero h1 { margin: 10px 0 10px; font-size: clamp(2.4rem, 4vw, 4.5rem); letter-spacing: -.06em; }
.dashboardHero p { margin: 0; color: var(--muted); }
.dashboardStatus { display: flex; align-items: center; gap: 8px; padding: 13px 15px; border: 1px solid var(--line); border-radius: 12px; background: rgba(11,22,39,.75); }
.dashboardStatus span { font-size: .67rem; font-weight: 900; letter-spacing: .12em; }
.dashboardStatus b { margin-left: 8px; padding-left: 12px; border-left: 1px solid var(--line); color: var(--accent); font-size: .67rem; }
.dashboardBody { padding-top: 20px; }
.upgradeBanner { display: flex; align-items: center; justify-content: space-between; gap: 28px; margin-bottom: 18px; padding: 25px; border: 1px solid rgba(245,201,103,.26); border-radius: 17px; background: rgba(245,201,103,.06); }
.upgradeBanner h2 { font-size: 1.4rem; }
.gameGrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.gameCard { display: flex; justify-content: space-between; gap: 24px; padding: 18px; border: 1px solid var(--line); border-radius: 13px; background: rgba(5,12,22,.50); transition: border-color .18s ease, transform .18s ease; }
.gameCard:hover { transform: translateY(-1px); border-color: var(--line-strong); }
.gameCard span, .gameCard small { display: block; color: var(--muted); font-size: .68rem; }
.gameCard b { display: block; margin: 8px 0 7px; }
.gameProjection { min-width: 120px; text-align: right; }
.gameProjection b { font-size: 1.22rem; }

.gameHero { display: flex; justify-content: space-between; align-items: flex-end; gap: 40px; }
.gameHero h1 { font-size: clamp(2.7rem, 5vw, 5.2rem); }
.gameHero h1 em { color: var(--muted); font-style: normal; font-weight: 400; }
.gameHero p { color: var(--muted); }
.scoreProjection { min-width: 280px; padding: 24px; border: 1px solid rgba(103,169,255,.30); border-radius: 18px; text-align: center; background: rgba(11,23,40,.80); }
.scoreProjection span, .scoreProjection small { display: block; color: var(--muted); font-size: .68rem; letter-spacing: .11em; }
.scoreProjection strong { display: block; margin: 15px 0 10px; font-size: 2.3rem; }
.scoreProjection i { color: var(--muted); font-style: normal; }
.intelligenceGrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }
.intelligenceGrid article { padding: 22px; border: 1px solid var(--line); border-radius: 15px; background: rgba(11,22,39,.80); }
.intelligenceGrid span, .intelligenceGrid small { display: block; color: var(--muted); font-size: .70rem; }
.intelligenceGrid strong { display: block; margin: 12px 0 8px; font-size: 1.8rem; }
.splitPanels { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
.dataList { margin: 0; }
.dataList div { display: flex; justify-content: space-between; gap: 20px; padding: 13px 0; border-bottom: 1px solid var(--line); }
.dataList dt { color: var(--muted); }
.dataList dd { margin: 0; text-align: right; font-weight: 700; }

.adminGrid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.operationPanel { grid-column: 1 / -1; }
.actionGrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.operationMessage { max-height: 150px; margin-top: 16px; padding: 13px; overflow: auto; border-radius: 10px; color: #b9cbe0; background: #050b14; font-size: .72rem; white-space: pre-wrap; }
.settingsForm { display: grid; grid-template-columns: repeat(2, 1fr); gap: 13px; }
.settingsForm label { display: grid; gap: 6px; color: var(--muted); font-size: .72rem; text-transform: capitalize; }
.settingsForm input { height: 42px; padding: 0 11px; border: 1px solid var(--line); border-radius: 9px; color: var(--text); background: rgba(3,9,18,.65); }
.settingsForm .button { grid-column: 1 / -1; }
.tableWrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .79rem; }
th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; white-space: nowrap; }
th { color: var(--muted); font-size: .65rem; text-transform: uppercase; letter-spacing: .11em; }
td code { display: block; max-width: 330px; overflow: hidden; text-overflow: ellipsis; color: #9fb0c6; font-size: .68rem; }
.status { padding: 5px 8px; border-radius: 999px; font-size: .62rem; font-weight: 900; text-transform: uppercase; }
.status.success { color: var(--accent); background: rgba(89,226,185,.09); }
.status.failed { color: var(--red); background: rgba(255,127,140,.09); }
.status.running { color: var(--gold); background: rgba(245,201,103,.09); }

.chartShell { padding: 10px 0 0; }
.chartShell svg { width: 100%; min-height: 260px; overflow: visible; }
.chartLine { fill: none; stroke: var(--accent); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; filter: drop-shadow(0 0 8px rgba(89,226,185,.35)); }
.zeroLine { stroke: rgba(255,255,255,.14); stroke-dasharray: 7 7; }
.chartLabels { display: flex; justify-content: space-between; color: var(--muted); font-size: .68rem; }

.successPage { min-height: 70vh; max-width: 760px; margin: 0 auto; padding: 120px 28px; text-align: center; }
.successPage h1 { font-size: clamp(2.8rem, 5vw, 5rem); }
.successPage p { margin: 0 auto 28px; color: var(--muted); line-height: 1.75; }
.successIcon { width: 70px; height: 70px; display: grid; place-items: center; margin: 0 auto 25px; border-radius: 50%; color: #042218; background: var(--accent); font-size: 1.8rem; font-weight: 950; }

.footer { max-width: 1400px; margin: 0 auto; padding: 34px 28px 45px; display: flex; align-items: center; gap: 30px; border-top: 1px solid var(--line); color: var(--muted); }
.footer .brand { margin-right: 0; }
.footer p { flex: 1; margin: 0; text-align: center; font-size: .72rem; }
.footer > div { display: flex; gap: 15px; font-size: .72rem; }

@media (max-width: 1050px) {
  .heroSection { grid-template-columns: 1fr; padding-top: 70px; }
  .terminalCard { max-width: 720px; }
  .freePickSection, .authPage { grid-template-columns: 1fr; }
  .authForm { max-width: 560px; }
  .pricingGrid { grid-template-columns: 1fr; }
  .pricingCard.featured { transform: none; }
  .metricsGrid, .intelligenceGrid { grid-template-columns: repeat(2, 1fr); }
  .pickGrid { grid-template-columns: repeat(3, 1fr); }
  .gameHero { align-items: flex-start; flex-direction: column; }
  .scoreProjection { width: 100%; }
}

@media (max-width: 760px) {
  .siteNav { height: auto; min-height: 68px; padding: 13px 18px; flex-wrap: wrap; }
  .brand { margin-right: auto; }
  .navLinks { order: 3; width: 100%; overflow-x: auto; padding-top: 5px; border-top: 1px solid var(--line); }
  .navActions .tierPill { display: none; }
  .heroSection { min-height: 0; padding: 62px 20px; gap: 45px; }
  .heroCopy h1 { font-size: clamp(3rem, 16vw, 5rem); }
  .terminalCard { min-height: 450px; padding: 18px; }
  .terminalMatchup { margin-top: 58px; padding: 20px; }
  .proofSection, .featureSection, .freePickSection, .pageSection, .faqSection, .dashboardBody { padding-left: 18px; padding-right: 18px; }
  .metricsGrid, .featureGrid, .faqGrid, .gameGrid, .splitPanels, .adminGrid { grid-template-columns: 1fr; }
  .operationPanel { grid-column: auto; }
  .dashboardHero, .pageHero, .gameHero { padding-left: 18px; padding-right: 18px; }
  .dashboardHero { align-items: flex-start; flex-direction: column; }
  .dashboardStatus { width: 100%; }
  .pickTop { grid-template-columns: auto 1fr; }
  .pickTop .price { grid-column: 2; }
  .pickGrid { grid-template-columns: repeat(2, 1fr); }
  .freePickSection { gap: 28px; }
  .upgradeBanner { align-items: flex-start; flex-direction: column; }
  .actionGrid, .settingsForm { grid-template-columns: 1fr; }
  .settingsForm .button { grid-column: auto; }
  .footer { align-items: flex-start; flex-direction: column; }
  .footer p { text-align: left; }
}

.accountGrid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.panelCopy { color: var(--muted); line-height: 1.7; }
.accountActions { margin-top: 24px; }
@media (max-width: 760px) { .accountGrid { grid-template-columns: 1fr; } }

.healthStack{display:grid;gap:20px}.healthGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px}.healthCard{display:flex;align-items:center;justify-content:space-between;gap:12px;text-transform:capitalize}.healthCard strong{font-size:1.15rem}.reasonDetails{margin-top:12px;border-top:1px solid var(--border);padding-top:10px}.reasonDetails summary{cursor:pointer;font-weight:700}.pickMeta{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.pickMeta span{font-size:.78rem;padding:6px 9px;border:1px solid var(--border);border-radius:999px}.status.stale,.status.degraded{background:rgba(245,158,11,.12);color:#f59e0b}
