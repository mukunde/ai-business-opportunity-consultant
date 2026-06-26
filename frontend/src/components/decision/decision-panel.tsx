"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Markdown } from "@/components/decision/markdown";
import { InfoTip } from "@/components/info-tip";
import { Button } from "@/components/ui/button";
import { useT } from "@/lib/i18n";
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

const SCORE_METRICS: {
  key: keyof Score;
  label: string;
  formula: string;
  rationale: string;
}[] = [
  {
    key: "roi_score",
    label: "ROI",
    formula: "ROI readiness × 10",
    rationale:
      "Can we size the return? Driven by whether business volume and handling time are known, the inputs an ROI estimate needs.",
  },
  {
    key: "impact_score",
    label: "Impact",
    formula: "your Impact input (1-10)",
    rationale: "Analyst-judged business impact of solving this problem.",
  },
  {
    key: "feasibility_score",
    label: "Feasibility",
    formula: "data readiness × 10",
    rationale: "Is there data to build on? High when data availability is known.",
  },
  {
    key: "risk_score",
    label: "Risk",
    formula: "(1 - completeness) × 5 + (1 - data readiness) × 5",
    rationale:
      "Rises with missing context and missing data. Lower is better; it is subtracted in the final score.",
  },
  {
    key: "strategic_alignment_score",
    label: "Strategic",
    formula: "your Strategic alignment input (1-10)",
    rationale: "Analyst-judged fit with strategy.",
  },
  {
    key: "time_to_value_score",
    label: "Time to value",
    formula: "data readiness × 10",
    rationale: "Proxied by feasibility: more data-ready means value lands sooner.",
  },
];

