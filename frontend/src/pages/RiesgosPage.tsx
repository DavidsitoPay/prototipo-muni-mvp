import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchAssets } from "../api/assets";
import { fetchHeatmap } from "../api/dashboard";
import { fetchVulnerabilities, type VulnerabilityListFilters } from "../api/vulnerabilities";
import { Card } from "../components/common/Card";
import { RiskBadge } from "../components/common/RiskBadge";
import { RiskHeatmap } from "../components/charts/RiskHeatmap";
import { RISK_BAND_LABELS } from "../constants/riskBands";
import type { RiskBand, VulnerabilityStatus } from "../types";

const BAND_OPTIONS: RiskBand[] = ["bajo", "medio", "alto", "critico"];

export default function RiesgosPage() {
  const [filters, setFilters] = useState<VulnerabilityListFilters>({});

  const vulnsQuery = useQuery({
    queryKey: ["vulnerabilities", filters],
    queryFn: () => fetchVulnerabilities(filters),
  });
  const assetsQuery = useQuery({ queryKey: ["assets", {}], queryFn: () => fetchAssets() });
  const heatmapQuery = useQuery({ queryKey: ["dashboard-heatmap"], queryFn: fetchHeatmap });

  const assetNameById = useMemo(
    () => new Map((assetsQuery.data ?? []).map((a) => [a.id, a.name])),
    [assetsQuery.data]
  );

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-primary">Riesgos</h1>

      <Card>
        <h2 className="font-semibold mb-2">Matriz de calor (probabilidad × impacto)</h2>
        {heatmapQuery.data ? <RiskHeatmap cells={heatmapQuery.data.cells} /> : <p className="text-sm text-[var(--color-text-muted)]">Cargando...</p>}
      </Card>

      <Card>
        <div className="flex flex-wrap gap-3 items-end mb-4">
          <div>
            <label htmlFor="riesgos-filter-band" className="block text-xs font-medium mb-1">
              Nivel de riesgo
            </label>
            <select
              id="riesgos-filter-band"
              value={filters.risk_band ?? ""}
              onChange={(e) => setFilters({ ...filters, risk_band: (e.target.value || undefined) as RiskBand })}
              className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm"
            >
              <option value="">Todos</option>
              {BAND_OPTIONS.map((b) => (
                <option key={b} value={b}>
                  {RISK_BAND_LABELS[b]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="riesgos-filter-status" className="block text-xs font-medium mb-1">
              Estado
            </label>
            <select
              id="riesgos-filter-status"
              value={filters.status_ ?? ""}
              onChange={(e) =>
                setFilters({ ...filters, status_: (e.target.value || undefined) as VulnerabilityStatus })
              }
              className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm"
            >
              <option value="">Todos</option>
              <option value="abierta">Abierta</option>
              <option value="mitigada">Mitigada</option>
            </select>
          </div>
        </div>

        {vulnsQuery.isLoading ? (
          <p className="text-sm text-[var(--color-text-muted)]">Cargando vulnerabilidades...</p>
        ) : vulnsQuery.isError ? (
          <p className="text-sm text-risk-critico">No se pudieron cargar las vulnerabilidades.</p>
        ) : (vulnsQuery.data ?? []).length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">No hay vulnerabilidades que coincidan con los filtros.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-[var(--color-text-muted)] border-b border-[var(--color-border)]">
                  <th className="py-2 pr-3">Descripción</th>
                  <th className="py-2 pr-3">Activo</th>
                  <th className="py-2 pr-3">Riesgo</th>
                  <th className="py-2 pr-3">Estado</th>
                </tr>
              </thead>
              <tbody>
                {(vulnsQuery.data ?? []).map((v) => (
                  <tr key={v.id} className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-bg)]">
                    <td className="py-2 pr-3 max-w-md">{v.description}</td>
                    <td className="py-2 pr-3">
                      <Link to={`/activos/${v.asset_id}`} className="text-primary hover:underline">
                        {assetNameById.get(v.asset_id) ?? "Ver activo"}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <RiskBadge band={v.risk_band} /> <span className="text-xs text-[var(--color-text-muted)]">({v.risk_score})</span>
                    </td>
                    <td className="py-2 pr-3">{v.status === "mitigada" ? "Mitigada" : "Abierta"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
