import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchAssets } from "../api/assets";
import { fetchAssetBusinessMetrics } from "../api/businessMetrics";
import { fetchDashboardSummary, fetchHeatmap, fetchNistRadar } from "../api/dashboard";
import { downloadExecutiveReport } from "../api/reports";
import { Card, KpiCard } from "../components/common/Card";
import { RiskBadge } from "../components/common/RiskBadge";
import { NistRadarChart } from "../components/charts/NistRadarChart";
import { RiskDonut } from "../components/charts/RiskDonut";
import { RiskHeatmap } from "../components/charts/RiskHeatmap";
import { TopAssetsBar } from "../components/charts/TopAssetsBar";

const MULTAS_ASSET_NAME = "Sistema de Remisiones/Multas";

function formatCurrency(value: number, unit: string): string {
  if (unit === "Q") {
    return `Q${value.toLocaleString("es-GT", { maximumFractionDigits: 0 })}`;
  }
  return value.toLocaleString("es-GT");
}

export default function DashboardPage() {
  const [exportError, setExportError] = useState(false);
  const summaryQuery = useQuery({ queryKey: ["dashboard-summary"], queryFn: fetchDashboardSummary });
  const heatmapQuery = useQuery({ queryKey: ["dashboard-heatmap"], queryFn: fetchHeatmap });
  const radarQuery = useQuery({ queryKey: ["dashboard-nist-radar"], queryFn: fetchNistRadar });
  const assetsQuery = useQuery({ queryKey: ["assets", {}], queryFn: () => fetchAssets() });

  const multasAsset = assetsQuery.data?.find((a) => a.name === MULTAS_ASSET_NAME);
  const metricsQuery = useQuery({
    queryKey: ["business-metrics", multasAsset?.id],
    queryFn: () => fetchAssetBusinessMetrics(multasAsset!.id),
    enabled: !!multasAsset,
  });

  if (summaryQuery.isLoading) {
    return <p className="text-sm text-[var(--color-text-muted)]">Cargando dashboard...</p>;
  }

  if (summaryQuery.isError || !summaryQuery.data) {
    return <p className="text-sm text-risk-critico">No se pudo cargar el dashboard.</p>;
  }

  const summary = summaryQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-primary">Panel de Riesgo de Ciberseguridad</h1>
        <div className="text-right">
          <button
            onClick={() => {
              setExportError(false);
              downloadExecutiveReport().catch(() => setExportError(true));
            }}
            className="text-sm px-3 py-1.5 rounded-md bg-accent text-[#1a1f2b] font-medium hover:opacity-90 transition-opacity"
          >
            Exportar PDF ejecutivo
          </button>
          {exportError && <p className="text-xs text-risk-critico mt-1">No se pudo generar el PDF.</p>}
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        <KpiCard label="Activos registrados" value={summary.total_assets} />
        <KpiCard
          label="Vulnerabilidades alto/crítico"
          value={
            (summary.vulnerabilities_by_risk_band.find((b) => b.risk_band === "alto")?.count ?? 0) +
            (summary.vulnerabilities_by_risk_band.find((b) => b.risk_band === "critico")?.count ?? 0)
          }
          accent="var(--color-risk-critico)"
        />
        <KpiCard
          label="Madurez NIST global"
          value={summary.nist_global_maturity_percent !== null ? `${summary.nist_global_maturity_percent}%` : "N/D"}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <h2 className="font-semibold mb-2">Vulnerabilidades por nivel de riesgo</h2>
          <RiskDonut data={summary.vulnerabilities_by_risk_band} />
        </Card>

        <Card>
          <h2 className="font-semibold mb-2">Matriz de calor (probabilidad × impacto)</h2>
          {heatmapQuery.data ? (
            <RiskHeatmap cells={heatmapQuery.data.cells} />
          ) : (
            <p className="text-sm text-[var(--color-text-muted)]">Cargando...</p>
          )}
        </Card>

        <Card>
          <h2 className="font-semibold mb-2">Madurez NIST CSF por función</h2>
          {radarQuery.data ? (
            <NistRadarChart points={radarQuery.data.points} />
          ) : (
            <p className="text-sm text-[var(--color-text-muted)]">Cargando...</p>
          )}
        </Card>

        <Card>
          <h2 className="font-semibold mb-2">Top 5 activos con mayor riesgo</h2>
          <TopAssetsBar data={summary.top_risky_assets} />
        </Card>
      </div>

      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Sistema de Remisiones/Multas — indicadores del mes</h2>
          {multasAsset && <RiskBadge band={multasAsset.risk_band} />}
        </div>
        <p className="text-xs text-[var(--color-text-muted)] mb-3">
          Datos simulados de negocio para ilustrar el impacto real si este activo crítico falla o es vulnerado.
        </p>
        {metricsQuery.data && metricsQuery.data.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {metricsQuery.data.map((m) => (
              <div key={m.id}>
                <div className="text-xl font-bold text-primary">{formatCurrency(m.value, m.unit)}</div>
                <div className="text-xs text-[var(--color-text-muted)]">{m.label}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--color-text-muted)]">Sin métricas disponibles.</p>
        )}
      </Card>
    </div>
  );
}
