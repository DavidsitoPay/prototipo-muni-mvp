import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-white border border-[var(--color-border)] rounded-lg shadow-sm p-4 ${className}`}>
      {children}
    </div>
  );
}

export function KpiCard({ label, value, accent }: { label: string; value: ReactNode; accent?: string }) {
  return (
    <Card className="flex-1 min-w-[160px]">
      <div className="text-2xl font-bold" style={accent ? { color: accent } : { color: "var(--color-primary)" }}>
        {value}
      </div>
      <div className="text-xs text-[var(--color-text-muted)] mt-1">{label}</div>
    </Card>
  );
}
