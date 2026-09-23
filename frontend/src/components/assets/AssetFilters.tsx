import type { AssetFilters as Filters } from "../../types";
import { ASSET_CRITICALITY_LABELS, ASSET_TYPE_LABELS } from "../../constants/assetLabels";

export function AssetFiltersBar({
  filters,
  onChange,
}: {
  filters: Filters;
  onChange: (filters: Filters) => void;
}) {
  return (
    <div className="flex flex-wrap gap-3 items-end">
      <div>
        <label htmlFor="asset-filter-q" className="block text-xs font-medium mb-1">
          Buscar por nombre
        </label>
        <input
          id="asset-filter-q"
          value={filters.q ?? ""}
          onChange={(e) => onChange({ ...filters, q: e.target.value || undefined })}
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm"
          placeholder="Nombre del activo..."
        />
      </div>
      <div>
        <label htmlFor="asset-filter-type" className="block text-xs font-medium mb-1">
          Tipo
        </label>
        <select
          id="asset-filter-type"
          value={filters.type ?? ""}
          onChange={(e) => onChange({ ...filters, type: (e.target.value || undefined) as Filters["type"] })}
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm"
        >
          <option value="">Todos</option>
          {Object.entries(ASSET_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="asset-filter-criticality" className="block text-xs font-medium mb-1">
          Criticidad
        </label>
        <select
          id="asset-filter-criticality"
          value={filters.criticality ?? ""}
          onChange={(e) =>
            onChange({ ...filters, criticality: (e.target.value || undefined) as Filters["criticality"] })
          }
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm"
        >
          <option value="">Todas</option>
          {Object.entries(ASSET_CRITICALITY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      {(filters.q || filters.type || filters.criticality || filters.department) && (
        <button
          onClick={() => onChange({})}
          className="text-sm px-3 py-1.5 rounded-md border border-[var(--color-border)] hover:bg-[var(--color-bg)]"
        >
          Limpiar filtros
        </button>
      )}
    </div>
  );
}
