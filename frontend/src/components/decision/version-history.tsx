"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useT } from "@/lib/i18n";
import { ApiError, api, type Version } from "@/lib/api";

// Snapshot recommendation_type is a plain string in the schema, so key by string.
const REC_LABEL: Record<string, string> = {
  PROCEED: "Proceed",
  PROCEED_WITH_CONDITIONS: "Proceed with conditions",
  DEFER: "Defer",
  DO_NOT_PURSUE: "Do not pursue",
};

const NONE = "·";

function finalScore(v: Version): number | null {
  const s = v.snapshot.score?.final_score;
  return typeof s === "number" ? s : null;
}

/** What changed from the previous (older) version to this one. */
function VersionDiff({ curr, prev }: { curr: Version; prev: Version }) {
  const t = useT();
  const a = finalScore(prev);
  const b = finalScore(curr);
  const delta = a !== null && b !== null ? b - a : null;
  const recBefore = prev.snapshot.recommendation_type;
  const recAfter = curr.snapshot.recommendation_type;
  const recChanged = recBefore !== recAfter;

  if ((delta === null || Math.abs(delta) < 0.05) && !recChanged) {
    return (
      <p className="text-muted-foreground text-xs">
        {t("No change since")} v{prev.version_number}
      </p>
    );
  }

  return (
    <div className="text-muted-foreground flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
      <span>
        {t("Since")} v{prev.version_number}:
      </span>
      {delta !== null && Math.abs(delta) >= 0.05 ? (
        <span
          className={
            delta > 0
              ? "text-emerald-600 dark:text-emerald-400"
              : "text-red-600 dark:text-red-400"
          }
        >
          {t("Score")} {delta > 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}
        </span>
      ) : null}
      {recChanged ? (
        <span>
          {recBefore ? t(REC_LABEL[recBefore] ?? recBefore) : NONE} {"→"}{" "}
          <span className="text-foreground font-medium">
            {recAfter ? t(REC_LABEL[recAfter] ?? recAfter) : NONE}
          </span>
        </span>
      ) : null}
    </div>
  );
}

export function VersionHistory({ opportunityId }: { opportunityId: string }) {
  const t = useT();
  const qc = useQueryClient();
  const [note, setNote] = useState("");

  const versions = useQuery({
    queryKey: ["versions", opportunityId],
    queryFn: () => api.listVersions(opportunityId),
  });

  const save = useMutation({
    mutationFn: () => api.createVersion(opportunityId, note.trim() || undefined),
    onSuccess: () => {
      setNote("");
      void qc.invalidateQueries({ queryKey: ["versions", opportunityId] });
      void qc.invalidateQueries({ queryKey: ["opportunity", opportunityId] });
      toast.success(t("Version saved"));
    },
    onError: (e: unknown) =>
      toast.error(e instanceof ApiError ? e.message : t("Request failed")),
  });

  const list = versions.data ?? [];

  return (
    <section className="bg-card rounded-xl border p-5">
      <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
        {t("Version history")}
      </h2>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Input
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder={t("Label this version (optional)")}
          className="h-9 max-w-xs"
        />
        <Button onClick={() => save.mutate()} disabled={save.isPending}>
          {save.isPending ? t("Saving…") : t("Save version")}
        </Button>
      </div>

      {list.length > 0 ? (
        <ol className="mt-5 space-y-3">
          {list.map((v, i) => {
            const prev = list[i + 1]; // list is newest-first; next item is older
            const score = finalScore(v);
            const rec = v.snapshot.recommendation_type;
            return (
              <li key={v.id} className="rounded-lg border p-3">
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-sm font-semibold">
                      v{v.version_number}
                    </span>
                    {v.note ? (
                      <span className="text-sm">{v.note}</span>
                    ) : null}
                  </div>
                  <span className="text-muted-foreground font-mono text-xs">
                    {new Date(v.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
                  <span>
                    <span className="text-muted-foreground">{t("Score")}: </span>
                    <span className="font-mono tabular-nums">
                      {score !== null ? `${score.toFixed(1)}/10` : t("Not scored")}
                    </span>
                  </span>
                  <span>
                    <span className="text-muted-foreground">
                      {t("Recommendation")}:{" "}
                    </span>
                    {rec ? t(REC_LABEL[rec] ?? rec) : NONE}
                  </span>
                </div>

                {prev ? (
                  <div className="mt-2 border-t pt-2">
                    <VersionDiff curr={v} prev={prev} />
                  </div>
                ) : null}
              </li>
            );
          })}
        </ol>
      ) : (
        <p className="text-muted-foreground mt-4 text-sm">
          {t("Save the current assessment to capture a comparable snapshot.")}
        </p>
      )}
    </section>
  );
}
