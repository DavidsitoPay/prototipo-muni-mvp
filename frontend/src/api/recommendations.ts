import type { NistFunctionKey, Recommendation } from "../types";
import { apiClient } from "./client";

export async function fetchVulnerabilityRecommendations(vulnerabilityId: string): Promise<Recommendation[]> {
  const { data } = await apiClient.get<Recommendation[]>(`/vulnerabilities/${vulnerabilityId}/recommendations`);
  return data;
}

export async function fetchNistFunctionRecommendations(nistFunction: NistFunctionKey): Promise<Recommendation[]> {
  const { data } = await apiClient.get<Recommendation[]>(`/nist/${nistFunction}/recommendations`);
  return data;
}
