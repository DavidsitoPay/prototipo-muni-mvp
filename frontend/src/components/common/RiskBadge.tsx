import type { RiskBand } from "../../types";
import { RISK_BAND_LABELS } from "../../constants/riskBands";

const RISK_CSS_COLORS: Record<RiskBand, string> = {
  bajo: "var(--color-risk-bajo)",
  medio: "var(--color-risk-medio)",
  alto: "var(--color-risk-alto)",
  critico: "var(--color-risk-critico)",
};

export function RiskBadge({ band }: { band: RiskBand | null }) {
  if (!band) {
    return (
      <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-300 text-gray-700">
        Sin riesgo
      </span>
    );
  }
  return (
    <span
      className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold text-white"
      style={{ backgroundColor: RISK_CSS_COLORS[band] }}
    >
      {RISK_BAND_LABELS[band]}
    </span>
  );
}
