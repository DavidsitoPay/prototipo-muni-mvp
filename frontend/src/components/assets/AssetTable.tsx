import { Link } from "react-router-dom";
import type { Asset } from "../../types";
import { ASSET_CRITICALITY_LABELS, ASSET_STATUS_LABELS } from "../../constants/assetLabels";
import { RiskBadge } from "../common/RiskBadge";

export function AssetTable({
  assets,
  canManage,
  onEdit,
  onDelete,
}: {
  assets: Asset[];
  canManage: boolean;
  onEdit: (asset: Asset) => void;
  onDelete: (asset: Asset) => void;
}) {
  if (assets.length === 0) {
    return <p className="text-sm text-[var(--color-text-muted)] py-6 text-center">No hay activos que coincidan con los filtros.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-[var(--color-text-muted)] border-b border-[var(--color-border)]">
            <th className="py-2 pr-3">Nombre</th>
            <th className="py-2 pr-3">Dependencia</th>
            <th className="py-2 pr-3">Criticidad</th>
            <th className="py-2 pr-3">Estado</th>
            <th className="py-2 pr-3">Riesgo</th>
            {canManage && <th className="py-2 pr-3"></th>}
          </tr>
        </thead>
        <tbody>
          {assets.map((asset) => (
            <tr key={asset.id} className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-bg)]">
              <td className="py-2 pr-3">
                <Link to={`/activos/${asset.id}`} className="font-medium text-primary hover:underline">
                  {asset.name}
                </Link>
              </td>
              <td className="py-2 pr-3">{asset.department}</td>
              <td className="py-2 pr-3">{ASSET_CRITICALITY_LABELS[asset.criticality]}</td>
              <td className="py-2 pr-3">{ASSET_STATUS_LABELS[asset.status]}</td>
              <td className="py-2 pr-3">
                <RiskBadge band={asset.risk_band} />
              </td>
              {canManage && (
                <td className="py-2 pr-3 text-right whitespace-nowrap">
                  <button onClick={() => onEdit(asset)} className="text-xs text-primary hover:underline mr-3">
                    Editar
                  </button>
                  <button onClick={() => onDelete(asset)} className="text-xs text-risk-critico hover:underline">
                    Eliminar
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
