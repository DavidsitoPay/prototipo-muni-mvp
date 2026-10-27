import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Asset, User } from "../types";

const { fetchAssets, createAsset, updateAsset, deleteAsset } = vi.hoisted(() => ({
  fetchAssets: vi.fn(),
  createAsset: vi.fn(),
  updateAsset: vi.fn(),
  deleteAsset: vi.fn(),
}));

vi.mock("../api/assets", () => ({ fetchAssets, createAsset, updateAsset, deleteAsset }));

const { useAuth } = vi.hoisted(() => ({ useAuth: vi.fn() }));
vi.mock("../auth/AuthContext", () => ({ useAuth }));

import AssetsPage from "./AssetsPage";

const ADMIN: User = { id: "u1", username: "admin", display_name: "Admin", role: "admin_ti" };

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

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AssetsPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("AssetsPage", () => {
  beforeEach(() => {
    fetchAssets.mockReset();
    createAsset.mockReset();
    updateAsset.mockReset();
    deleteAsset.mockReset();
    useAuth.mockReset();
    useAuth.mockReturnValue({ user: ADMIN });
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  it("lists assets and lets an admin edit, delete and create one", async () => {
    fetchAssets.mockResolvedValue([ASSET]);
    deleteAsset.mockResolvedValue(undefined);
    const user = userEvent.setup();

    renderPage();

    expect(await screen.findByText("Servidor principal")).toBeInTheDocument();

    await user.click(screen.getByText("Editar"));
    expect(await screen.findByText(/Editar: Servidor principal/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "×" }));
    expect(screen.queryByText(/Editar: Servidor principal/)).not.toBeInTheDocument();

    await user.click(screen.getByText("+ Nuevo activo"));
    expect(await screen.findByText("Nuevo activo")).toBeInTheDocument();
  });

  it("shows an error state when assets fail to load and hides write actions for read-only roles", async () => {
    useAuth.mockReturnValue({ user: { ...ADMIN, role: "directivo" } });
    fetchAssets.mockRejectedValue(new Error("network down"));

    renderPage();

    expect(await screen.findByText("No se pudieron cargar los activos.")).toBeInTheDocument();
    expect(screen.queryByText("+ Nuevo activo")).not.toBeInTheDocument();
  });

  it("asks for confirmation before deleting an asset", async () => {
    fetchAssets.mockResolvedValue([ASSET]);
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Servidor principal");
    await user.click(screen.getByText("Eliminar"));

    expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining("Servidor principal"));
    await waitFor(() => expect(deleteAsset.mock.calls[0]?.[0]).toBe("a1"));
  });
});
