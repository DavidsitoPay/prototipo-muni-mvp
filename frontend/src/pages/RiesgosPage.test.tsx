import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Asset, HeatmapData, Vulnerability } from "../types";

const { fetchVulnerabilities } = vi.hoisted(() => ({ fetchVulnerabilities: vi.fn() }));
vi.mock("../api/vulnerabilities", () => ({ fetchVulnerabilities }));

const { fetchAssets } = vi.hoisted(() => ({ fetchAssets: vi.fn() }));
vi.mock("../api/assets", () => ({ fetchAssets }));

const { fetchHeatmap } = vi.hoisted(() => ({ fetchHeatmap: vi.fn() }));
vi.mock("../api/dashboard", () => ({ fetchHeatmap }));

import RiesgosPage from "./RiesgosPage";

const ASSET: Asset = {
  id: "a1",
  name: "Servidor principal",
  type: "servidor",
  department: "TI",
  criticality: "alta",
  status: "activo",
  owner: "TI",
  location: "on_prem",
  created_at: "2026-01-01",
  risk_band: "alto",
};

const VULN: Vulnerability = {
  id: "v1",
  asset_id: "a1",
  description: "Parche de seguridad pendiente",
  probability: 3,
  impact: 4,
  risk_score: 12,
  risk_band: "alto",
  status: "abierta",
  created_at: "2026-01-01",
};

const HEATMAP: HeatmapData = { cells: [{ probability: 3, impact: 4, count: 1 }] };

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <RiesgosPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("RiesgosPage", () => {
  beforeEach(() => {
    fetchVulnerabilities.mockReset();
    fetchAssets.mockReset();
    fetchHeatmap.mockReset();
  });

  it("lists vulnerabilities with the related asset name and the heatmap", async () => {
    fetchVulnerabilities.mockResolvedValue([VULN]);
    fetchAssets.mockResolvedValue([ASSET]);
    fetchHeatmap.mockResolvedValue(HEATMAP);

    renderPage();

    expect(await screen.findByText("Parche de seguridad pendiente")).toBeInTheDocument();
    expect(screen.getByText("Servidor principal")).toBeInTheDocument();
  });

  it("shows an empty state when there are no matching vulnerabilities", async () => {
    fetchVulnerabilities.mockResolvedValue([]);
    fetchAssets.mockResolvedValue([]);
    fetchHeatmap.mockResolvedValue({ cells: [] });

    renderPage();

    expect(await screen.findByText("No hay vulnerabilidades que coincidan con los filtros.")).toBeInTheDocument();
  });

  it("shows an error state when vulnerabilities fail to load", async () => {
    fetchVulnerabilities.mockRejectedValue(new Error("network down"));
    fetchAssets.mockResolvedValue([]);
    fetchHeatmap.mockResolvedValue({ cells: [] });

    renderPage();

    expect(await screen.findByText("No se pudieron cargar las vulnerabilidades.")).toBeInTheDocument();
  });

  it("filters by risk band and status", async () => {
    fetchVulnerabilities.mockResolvedValue([VULN]);
    fetchAssets.mockResolvedValue([ASSET]);
    fetchHeatmap.mockResolvedValue(HEATMAP);
    const user = userEvent.setup();

    renderPage();
    await screen.findByText("Parche de seguridad pendiente");

    await user.selectOptions(screen.getByLabelText("Nivel de riesgo"), "alto");
    await user.selectOptions(screen.getByLabelText("Estado"), "abierta");

    expect(fetchVulnerabilities).toHaveBeenCalledWith({ risk_band: "alto", status_: "abierta" });
  });
});
