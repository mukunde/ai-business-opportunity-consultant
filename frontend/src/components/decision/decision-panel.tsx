"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Markdown } from "@/components/decision/markdown";
import { Button } from "@/components/ui/button";
import {
  ApiError,
  api,
  type Recommendation,
  type RecommendationType,
  type ReportBundle,
  type Score,
} from "@/lib/api";

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="bg-card rounded-xl border p-5">
      <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

const SCORE_METRICS: { key: keyof Score; label: string }[] = [
  { key: "roi_score", label: "ROI" },
  { key: "impact_score", label: "Impact" },
  { key: "feasibility_score", label: "Feasibility" },
  { key: "risk_score", label: "Risk" },
  { key: "strategic_alignment_score", label: "Strategic" },
  { key: "time_to_value_score", label: "Time to value" },
];

function Slider({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <label className="flex items-center gap-3 text-sm">
      <span className="w-28 shrink-0">{label}</span>
      <input
        type="range"
        min={1}
        max={10}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="accent-primary flex-1"
      />
      <span className="w-6 text-right font-mono tabular-nums">{value}</span>
    </label>
  );
}

function ScoringSection({
  score,
  onScore,
  pending,
}: {
  score?: Score;
  onScore: (input: {
    impact: number;
    ease: number;
    strategic_alignment: number;
  }) => void;
  pending: boolean;
}) {
  const [impact, setImpact] = useState(7);
  const [ease, setEase] = useState(6);
  const [strategic, setStrategic] = useState(8);

  return (
    <Section title="Scoring">
      <div className="space-y-2.5">
        <Slider label="Impact" value={impact} onChange={setImpact} />
        <Slider label="Ease" value={ease} onChange={setEase} />
        <Slider
          label="Strategic align."
          value={strategic}
          onChange={setStrategic}
        />
      </div>
      <Button
        className="mt-4"
        disabled={pending}
        onClick={() =>
          onScore({ impact, ease, strategic_alignment: strategic })
        }
      >
        {pending ? "Scoring…" : score ? "Re-score" : "Score opportunity"}
      </Button>

      {score ? (
        <div className="mt-5 border-t pt-5">
          <div className="flex items-end gap-6">
            <div>
              <p className="text-muted-foreground text-xs">Priority score</p>
              <p className="font-mono text-3xl font-semibold tabular-nums">
                {score.final_score.toFixed(1)}
                <span className="text-muted-foreground text-base">/10</span>
              </p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs">Confidence</p>
              <p className="font-mono text-xl tabular-nums">
                {Math.round(score.confidence * 100)}%
              </p>
            </div>
          </div>
          <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-3">
            {SCORE_METRICS.map((m) => (
              <div key={m.key} className="flex justify-between text-sm">
                <dt className="text-muted-foreground">{m.label}</dt>
                <dd className="font-mono tabular-nums">
                  {(score[m.key] as number).toFixed(1)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
    </Section>
  );
}

const REC_STYLE: Record<RecommendationType, string> = {
  PROCEED: "border-emerald-500/40 bg-emerald-50 text-emerald-900",
  PROCEED_WITH_CONDITIONS: "border-amber-500/40 bg-amber-50 text-amber-900",
  DEFER: "border-border bg-muted text-foreground",
  DO_NOT_PURSUE: "border-red-500/40 bg-red-50 text-red-900",
};

const REC_LABEL: Record<RecommendationType, string> = {
  PROCEED: "Proceed",
  PROCEED_WITH_CONDITIONS: "Proceed with conditions",
  DEFER: "Defer",
  DO_NOT_PURSUE: "Do not pursue",
};

function RecommendationSection({
  rec,
  canDecide,
  onDecide,
  pending,
}: {
  rec?: Recommendation;
  canDecide: boolean;
  onDecide: () => void;
  pending: boolean;
}) {
  return (
    <Section title="Recommendation">
      {rec ? (
        <div className={`rounded-lg border p-4 ${REC_STYLE[rec.type]}`}>
          <p className="text-lg font-semibold">{REC_LABEL[rec.type]}</p>
          <p className="mt-1 text-sm opacity-90">{rec.rationale}</p>
          <p className="mt-2 font-mono text-xs tabular-nums opacity-70">
            confidence {Math.round(rec.confidence * 100)}%
          </p>
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">
          {canDecide
            ? "Turn the score into a decision."
            : "Score the opportunity first."}
        </p>
      )}
      <Button
        className="mt-4"
        variant={rec ? "outline" : "default"}
        disabled={!canDecide || pending}
        onClick={onDecide}
      >
        {pending ? "Deciding…" : rec ? "Re-decide" : "Get recommendation"}
      </Button>
    </Section>
  );
}

function ReportSection({
  report,
  canGenerate,
  onGenerate,
  pending,
}: {
  report?: ReportBundle;
  canGenerate: boolean;
  onGenerate: () => void;
  pending: boolean;
}) {
  return (
    <Section title="Report">
      <Button
        variant={report ? "outline" : "default"}
        disabled={!canGenerate || pending}
        onClick={onGenerate}
      >
        {pending
          ? "Generating…"
          : report
            ? "Regenerate report"
            : "Generate report"}
      </Button>
      {!canGenerate ? (
        <p className="text-muted-foreground mt-3 text-sm">
          Get a recommendation first.
        </p>
      ) : null}

      {report ? (
        <div className="mt-5 space-y-4">
          <details open className="rounded-lg border p-4">
            <summary className="cursor-pointer text-sm font-medium">
              Executive summary
            </summary>
            <div className="mt-3">
              <Markdown>{report.executive_summary.markdown_content}</Markdown>
            </div>
          </details>
          <details className="rounded-lg border p-4">
            <summary className="cursor-pointer text-sm font-medium">
              Detailed assessment
            </summary>
            <div className="mt-3">
              <Markdown>{report.detailed_assessment.markdown_content}</Markdown>
            </div>
          </details>
        </div>
      ) : null}
    </Section>
  );
}

export function DecisionPanel({ opportunityId }: { opportunityId: string }) {
  const qc = useQueryClient();
  const id = opportunityId;

  const score = useQuery({
    queryKey: ["score", id],
    queryFn: () => api.getScore(id),
    retry: false,
  });
  const recommendation = useQuery({
    queryKey: ["recommendation", id],
    queryFn: () => api.getRecommendation(id),
    retry: false,
  });
  const report = useQuery({
    queryKey: ["report", id],
    queryFn: () => api.getReport(id),
    retry: false,
  });

  const invalidate = (...keys: string[]) =>
    keys.forEach((k) => void qc.invalidateQueries({ queryKey: [k, id] }));

  const onError = (e: unknown) =>
    toast.error(e instanceof ApiError ? e.message : "Request failed");

  const scoreMut = useMutation({
    mutationFn: (input: {
      impact: number;
      ease: number;
      strategic_alignment: number;
    }) => api.createScore(id, input),
    onSuccess: () => invalidate("score", "recommendation", "report", "opportunity"),
    onError,
  });
  const recMut = useMutation({
    mutationFn: () => api.createRecommendation(id),
    onSuccess: () => invalidate("recommendation", "report", "opportunity"),
    onError,
  });
  const reportMut = useMutation({
    mutationFn: () => api.createReport(id),
    onSuccess: () => invalidate("report", "opportunity"),
    onError,
  });

  return (
    <div className="space-y-5">
      <ScoringSection
        score={score.data}
        onScore={scoreMut.mutate}
        pending={scoreMut.isPending}
      />
      <RecommendationSection
        rec={recommendation.data}
        canDecide={score.isSuccess}
        onDecide={() => recMut.mutate()}
        pending={recMut.isPending}
      />
      <ReportSection
        report={report.data}
        canGenerate={recommendation.isSuccess}
        onGenerate={() => reportMut.mutate()}
        pending={reportMut.isPending}
      />
    </div>
  );
}
