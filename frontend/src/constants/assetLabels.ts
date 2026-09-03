import type { AssetCriticality, AssetLocation, AssetStatus, AssetType } from "../types";

export const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  servidor: "Servidor",
  aplicacion: "Aplicación",
  base_datos: "Base de datos",
  red: "Red",
  endpoint: "Endpoint",
  sistema_web_publico: "Sistema web público",
};

export const ASSET_CRITICALITY_LABELS: Record<AssetCriticality, string> = {
  baja: "Baja",
  media: "Media",
  alta: "Alta",
  critica: "Crítica",
};

export const ASSET_STATUS_LABELS: Record<AssetStatus, string> = {
  activo: "Activo",
  mantenimiento: "En mantenimiento",
  dado_de_baja: "Dado de baja",
};

export const ASSET_LOCATION_LABELS: Record<AssetLocation, string> = {
  fisico: "Físico",
  nube: "Nube",
  on_prem: "On-premise",
};
