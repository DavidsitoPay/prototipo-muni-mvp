import type { Asset, AssetDetail, AssetFilters } from "../types";
import { apiClient } from "./client";

export async function fetchAssets(filters: AssetFilters = {}): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>("/assets", { params: filters });
  return data;
}

export async function fetchAssetDetail(assetId: string): Promise<AssetDetail> {
  const { data } = await apiClient.get<AssetDetail>(`/assets/${assetId}`);
  return data;
}

export interface AssetPayload {
  name: string;
  type: Asset["type"];
  department: string;
  criticality: Asset["criticality"];
  status?: Asset["status"];
  owner: string;
  location: Asset["location"];
}

export async function createAsset(payload: AssetPayload): Promise<Asset> {
  const { data } = await apiClient.post<Asset>("/assets", payload);
  return data;
}

export async function updateAsset(assetId: string, payload: Partial<AssetPayload>): Promise<Asset> {
  const { data } = await apiClient.put<Asset>(`/assets/${assetId}`, payload);
  return data;
}

export async function deleteAsset(assetId: string): Promise<void> {
  await apiClient.delete(`/assets/${assetId}`);
}
