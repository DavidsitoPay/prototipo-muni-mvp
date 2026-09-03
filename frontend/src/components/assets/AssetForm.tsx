import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import type { Asset } from "../../types";
import {
  ASSET_CRITICALITY_LABELS,
  ASSET_LOCATION_LABELS,
  ASSET_STATUS_LABELS,
  ASSET_TYPE_LABELS,
} from "../../constants/assetLabels";

const schema = z.object({
  name: z.string().min(2, "Requerido"),
  type: z.enum(["servidor", "aplicacion", "base_datos", "red", "endpoint", "sistema_web_publico"]),
  department: z.string().min(2, "Requerido"),
  criticality: z.enum(["baja", "media", "alta", "critica"]),
  status: z.enum(["activo", "mantenimiento", "dado_de_baja"]),
  owner: z.string().min(2, "Requerido"),
  location: z.enum(["fisico", "nube", "on_prem"]),
});

export type AssetFormValues = z.infer<typeof schema>;

export function AssetForm({
  initial,
  onSubmit,
  submitLabel = "Guardar",
}: {
  initial?: Partial<Asset>;
  onSubmit: (values: AssetFormValues) => void;
  submitLabel?: string;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AssetFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? "",
      type: initial?.type ?? "servidor",
      department: initial?.department ?? "",
      criticality: initial?.criticality ?? "media",
      status: initial?.status ?? "activo",
      owner: initial?.owner ?? "",
      location: initial?.location ?? "on_prem",
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div>
        <label className="block text-sm font-medium mb-1">Nombre</label>
        <input
          {...register("name")}
          className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm"
        />
        {errors.name && <p className="text-xs text-risk-critico mt-1">{errors.name.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium mb-1">Tipo</label>
          <select {...register("type")} className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm">
            {Object.entries(ASSET_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Ubicación</label>
          <select {...register("location")} className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm">
            {Object.entries(ASSET_LOCATION_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Dependencia / Dirección responsable</label>
        <input
          {...register("department")}
          className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm"
        />
        {errors.department && <p className="text-xs text-risk-critico mt-1">{errors.department.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Propietario / Responsable</label>
        <input
          {...register("owner")}
          className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm"
        />
        {errors.owner && <p className="text-xs text-risk-critico mt-1">{errors.owner.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium mb-1">Criticidad</label>
          <select {...register("criticality")} className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm">
            {Object.entries(ASSET_CRITICALITY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Estado</label>
          <select {...register("status")} className="w-full rounded-md border border-[var(--color-border)] px-3 py-2 text-sm">
            {Object.entries(ASSET_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-primary hover:bg-primary-dark text-white font-medium rounded-md py-2 text-sm transition-colors disabled:opacity-60"
      >
        {submitLabel}
      </button>
    </form>
  );
}
