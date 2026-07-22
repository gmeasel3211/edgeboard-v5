type Point = { date: string; cumulative_units: number };

export function LineChart({ data }: { data: Point[] }) {
  if (!data.length) return <div className="emptyChart">Settled picks will build your performance curve here.</div>;
  const width = 900;
  const height = 280;
  const values = data.map((item) => item.cumulative_units);
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 0);
  const range = Math.max(max - min, 1);
  const points = data.map((item, index) => {
    const x = data.length === 1 ? width / 2 : (index / (data.length - 1)) * width;
    const y = height - ((item.cumulative_units - min) / range) * (height - 40) - 20;
    return `${x},${y}`;
  }).join(" ");
  const zeroY = height - ((0 - min) / range) * (height - 40) - 20;
  return (
    <div className="chartShell">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Cumulative units chart">
        <line x1="0" x2={width} y1={zeroY} y2={zeroY} className="zeroLine" />
        <polyline points={points} className="chartLine" />
      </svg>
      <div className="chartLabels"><span>{data[0].date}</span><span>{data[data.length - 1].date}</span></div>
    </div>
  );
}
