import { useState } from "react";
import { AssetFiltersBar } from "../components/assets/AssetFilters";
import { Card } from "../components/common/Card";
import { downloadExecutiveReport, downloadTechnicalReport } from "../api/reports";
import type { AssetFilters } from "../types";

export default function ReportsPage() {
  const [filters, setFilters] = useState<AssetFilters>({});
  const [downloading, setDownloading] = useState<"executive" | "technical" | null>(null);
  const [error, setError] = useState<"executive" | "technical" | null>(null);

  async function handleDownload(kind: "executive" | "technical") {
    setDownloading(kind);
    setError(null);
    try {
      if (kind === "executive") await downloadExecutiveReport(filters);
      else await downloadTechnicalReport(filters);
    } catch {
      setError(kind);
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-primary">Reportes</h1>

      <Card>
        <h2 className="font-semibold mb-2">Filtrar activos incluidos en el reporte</h2>
        <p className="text-xs text-[var(--color-text-muted)] mb-3">
          Opcional — los reportes reflejan los mismos filtros aplicados aquí.
        </p>
        <AssetFiltersBar filters={filters} onChange={setFilters} />
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <h2 className="font-semibold mb-1">Reporte ejecutivo</h2>
          <p className="text-sm text-[var(--color-text-muted)] mb-4">
            Resumen visual (1-2 páginas) con KPIs de riesgo, top 5 activos críticos y % de madurez NIST.
          </p>
          <button
            onClick={() => handleDownload("executive")}
            disabled={downloading !== null}
            className="text-sm px-4 py-2 rounded-md bg-accent text-[#1a1f2b] font-medium hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            {downloading === "executive" ? "Generando..." : "Exportar PDF ejecutivo"}
          </button>
          {error === "executive" && <p className="text-xs text-risk-critico mt-2">No se pudo generar el PDF.</p>}
        </Card>

        <Card>
          <h2 className="font-semibold mb-1">Reporte técnico</h2>
          <p className="text-sm text-[var(--color-text-muted)] mb-4">
            Listado completo de activos, vulnerabilidades y recomendaciones asociadas.
          </p>
          <button
            onClick={() => handleDownload("technical")}
            disabled={downloading !== null}
            className="text-sm px-4 py-2 rounded-md bg-primary text-white font-medium hover:bg-primary-dark transition-colors disabled:opacity-60"
          >
            {downloading === "technical" ? "Generando..." : "Exportar PDF técnico"}
          </button>
          {error === "technical" && <p className="text-xs text-risk-critico mt-2">No se pudo generar el PDF.</p>}
        </Card>
      </div>
    </div>
  );
}
