import type { DashboardSummary, HeatmapData, NistRadarData } from "../types";
import { apiClient } from "./client";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<DashboardSummary>("/dashboard/summary");
  return data;
}

export async function fetchHeatmap(): Promise<HeatmapData> {
  const { data } = await apiClient.get<HeatmapData>("/dashboard/heatmap");
  return data;
}

export async function fetchNistRadar(): Promise<NistRadarData> {
  const { data } = await apiClient.get<NistRadarData>("/dashboard/nist-radar");
  return data;
}