function Slider({
  label,
  value,
  onChange,
  tip,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  tip?: string;
}) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="flex w-32 shrink-0 items-center">
        {label}
        {tip ? <InfoTip text={tip} /> : null}
      </span>
      <input
        type="range"
        min={1}
        max={10}
        value={value}
        aria-label={label}
        onChange={(e) => onChange(Number(e.target.value))}
        className="accent-primary flex-1"
      />
      <span className="w-6 text-right font-mono tabular-nums">{value}</span>
    </div>
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
  const t = useT();
  const [impact, setImpact] = useState(7);
  const [ease, setEase] = useState(6);
  const [strategic, setStrategic] = useState(8);

  return (
    <Section title={t("Scoring")}>
      <div className="space-y-2.5">
        <Slider
          label={t("Impact")}
          value={impact}
          onChange={setImpact}
          tip={t(
            "How much value would solving this create? Higher means bigger business impact. Your judgement, 1 to 10.",
          )}
        />
        <Slider
          label={t("Ease")}
          value={ease}
          onChange={setEase}
          tip={t(
            "How easy is it to deliver? Higher means simpler to build and roll out. Feeds the ICE score. 1 to 10.",
          )}
        />
        <Slider
          label={t("Strategic align.")}
          value={strategic}
          onChange={setStrategic}
          tip={t("How well does it fit the company strategy and priorities? 1 to 10.")}
        />
      </div>
      <Button
        className="mt-4"
        disabled={pending}
        onClick={() =>
          onScore({ impact, ease, strategic_alignment: strategic })
        }
      >
        {pending
          ? t("Scoring…")
          : score
            ? t("Re-score")
            : t("Score opportunity")}
      </Button>

      {score ? (
        <div className="animate-in fade-in slide-in-from-top-1 mt-5 space-y-4 border-t pt-5 duration-300 motion-reduce:animate-none">
          <div className="flex items-end gap-6">
            <div>
              <p className="text-muted-foreground text-xs">
                {t("Priority score")}
              </p>
              <p className="font-mono text-3xl font-semibold tabular-nums">
                {score.final_score.toFixed(1)}
                <span className="text-muted-foreground text-base">/10</span>
              </p>
            </div>
            <details className="group">
              <summary className="cursor-pointer list-none">
                <p className="text-muted-foreground text-xs">
                  {t("Confidence")}
                  <span className="ml-1 opacity-60 group-open:hidden">(?)</span>
                </p>
                <p className="font-mono text-xl tabular-nums">
                  {Math.round(score.confidence * 100)}%
                </p>
              </summary>
              <p className="text-muted-foreground mt-1 max-w-xs text-xs">
                {t(
                  "= overall context completeness. An incomplete interview lowers the score's confidence rather than faking certainty.",
                )}
              </p>
            </details>
          </div>

          <div className="bg-muted/50 text-muted-foreground rounded-md p-3 text-xs">
            <p className="text-foreground font-mono">
              Final = 0.3×ROI + 0.3×ICE + 0.2×Strategic - 0.2×Risk (0-10)
            </p>
            <p className="mt-1.5">
              {t(
                "ICE = Impact × Confidence × Ease (normalized to 0-10). Click any metric below for its rationale and calculation.",
              )}
            </p>
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            {SCORE_METRICS.map((m) => (
              <details
                key={m.key}
                className="group rounded-md border px-3 py-2"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between text-sm">
                  <span className="text-muted-foreground group-hover:text-foreground transition-colors">
                    {t(m.label)}
                  </span>
                  <span className="font-mono tabular-nums">
                    {(score[m.key] as number).toFixed(1)}
                  </span>
                </summary>
                <div className="text-muted-foreground mt-2 space-y-1.5 border-t pt-2 text-xs">
                  <p>{t(m.rationale)}</p>
                  <p className="text-foreground font-mono">
                    {t(m.label)} = {t(m.formula)}
                  </p>
                </div>
              </details>
            ))}
          </div>
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
  const t = useT();
  return (
    <Section title={t("Recommendation")}>
      {rec ? (
        <div
          className={`animate-in fade-in zoom-in-95 rounded-lg border p-4 duration-300 motion-reduce:animate-none ${REC_STYLE[rec.type]}`}
        >
          <p className="text-lg font-semibold">{t(REC_LABEL[rec.type])}</p>
          <p className="mt-1 text-sm opacity-90">{rec.rationale}</p>
          <p className="mt-2 font-mono text-xs tabular-nums opacity-70">
            {t("confidence")} {Math.round(rec.confidence * 100)}%
          </p>
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">
          {canDecide
            ? t("Turn the score into a decision.")
            : t("Score the opportunity first.")}
        </p>
      )}
      <Button
        className="mt-4"
        variant={rec ? "outline" : "default"}
        disabled={!canDecide || pending}
        onClick={onDecide}
      >
        {pending
          ? t("Deciding…")
          : rec
            ? t("Re-decide")
            : t("Get recommendation")}
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
  const t = useT();
  return (
    <Section title={t("Report")}>
      <Button
        variant={report ? "outline" : "default"}
        disabled={!canGenerate || pending}
        onClick={onGenerate}
      >
        {pending
          ? t("Generating…")
          : report
            ? t("Regenerate report")
            : t("Generate report")}
      </Button>
      {!canGenerate ? (
        <p className="text-muted-foreground mt-3 text-sm">
          {t("Get a recommendation first.")}
        </p>
      ) : null}

      {report ? (
        <div className="animate-in fade-in slide-in-from-top-1 mt-5 space-y-4 duration-300 motion-reduce:animate-none">
          <details open className="rounded-lg border p-4">
            <summary className="cursor-pointer text-sm font-medium">
              {t("Executive summary")}
            </summary>
            <div className="mt-3">
              <Markdown>{report.executive_summary.markdown_content}</Markdown>
            </div>
          </details>
          <details className="rounded-lg border p-4">
            <summary className="cursor-pointer text-sm font-medium">
              {t("Detailed assessment")}
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
  const t = useT();
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
    toast.error(e instanceof ApiError ? e.message : t("Request failed"));

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
