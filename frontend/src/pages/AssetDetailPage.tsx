import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { MANAGE_ROLES, hasAnyRole } from "../auth/roles";
import { fetchAssetDetail } from "../api/assets";
import { createVulnerability, deleteVulnerability, updateVulnerability } from "../api/vulnerabilities";
import { Card } from "../components/common/Card";
import { RiskBadge } from "../components/common/RiskBadge";
import {
  ASSET_CRITICALITY_LABELS,
  ASSET_LOCATION_LABELS,
  ASSET_STATUS_LABELS,
} from "../constants/assetLabels";
import { VulnerabilityForm, type VulnerabilityFormValues } from "../components/vulnerabilities/VulnerabilityForm";
import { VulnerabilityTable } from "../components/vulnerabilities/VulnerabilityTable";
import type { Vulnerability } from "../types";

export default function AssetDetailPage() {
  const { assetId } = useParams<{ assetId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const canManageVulns = hasAnyRole(user, MANAGE_ROLES);
  const queryClient = useQueryClient();

  const detailQuery = useQuery({
    queryKey: ["asset-detail", assetId],
    queryFn: () => fetchAssetDetail(assetId!),
    enabled: !!assetId,
  });

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["asset-detail", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-heatmap"] });
  }

  const createMutation = useMutation({
    mutationFn: (values: VulnerabilityFormValues) => createVulnerability(assetId!, values),
    onSuccess: invalidate,
  });

  const toggleStatusMutation = useMutation({
    mutationFn: (v: Vulnerability) =>
      updateVulnerability(v.id, { status: v.status === "mitigada" ? "abierta" : "mitigada" }),
    onSuccess: invalidate,
  });

  const deleteMutation = useMutation({
    mutationFn: (v: Vulnerability) => deleteVulnerability(v.id),
    onSuccess: invalidate,
  });

  if (detailQuery.isLoading) {
    return <p className="text-sm text-[var(--color-text-muted)]">Cargando activo...</p>;
  }

  if (detailQuery.isError || !detailQuery.data) {
    return <p className="text-sm text-risk-critico">No se pudo cargar el activo.</p>;
  }

  const asset = detailQuery.data;

  return (
    <div className="space-y-4">
      <button onClick={() => navigate("/activos")} className="text-sm text-primary hover:underline">
        ← Volver a activos
      </button>

      <Card>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-primary">{asset.name}</h1>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              {asset.department} · {ASSET_LOCATION_LABELS[asset.location]}
            </p>
          </div>
          <RiskBadge band={asset.risk_band} />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-sm">
          <div>
            <div className="text-xs text-[var(--color-text-muted)]">Criticidad</div>
            <div>{ASSET_CRITICALITY_LABELS[asset.criticality]}</div>
          </div>
          <div>
            <div className="text-xs text-[var(--color-text-muted)]">Estado</div>
            <div>{ASSET_STATUS_LABELS[asset.status]}</div>
          </div>
          <div>
            <div className="text-xs text-[var(--color-text-muted)]">Propietario</div>
            <div>{asset.owner}</div>
          </div>
          <div>
            <div className="text-xs text-[var(--color-text-muted)]">Registrado</div>
            <div>{new Date(asset.created_at).toLocaleDateString("es-GT")}</div>
          </div>
        </div>
      </Card>

      {asset.business_metrics.length > 0 && (
        <Card>
          <h2 className="font-semibold mb-3">Métricas de negocio (dato simulado)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {asset.business_metrics.map((m) => (
              <div key={m.id}>
                <div className="text-lg font-bold text-primary">
                  {m.unit === "Q" ? `Q${m.value.toLocaleString("es-GT")}` : m.value.toLocaleString("es-GT")}
                </div>
                <div className="text-xs text-[var(--color-text-muted)]">{m.label}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card>
        <h2 className="font-semibold mb-3">Vulnerabilidades</h2>
        {(toggleStatusMutation.isError || deleteMutation.isError) && (
          <p className="text-xs text-risk-critico mb-2">No se pudo completar la acción. Intenta de nuevo.</p>
        )}
        <VulnerabilityTable
          vulnerabilities={asset.vulnerabilities}
          canManage={canManageVulns}
          onToggleStatus={(v) => toggleStatusMutation.mutate(v)}
          onDelete={(v) => {
            if (window.confirm("¿Eliminar esta vulnerabilidad?")) deleteMutation.mutate(v);
          }}
        />
      </Card>

      {canManageVulns && (
        <Card>
          <h2 className="font-semibold mb-3">Registrar nueva vulnerabilidad</h2>
          <VulnerabilityForm onSubmit={(values) => createMutation.mutate(values)} />
          {createMutation.isError && (
            <p className="text-xs text-risk-critico mt-2">No se pudo registrar la vulnerabilidad. Intenta de nuevo.</p>
          )}
        </Card>
      )}
    </div>
  );
}
