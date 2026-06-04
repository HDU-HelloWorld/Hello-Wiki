import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type StatCardProps = {
  label: string;
  value: string;
  hint?: string;
  icon?: ReactNode;
  tone?: "blue" | "green" | "amber" | "red" | "zinc";
};

const toneClassName = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  green: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  amber: "bg-amber-50 text-amber-700 ring-amber-100",
  red: "bg-red-50 text-red-700 ring-red-100",
  zinc: "bg-zinc-100 text-zinc-700 ring-zinc-200",
};

export function StatCard({
  label,
  value,
  hint,
  icon,
  tone = "blue",
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-white/40 bg-white/90 p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-zinc-500">{label}</p>
        {icon ? (
          <span
            className={cn(
              "flex size-9 items-center justify-center rounded-xl ring-1",
              toneClassName[tone],
            )}
          >
            {icon}
          </span>
        ) : null}
      </div>
      <div className="mt-3 text-2xl font-semibold tracking-tight text-zinc-950">
        {value}
      </div>
      {hint ? <p className="mt-1 text-xs text-zinc-500">{hint}</p> : null}
    </div>
  );
}
