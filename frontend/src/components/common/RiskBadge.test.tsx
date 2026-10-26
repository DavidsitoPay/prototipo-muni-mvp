import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it("renders 'Sin riesgo' when band is null", () => {
    render(<RiskBadge band={null} />);
    expect(screen.getByText("Sin riesgo")).toBeInTheDocument();
  });

  it.each([
    ["bajo", "Bajo"],
    ["medio", "Medio"],
    ["alto", "Alto"],
    ["critico", "Crítico"],
  ] as const)("renders the Spanish label for band '%s'", (band, label) => {
    render(<RiskBadge band={band} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("applies a distinct background color per band", () => {
    const { unmount } = render(<RiskBadge band="critico" />);
    const critico = screen.getByText("Crítico");
    const criticoColor = critico.style.backgroundColor;
    unmount();

    render(<RiskBadge band="bajo" />);
    const bajo = screen.getByText("Bajo");
    expect(bajo.style.backgroundColor).not.toBe(criticoColor);
  });
});
