import type { HeatmapCell } from "../../types";

function colorFor(count: number, max: number): string {
  if (count === 0) return "#f1f3f5";
  const intensity = max === 0 ? 0 : count / max;
  if (intensity > 0.75) return "#dc2626";
  if (intensity > 0.5) return "#f97316";
  if (intensity > 0.25) return "#eab308";
  return "#86efac";
}

export function RiskHeatmap({ cells }: { cells: HeatmapCell[] }) {
  const max = Math.max(1, ...cells.map((c) => c.count));
  const byKey = new Map(cells.map((c) => [`${c.probability}-${c.impact}`, c.count]));

  const impacts = [5, 4, 3, 2, 1];
  const probabilities = [1, 2, 3, 4, 5];

  return (
    <div className="flex gap-2">
      <div className="flex flex-col justify-between text-[10px] text-[var(--color-text-muted)] py-1">
        {impacts.map((i) => (
          <div key={i} className="h-9 flex items-center">
            {i}
          </div>
        ))}
      </div>
      <div>
        <div className="grid grid-cols-5 gap-1">
          {impacts.map((impact) =>
            probabilities.map((probability) => {
              const count = byKey.get(`${probability}-${impact}`) ?? 0;
              return (
                <div
                  key={`${probability}-${impact}`}
                  title={`Probabilidad ${probability} × Impacto ${impact}: ${count}`}
                  className="h-9 w-9 rounded-sm flex items-center justify-center text-xs font-semibold text-[#1a1f2b]"
                  style={{ backgroundColor: colorFor(count, max) }}
                >
                  {count > 0 ? count : ""}
                </div>
              );
            })
          )}
        </div>
        <div className="flex gap-1 mt-1 pl-0">
          {probabilities.map((p) => (
            <div key={p} className="w-9 text-center text-[10px] text-[var(--color-text-muted)]">
              {p}
            </div>
          ))}
        </div>
        <div className="text-[10px] text-[var(--color-text-muted)] mt-1">Probabilidad → · Impacto ↑</div>
      </div>
    </div>
  );
}
