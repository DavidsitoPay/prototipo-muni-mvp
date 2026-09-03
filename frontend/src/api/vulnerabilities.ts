import type { RiskBand, Vulnerability, VulnerabilityStatus } from "../types";
import { apiClient } from "./client";

export interface VulnerabilityListFilters {
  risk_band?: RiskBand;
  status_?: VulnerabilityStatus;
}

export async function fetchVulnerabilities(filters: VulnerabilityListFilters = {}): Promise<Vulnerability[]> {
  const { data } = await apiClient.get<Vulnerability[]>("/vulnerabilities", { params: filters });
  return data;
}

export async function fetchAssetVulnerabilities(assetId: string): Promise<Vulnerability[]> {
  const { data } = await apiClient.get<Vulnerability[]>(`/assets/${assetId}/vulnerabilities`);
  return data;
}

export interface VulnerabilityPayload {
  description: string;
  probability: number;
  impact: number;
}

export async function createVulnerability(assetId: string, payload: VulnerabilityPayload): Promise<Vulnerability> {
  const { data } = await apiClient.post<Vulnerability>(`/assets/${assetId}/vulnerabilities`, payload);
  return data;
}

export async function updateVulnerability(
  vulnerabilityId: string,
  payload: Partial<VulnerabilityPayload> & { status?: VulnerabilityStatus }
): Promise<Vulnerability> {
  const { data } = await apiClient.put<Vulnerability>(`/vulnerabilities/${vulnerabilityId}`, payload);
  return data;
}

export async function deleteVulnerability(vulnerabilityId: string): Promise<void> {
  await apiClient.delete(`/vulnerabilities/${vulnerabilityId}`);
}
