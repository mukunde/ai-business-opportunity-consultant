"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Markdown } from "@/components/decision/markdown";
import { Button } from "@/components/ui/button";
import { useT } from "@/lib/i18n";
import {
  ApiError,
  api,
  type Deliverable,
  type DeliverableKind,
} from "@/lib/api";

const KINDS: { kind: DeliverableKind; label: string }[] = [
  { kind: "CONDENSED_BRIEF", label: "Condensed brief" },
  { kind: "IMPLEMENTATION_ROADMAP", label: "Implementation roadmap" },
  { kind: "PRD", label: "PRD" },
  { kind: "TRD", label: "TRD" },
  { kind: "UIUX", label: "UI/UX doc" },
  { kind: "BACKEND_SCHEMA", label: "Backend schema" },
  { kind: "APPFLOW", label: "Appflow" },
];

export function DeliverablesPanel({ opportunityId }: { opportunityId: string }) {
  const t = useT();
  const qc = useQueryClient();

  const list = useQuery({
    queryKey: ["deliverables", opportunityId],
    queryFn: () => api.listDeliverables(opportunityId),
  });

  const generate = useMutation({
    mutationFn: (kind: DeliverableKind) =>
      api.generateDeliverable(opportunityId, kind),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["deliverables", opportunityId] });
      toast.success(t("Deliverable generated"));
    },
    onError: (e: unknown) =>
      toast.error(e instanceof ApiError ? e.message : t("Request failed")),
  });

  // Collapse to the latest of each kind (list is oldest-first, so last wins).
  const latest = new Map<string, Deliverable>();
  for (const d of list.data ?? []) latest.set(d.kind, d);

  return (
    <section className="bg-card rounded-xl border p-5">
      <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
        {t("Handoff dossier")}
      </h2>
      <p className="text-muted-foreground mt-1 max-w-prose text-sm">
        {t("Generate ready-to-use documents from this assessment.")}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {KINDS.map(({ kind, label }) => {
          const pending = generate.isPending && generate.variables === kind;
          return (
            <Button
              key={kind}
              variant="outline"
              size="sm"
              disabled={pending}
              onClick={() => generate.mutate(kind)}
            >
              {pending ? t("Generating…") : t(label)}
            </Button>
          );
        })}
      </div>

      {latest.size > 0 ? (
        <div className="mt-5 space-y-3">
          {KINDS.filter((k) => latest.has(k.kind)).map(({ kind, label }) => (
            <details key={kind} className="rounded-lg border p-4">
              <summary className="cursor-pointer text-sm font-medium">
                {t(label)}
              </summary>
              <div className="mt-3">
                <Markdown>{latest.get(kind)!.markdown_content}</Markdown>
              </div>
            </details>
          ))}
        </div>
      ) : null}
    </section>
  );
}
