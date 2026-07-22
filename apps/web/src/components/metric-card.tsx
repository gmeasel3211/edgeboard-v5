export function MetricCard({ label, value, note, tone = "" }: { label: string; value: string; note: string; tone?: string }) {
  return (
    <article className={`metricCard ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}
