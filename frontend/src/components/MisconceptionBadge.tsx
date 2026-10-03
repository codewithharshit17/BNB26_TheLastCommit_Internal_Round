import type { MisconceptionState } from "@/lib/types";

interface MisconceptionBadgeProps {
  state: MisconceptionState | string;
  size?: "sm" | "md";
}

export default function MisconceptionBadge({ state, size = "md" }: MisconceptionBadgeProps) {
  const configs: Record<
    string,
    { label: string; dotColor: string; bg: string; border: string; text: string }
  > = {
    active: {
      label: "Active Misconception",
      dotColor: "#f59e0b",
      bg: "bg-[#f59e0b]/10",
      border: "border-[#f59e0b]/30",
      text: "text-[#f59e0b]",
    },
    intervened: {
      label: "Intervened",
      dotColor: "#3b82f6",
      bg: "bg-[#3b82f6]/10",
      border: "border-[#3b82f6]/30",
      text: "text-[#3b82f6]",
    },
    suspected_resolved: {
      label: "Suspected Resolved",
      dotColor: "#a855f7",
      bg: "bg-[#a855f7]/10",
      border: "border-[#a855f7]/30",
      text: "text-[#a855f7]",
    },
    confirmed_resolved: {
      label: "Confirmed Resolved",
      dotColor: "#10b981",
      bg: "bg-[#10b981]/10",
      border: "border-[#10b981]/30",
      text: "text-[#10b981]",
    },
    relapsed: {
      label: "Relapsed",
      dotColor: "#ef4444",
      bg: "bg-[#ef4444]/10",
      border: "border-[#ef4444]/30",
      text: "text-[#ef4444]",
    },
  };

  const config = configs[state] || configs.active;
  const padding = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-[11px]";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-mono uppercase tracking-wider font-semibold border ${config.bg} ${config.border} ${config.text} ${padding}`}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: config.dotColor }}
      />
      <span>{config.label}</span>
    </span>
  );
}
