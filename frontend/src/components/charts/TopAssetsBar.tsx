import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardSummary } from "../../types";
import { RISK_BAND_COLORS } from "../../constants/riskBands";

export function TopAssetsBar({ data }: { data: DashboardSummary["top_risky_assets"] }) {
  if (data.length === 0) {
    return <div className="text-sm text-[var(--color-text-muted)] py-8 text-center">Sin activos con riesgo registrado.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
        <XAxis type="number" domain={[0, 25]} hide />
        <YAxis
          type="category"
          dataKey="name"
          width={160}
          tick={{ fontSize: 11 }}
          tickFormatter={(value: string) => (value.length > 22 ? `${value.slice(0, 22)}…` : value)}
        />
        <Tooltip />
        <Bar dataKey="risk_score" radius={[0, 4, 4, 0]} isAnimationActive={false}>
          {data.map((entry) => (
            <Cell key={entry.asset_id} fill={RISK_BAND_COLORS[entry.risk_band]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
