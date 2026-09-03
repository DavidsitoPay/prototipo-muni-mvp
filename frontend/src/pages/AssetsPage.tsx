import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { createAsset, deleteAsset, fetchAssets, updateAsset } from "../api/assets";
import { AssetFiltersBar } from "../components/assets/AssetFilters";
import { AssetForm, type AssetFormValues } from "../components/assets/AssetForm";
import { AssetTable } from "../components/assets/AssetTable";
import { Card } from "../components/common/Card";
import { Modal } from "../components/common/Modal";
import { useAuth } from "../auth/AuthContext";
import { ASSET_WRITE_ROLES, hasAnyRole } from "../auth/roles";
import type { Asset, AssetFilters } from "../types";

export default function AssetsPage() {
  const { user } = useAuth();
  const canEdit = hasAnyRole(user, ASSET_WRITE_ROLES);
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<AssetFilters>({});
  const [modalMode, setModalMode] = useState<"create" | "edit" | null>(null);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

  const assetsQuery = useQuery({ queryKey: ["assets", filters], queryFn: () => fetchAssets(filters) });

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["assets"] });
  }

  const createMutation = useMutation({
    mutationFn: createAsset,
    onSuccess: () => {
      invalidate();
      setModalMode(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: string; values: AssetFormValues }) => updateAsset(id, values),
    onSuccess: () => {
      invalidate();
      setModalMode(null);
      setEditingAsset(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAsset,
    onSuccess: invalidate,
  });

  function handleDelete(asset: Asset) {
    if (window.confirm(`¿Dar de baja el activo "${asset.name}"?`)) {
      deleteMutation.mutate(asset.id);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-primary">Activos</h1>
        {canEdit && (
          <button
            onClick={() => setModalMode("create")}
            className="text-sm px-3 py-1.5 rounded-md bg-primary text-white font-medium hover:bg-primary-dark transition-colors"
          >
            + Nuevo activo
          </button>
        )}
      </div>

      <Card>
        <AssetFiltersBar filters={filters} onChange={setFilters} />
      </Card>

      {deleteMutation.isError && (
        <p className="text-sm text-risk-critico">No se pudo eliminar el activo. Intenta de nuevo.</p>
      )}

      <Card>
        {assetsQuery.isLoading ? (
          <p className="text-sm text-[var(--color-text-muted)]">Cargando activos...</p>
        ) : assetsQuery.isError ? (
          <p className="text-sm text-risk-critico">No se pudieron cargar los activos.</p>
        ) : (
          <AssetTable
            assets={assetsQuery.data ?? []}
            canManage={canEdit}
            onEdit={(asset) => {
              setEditingAsset(asset);
              setModalMode("edit");
            }}
            onDelete={handleDelete}
          />
        )}
      </Card>

      {modalMode === "create" && (
        <Modal title="Nuevo activo" onClose={() => setModalMode(null)}>
          <AssetForm submitLabel="Crear activo" onSubmit={(values) => createMutation.mutate(values)} />
          {createMutation.isError && (
            <p className="text-xs text-risk-critico mt-2">No se pudo crear el activo. Verifica los datos e intenta de nuevo.</p>
          )}
        </Modal>
      )}

      {modalMode === "edit" && editingAsset && (
        <Modal
          title={`Editar: ${editingAsset.name}`}
          onClose={() => {
            setModalMode(null);
            setEditingAsset(null);
          }}
        >
          <AssetForm
            initial={editingAsset}
            submitLabel="Guardar cambios"
            onSubmit={(values) => updateMutation.mutate({ id: editingAsset.id, values })}
          />
          {updateMutation.isError && (
            <p className="text-xs text-risk-critico mt-2">No se pudo guardar el activo. Intenta de nuevo.</p>
          )}
        </Modal>
      )}
    </div>
  );
}
