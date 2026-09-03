import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { NistFunctionKey } from "../../types";
import { NIST_FUNCTION_LABELS } from "../../constants/nistFunctions";

export function NistRadarChart({ points }: { points: { function: NistFunctionKey; maturity_percent: number | null }[] }) {
  const data = points.map((p) => ({
    function: NIST_FUNCTION_LABELS[p.function],
    madurez: p.maturity_percent ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data} outerRadius={90}>
        <PolarGrid />
        <PolarAngleAxis dataKey="function" tick={{ fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9 }} tickCount={5} />
        <Radar dataKey="madurez" stroke="#1b4f91" fill="#1b4f91" fillOpacity={0.35} isAnimationActive={false} />
        <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
