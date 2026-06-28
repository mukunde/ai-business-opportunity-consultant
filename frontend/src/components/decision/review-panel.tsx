"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useT } from "@/lib/i18n";
import { ApiError, api, type ReviewDecision } from "@/lib/api";

export function ReviewPanel({ opportunityId }: { opportunityId: string }) {
  const t = useT();
  const qc = useQueryClient();
  const [note, setNote] = useState("");

  const review = useQuery({
    queryKey: ["review", opportunityId],
    queryFn: () => api.getReview(opportunityId),
    retry: false,
  });

  const decide = useMutation({
    mutationFn: (decision: ReviewDecision) =>
      api.createReview(opportunityId, decision, note.trim() || undefined),
    onSuccess: () => {
      setNote("");
      void qc.invalidateQueries({ queryKey: ["review", opportunityId] });
      void qc.invalidateQueries({ queryKey: ["opportunity", opportunityId] });
    },
    onError: (e: unknown) =>
      toast.error(e instanceof ApiError ? e.message : t("Request failed")),
  });

  const verdict = review.data;

  return (
    <section className="bg-card rounded-xl border p-5">
      <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
        {t("Human review")}
      </h2>

      {verdict ? (
        <div
          className={`animate-in fade-in zoom-in-95 mt-4 rounded-lg border p-4 duration-300 motion-reduce:animate-none ${
            verdict.decision === "APPROVE"
              ? "border-emerald-500/40 bg-emerald-50 text-emerald-900"
              : "border-red-500/40 bg-red-50 text-red-900"
          }`}
        >
          <p className="text-lg font-semibold">
            {verdict.decision === "APPROVE" ? t("Approved") : t("Rejected")}
          </p>
          {verdict.note ? (
            <p className="mt-1 text-sm opacity-90">{verdict.note}</p>
          ) : null}
          <p className="mt-2 font-mono text-xs tabular-nums opacity-70">
            {new Date(verdict.created_at).toLocaleString()}
          </p>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          <p className="text-muted-foreground text-sm">
            {t("Record your verdict to close this opportunity.")}
          </p>
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            placeholder={t("Add a note (optional)")}
            className="resize-none"
          />
          <div className="flex gap-2">
            <Button
              disabled={decide.isPending}
              onClick={() => decide.mutate("APPROVE")}
            >
              {t("Approve")}
            </Button>
            <Button
              variant="outline"
              disabled={decide.isPending}
              onClick={() => decide.mutate("REJECT")}
            >
              {t("Reject")}
            </Button>
          </div>
        </div>
      )}
    </section>
  );
}
