"use client";

import { useT } from "@/lib/i18n";
import type { OpportunityStatus } from "@/lib/api";
import { cn } from "@/lib/utils";

// Lifecycle is a progression, so each stage keeps a distinct hue - but only in
// the dot. The pill chrome stays uniform (border + foreground text), which reads
// cohesive instead of rainbow and adapts to light/dark automatically.
const DOT: Record<OpportunityStatus, string> = {
  DRAFT: "bg-zinc-400",
  INTERVIEW_ACTIVE: "bg-blue-500",
  STRUCTURED: "bg-indigo-500",
  SCORING: "bg-amber-500",
  RECOMMENDED: "bg-emerald-500",
  REVIEW: "bg-violet-500",
};

const LABEL: Record<OpportunityStatus, string> = {
  DRAFT: "Draft",
  INTERVIEW_ACTIVE: "Interview",
  STRUCTURED: "Structured",
  SCORING: "Scoring",
  RECOMMENDED: "Recommended",
  REVIEW: "Review",
};

export function StatusBadge({ status }: { status: OpportunityStatus }) {
  const t = useT();
  return (
    <span className="border-border text-foreground inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium">
      <span className={cn("size-1.5 rounded-full", DOT[status])} aria-hidden />
      {t(LABEL[status])}
    </span>
  );
}
