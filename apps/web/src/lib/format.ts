export const pct = (value: number | null | undefined, digits = 1) =>
  value == null ? "—" : `${(value * 100).toFixed(digits)}%`;

export const odds = (value: number | null | undefined) =>
  value == null ? "—" : value > 0 ? `+${value}` : `${value}`;

export const units = (value: number | null | undefined) =>
  value == null ? "—" : `${value >= 0 ? "+" : ""}${value.toFixed(2)}u`;

export const localTime = (value: string) =>
  new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  }).format(new Date(value));

export const marketName = (market: string) =>
  ({ h2h: "Moneyline", spreads: "Run line", totals: "Total" }[market] ?? market);
