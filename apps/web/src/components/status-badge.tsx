import { cn } from "@/lib/utils";

type StatusTone = "green" | "amber" | "red" | "blue" | "zinc" | "purple";

const toneClassName: Record<StatusTone, string> = {
  green: "border-emerald-200 bg-emerald-50 text-emerald-700",
  amber: "border-amber-200 bg-amber-50 text-amber-700",
  red: "border-red-200 bg-red-50 text-red-700",
  blue: "border-blue-200 bg-blue-50 text-blue-700",
  zinc: "border-zinc-200 bg-zinc-50 text-zinc-600",
  purple: "border-violet-200 bg-violet-50 text-violet-700",
};

const statusTone: Record<string, StatusTone> = {
  compiled: "green",
  completed: "green",
  approved: "green",
  online: "green",
  answered: "green",
  compiling: "blue",
  running: "blue",
  pending: "amber",
  partial: "amber",
  reviewing: "amber",
  waiting: "amber",
  failed: "red",
  unknown: "red",
  rejected: "red",
  draft: "zinc",
  offline: "zinc",
  conflict: "purple",
};

type StatusBadgeProps = {
  status: string;
  label?: string;
  className?: string;
};

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const tone = statusTone[status] ?? "zinc";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        toneClassName[tone],
        className,
      )}
    >
      {label ?? status}
    </span>
  );
}
