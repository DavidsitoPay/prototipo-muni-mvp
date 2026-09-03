import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { RiskBand } from "../../types";
import { RISK_BAND_COLORS, RISK_BAND_LABELS } from "../../constants/riskBands";

export function RiskDonut({ data }: { data: { risk_band: RiskBand; count: number }[] }) {
  const chartData = data.map((d) => ({ name: RISK_BAND_LABELS[d.risk_band], value: d.count, band: d.risk_band }));
  const total = chartData.reduce((sum, d) => sum + d.value, 0);

  if (total === 0) {
    return <div className="text-sm text-[var(--color-text-muted)] py-8 text-center">Sin vulnerabilidades registradas.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          innerRadius={50}
          outerRadius={80}
          paddingAngle={2}
          isAnimationActive={false}
        >
          {chartData.map((entry) => (
            <Cell key={entry.band} fill={RISK_BAND_COLORS[entry.band]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
