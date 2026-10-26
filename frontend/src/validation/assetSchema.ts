import { z } from "zod";

export const assetSchema = z.object({
  name: z.string().min(2, "Requerido"),
  type: z.enum(["servidor", "aplicacion", "base_datos", "red", "endpoint", "sistema_web_publico"]),
  department: z.string().min(2, "Requerido"),
  criticality: z.enum(["baja", "media", "alta", "critica"]),
  status: z.enum(["activo", "mantenimiento", "dado_de_baja"]),
  owner: z.string().min(2, "Requerido"),
  location: z.enum(["fisico", "nube", "on_prem"]),
});

export type AssetFormValues = z.infer<typeof assetSchema>;
