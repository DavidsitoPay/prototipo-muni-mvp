import type { AssetFilters } from "../types";
import { apiClient } from "./client";

async function downloadPdf(path: string, filters: AssetFilters, filename: string): Promise<void> {
  const response = await apiClient.get(path, { params: filters, responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function downloadExecutiveReport(filters: AssetFilters = {}): Promise<void> {
  return downloadPdf("/reports/executive", filters, "sgcm-reporte-ejecutivo.pdf");
}

export function downloadTechnicalReport(filters: AssetFilters = {}): Promise<void> {
  return downloadPdf("/reports/technical", filters, "sgcm-reporte-tecnico.pdf");
}
