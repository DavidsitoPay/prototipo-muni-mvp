export type UserRole = "admin_ti" | "analista_riesgo" | "directivo";

export interface User {
  id: string;
  username: string;
  role: UserRole;
  display_name: string;
}

export type AssetType =
  | "servidor"
  | "aplicacion"
  | "base_datos"
  | "red"
  | "endpoint"
  | "sistema_web_publico";

export type AssetCriticality = "baja" | "media" | "alta" | "critica";
export type AssetStatus = "activo" | "mantenimiento" | "dado_de_baja";
export type AssetLocation = "fisico" | "nube" | "on_prem";
export type RiskBand = "bajo" | "medio" | "alto" | "critico";
export type VulnerabilityStatus = "abierta" | "mitigada";
export type NistFunctionKey = "identify" | "protect" | "detect" | "respond" | "recover";
export type RecommendationSource = "regla" | "llm";

export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  department: string;
  criticality: AssetCriticality;
  status: AssetStatus;
  owner: string;
  location: AssetLocation;
  created_at: string;
  risk_band: RiskBand | null;
}

export interface BusinessMetric {
  id: string;
  asset_id: string;
  label: string;
  value: number;
  period: string;
  unit: string;
}

export interface Vulnerability {
  id: string;
  asset_id: string;
  description: string;
  probability: number;
  impact: number;
  risk_score: number;
  risk_band: RiskBand;
  status: VulnerabilityStatus;
  created_at: string;
}

export interface AssetDetail extends Asset {
  vulnerabilities: Vulnerability[];
  business_metrics: BusinessMetric[];
}

export interface Recommendation {
  id: string;
  vulnerability_id: string | null;
  nist_function: NistFunctionKey | null;
  source: RecommendationSource;
  text: string;
  created_at: string;
}

export interface NistQuestion {
  code: string;
  function: NistFunctionKey;
  text: string;
}

export interface NistAssessmentItem {
  question_code: string;
  function: NistFunctionKey;
  question_text: string;
  score: number | null;
  evaluated_at: string | null;
}

export interface NistFunctionSummary {
  function: NistFunctionKey;
  maturity_percent: number | null;
  answered_count: number;
  total_questions: number;
}

export interface NistSummary {
  global_maturity_percent: number | null;
  functions: NistFunctionSummary[];
}

export interface DashboardSummary {
  total_assets: number;
  assets_by_criticality: { criticality: AssetCriticality; count: number }[];
  vulnerabilities_by_risk_band: { risk_band: RiskBand; count: number }[];
  nist_global_maturity_percent: number | null;
  top_risky_assets: {
    asset_id: string;
    name: string;
    criticality: AssetCriticality;
    risk_band: RiskBand;
    risk_score: number;
  }[];
}

export interface HeatmapCell {
  probability: number;
  impact: number;
  count: number;
}

export interface HeatmapData {
  cells: HeatmapCell[];
}

export interface NistRadarPoint {
  function: NistFunctionKey;
  maturity_percent: number | null;
}

export interface NistRadarData {
  points: NistRadarPoint[];
}

export interface AssetFilters {
  type?: AssetType;
  criticality?: AssetCriticality;
  department?: string;
  status_?: AssetStatus;
  q?: string;
}
