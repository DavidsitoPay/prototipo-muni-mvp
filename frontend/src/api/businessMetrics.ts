import type { BusinessMetric } from "../types";
import { apiClient } from "./client";

export async function fetchAssetBusinessMetrics(assetId: string): Promise<BusinessMetric[]> {
  const { data } = await apiClient.get<BusinessMetric[]>(`/assets/${assetId}/business-metrics`);
  return data;
}
