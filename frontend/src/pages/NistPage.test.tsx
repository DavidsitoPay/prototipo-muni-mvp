import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { NistAssessmentItem, NistQuestion, NistSummary } from "../types";

const { fetchNistQuestions, fetchNistAssessment, fetchNistSummary, updateNistAssessment } = vi.hoisted(() => ({
  fetchNistQuestions: vi.fn(),
  fetchNistAssessment: vi.fn(),
  fetchNistSummary: vi.fn(),
  updateNistAssessment: vi.fn(),
}));

vi.mock("../api/nist", () => ({
  fetchNistQuestions,
  fetchNistAssessment,
  fetchNistSummary,
  updateNistAssessment,
}));

import NistPage from "./NistPage";

const QUESTIONS: NistQuestion[] = [{ code: "ID-1", function: "identify", text: "¿Hay inventario de activos?" }];

const ASSESSMENT: NistAssessmentItem[] = [
  { question_code: "ID-1", function: "identify", question_text: "¿Hay inventario de activos?", score: 3, evaluated_at: "2026-01-01" },
];

const SUMMARY: NistSummary = {
  global_maturity_percent: 60,
  functions: [{ function: "identify", maturity_percent: 60, answered_count: 1, total_questions: 1 }],
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <NistPage />
    </QueryClientProvider>
  );
}

describe("NistPage", () => {
  beforeEach(() => {
    fetchNistQuestions.mockReset();
    fetchNistAssessment.mockReset();
    fetchNistSummary.mockReset();
    updateNistAssessment.mockReset();
  });

  it("shows the loading state before the questionnaire arrives", () => {
    fetchNistQuestions.mockReturnValue(new Promise(() => {}));
    fetchNistAssessment.mockResolvedValue([]);
    fetchNistSummary.mockResolvedValue({ global_maturity_percent: null, functions: [] });

    renderPage();

    expect(screen.getByText("Cargando cuestionario NIST...")).toBeInTheDocument();
  });

  it("seeds scores from the saved assessment, shows the maturity summary and saves changes", async () => {
    fetchNistQuestions.mockResolvedValue(QUESTIONS);
    fetchNistAssessment.mockResolvedValue(ASSESSMENT);
    fetchNistSummary.mockResolvedValue(SUMMARY);
    updateNistAssessment.mockResolvedValue(ASSESSMENT);
    const user = userEvent.setup();

    renderPage();

    expect(await screen.findByText("60%")).toBeInTheDocument();
    expect(screen.getByText("¿Hay inventario de activos?")).toBeInTheDocument();

    await user.click(screen.getByText("Guardar respuestas"));

    expect(await screen.findByText("Respuestas guardadas.")).toBeInTheDocument();
    expect(updateNistAssessment).toHaveBeenCalledWith([{ question_code: "ID-1", score: 3 }]);
  });

  it("reports a save error without crashing", async () => {
    fetchNistQuestions.mockResolvedValue(QUESTIONS);
    fetchNistAssessment.mockResolvedValue([]);
    fetchNistSummary.mockResolvedValue({ global_maturity_percent: null, functions: [] });
    updateNistAssessment.mockRejectedValue(new Error("network down"));
    const user = userEvent.setup();

    renderPage();

    await screen.findByText("¿Hay inventario de activos?");
    await user.click(screen.getByText("Guardar respuestas"));

    expect(await screen.findByText("No se pudieron guardar las respuestas.")).toBeInTheDocument();
  });
});
