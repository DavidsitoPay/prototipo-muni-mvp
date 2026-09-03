import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useRef, useState } from "react";
import { fetchNistAssessment, fetchNistQuestions, fetchNistSummary, updateNistAssessment } from "../api/nist";
import { Card } from "../components/common/Card";
import { NistRadarChart } from "../components/charts/NistRadarChart";
import { NIST_FUNCTION_LABELS } from "../constants/nistFunctions";
import type { NistFunctionKey } from "../types";

const FUNCTION_ORDER: NistFunctionKey[] = ["identify", "protect", "detect", "respond", "recover"];

const SCALE_LABELS: Record<number, string> = {
  1: "Inexistente",
  2: "Inicial",
  3: "En desarrollo",
  4: "Gestionado",
  5: "Optimizado",
};

export default function NistPage() {
  const queryClient = useQueryClient();
  const questionsQuery = useQuery({ queryKey: ["nist-questions"], queryFn: fetchNistQuestions });
  const assessmentQuery = useQuery({ queryKey: ["nist-assessment"], queryFn: fetchNistAssessment });
  const summaryQuery = useQuery({ queryKey: ["nist-summary"], queryFn: fetchNistSummary });

  const [scores, setScores] = useState<Record<string, number | null>>({});
  // Solo se siembra el estado local una vez con la primera carga del servidor;
  // un refetch posterior (p.ej. al recuperar el foco de la ventana) no debe
  // pisar respuestas que el usuario ya cambió en pantalla y no ha guardado.
  const seeded = useRef(false);
  if (assessmentQuery.data && !seeded.current) {
    seeded.current = true;
    const initial: Record<string, number | null> = {};
    for (const item of assessmentQuery.data) {
      initial[item.question_code] = item.score;
    }
    setScores(initial);
  }

  const saveMutation = useMutation({
    mutationFn: () => {
      const answers = Object.entries(scores)
        .filter((entry): entry is [string, number] => entry[1] !== null)
        .map(([question_code, score]) => ({ question_code, score }));
      return updateNistAssessment(answers);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nist-assessment"] });
      queryClient.invalidateQueries({ queryKey: ["nist-summary"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-nist-radar"] });
    },
  });

  const questionsByFunction = useMemo(() => {
    const map = new Map<NistFunctionKey, typeof questionsQuery.data>();
    for (const q of questionsQuery.data ?? []) {
      const list = map.get(q.function) ?? [];
      list.push(q);
      map.set(q.function, list);
    }
    return map;
  }, [questionsQuery.data]);

  if (questionsQuery.isLoading) {
    return <p className="text-sm text-[var(--color-text-muted)]">Cargando cuestionario NIST...</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-primary">Evaluación de madurez NIST CSF</h1>
        <div className="text-right">
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="text-sm px-4 py-2 rounded-md bg-primary text-white font-medium hover:bg-primary-dark transition-colors disabled:opacity-60"
          >
            {saveMutation.isPending ? "Guardando..." : "Guardar respuestas"}
          </button>
          {saveMutation.isError && <p className="text-xs text-risk-critico mt-1">No se pudieron guardar las respuestas.</p>}
          {saveMutation.isSuccess && <p className="text-xs text-risk-bajo mt-1">Respuestas guardadas.</p>}
        </div>
      </div>

      {summaryQuery.data && (
        <Card>
          <div className="flex flex-col sm:flex-row gap-6 items-center">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">
                {summaryQuery.data.global_maturity_percent !== null
                  ? `${summaryQuery.data.global_maturity_percent}%`
                  : "N/D"}
              </div>
              <div className="text-xs text-[var(--color-text-muted)]">Madurez global</div>
            </div>
            <div className="flex-1 w-full">
              <NistRadarChart points={summaryQuery.data.functions} />
            </div>
          </div>
        </Card>
      )}

      {FUNCTION_ORDER.map((fn) => (
        <Card key={fn}>
          <h2 className="font-semibold mb-3">{NIST_FUNCTION_LABELS[fn]}</h2>
          <div className="space-y-3">
            {(questionsByFunction.get(fn) ?? []).map((q) => (
              <div key={q.code} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <p className="text-sm flex-1">{q.text}</p>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      title={SCALE_LABELS[n]}
                      onClick={() => setScores((prev) => ({ ...prev, [q.code]: n }))}
                      className={`w-8 h-8 rounded-md text-xs font-semibold border transition-colors ${
                        scores[q.code] === n
                          ? "bg-primary text-white border-primary"
                          : "border-[var(--color-border)] hover:bg-[var(--color-bg)]"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
