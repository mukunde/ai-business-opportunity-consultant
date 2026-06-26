import { Badge } from "@/components/ui/badge";
import type { OpportunityStatus } from "@/lib/api";
import { cn } from "@/lib/utils";

const STYLES: Record<OpportunityStatus, string> = {
  DRAFT: "bg-muted text-muted-foreground",
  INTERVIEW_ACTIVE: "bg-blue-100 text-blue-800",
  STRUCTURED: "bg-indigo-100 text-indigo-800",
  SCORING: "bg-amber-100 text-amber-900",
  RECOMMENDED: "bg-emerald-100 text-emerald-800",
  REVIEW: "bg-purple-100 text-purple-800",
};

export function StatusBadge({ status }: { status: OpportunityStatus }) {
  return (
    <Badge variant="outline" className={cn("border-transparent", STYLES[status])}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
