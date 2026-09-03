import type { RiskBand } from "../types";

export const RISK_BAND_LABELS: Record<RiskBand, string> = {
  bajo: "Bajo",
  medio: "Medio",
  alto: "Alto",
  critico: "Crítico",
};

// Valores fijos (no via CSS var) porque Recharts necesita colores planos para
// el fill de SVG; RiskBadge usa las variables CSS de theme/tokens.css para el
// mismo mapeo. Si se actualiza la paleta institucional, actualizar ambos.
export const RISK_BAND_COLORS: Record<RiskBand, string> = {
  bajo: "#22c55e",
  medio: "#eab308",
  alto: "#f97316",
  critico: "#dc2626",
};
