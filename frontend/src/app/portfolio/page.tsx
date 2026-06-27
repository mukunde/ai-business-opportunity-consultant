"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo } from "react";

import {
  PortfolioMatrix,
  quadrantOf,
  type Quadrant,
} from "@/components/portfolio/portfolio-matrix";
import { StatusBadge } from "@/components/status-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useT } from "@/lib/i18n";
import { api, type OpportunitySummary } from "@/lib/api";

function isScored(
  o: OpportunitySummary,
): o is OpportunitySummary & { impact_score: number; feasibility_score: number } {
  return (
    typeof o.impact_score === "number" && typeof o.feasibility_score === "number"
  );
}

const QUADRANTS: { key: Quadrant; label: string; dot: string }[] = [
  { key: "quick", label: "Quick Wins", dot: "bg-emerald-500" },
  { key: "bet", label: "Strategic Bets", dot: "bg-amber-500" },
  { key: "low", label: "Low Priority", dot: "bg-zinc-400" },
];

export default function PortfolioPage() {
  const t = useT();
  const summaries = useQuery({
    queryKey: ["opportunities", "summary"],
    queryFn: api.listOpportunitySummaries,
  });

  const data = summaries.data;
  const scored = useMemo(() => (data ?? []).filter(isScored), [data]);
  const unscored = useMemo(
    () => (data ?? []).filter((o) => !isScored(o)),
    [data],
  );

  const counts = useMemo(() => {
    const c: Record<Quadrant, number> = { quick: 0, bet: 0, low: 0 };
    for (const o of scored) c[quadrantOf(o.impact_score, o.feasibility_score)] += 1;
    return c;
  }, [scored]);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header>
        <h1 className="text-lg font-semibold tracking-tight">{t("Portfolio")}</h1>
        <p className="text-muted-foreground mt-1 max-w-prose text-sm">
          {t(
            "Every scored opportunity placed by impact and feasibility, so the quick wins and the strategic bets separate themselves.",
          )}
        </p>
      </header>

      <div className="grid grid-cols-3 gap-3">
        {QUADRANTS.map((q) => (
          <div key={q.key} className="bg-card rounded-xl border p-4">
            <div className="text-muted-foreground flex items-center gap-2 text-xs font-medium tracking-wide uppercase">
              <span className={`size-1.5 rounded-full ${q.dot}`} aria-hidden />
              {t(q.label)}
            </div>
            <p className="mt-2 font-mono text-2xl font-semibold tabular-nums">
              {counts[q.key]}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-card rounded-xl border p-5">
        {summaries.isLoading ? (
          <Skeleton className="aspect-[480/440] w-full rounded-lg" />
        ) : scored.length > 0 ? (
          <PortfolioMatrix items={scored} />
        ) : (
          <div className="py-16 text-center">
            <p className="text-sm font-medium">{t("Nothing to plot yet")}</p>
            <p className="text-muted-foreground mx-auto mt-1 max-w-sm text-sm">
              {t("Score an opportunity to place it on the matrix.")}
            </p>
          </div>
        )}
      </div>

      {unscored.length > 0 ? (
        <section className="space-y-2">
          <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
            {t("Not yet scored")} ({unscored.length})
          </h2>
          <ul className="divide-y rounded-xl border">
            {unscored.map((o) => (
              <li key={o.id}>
                <Link
                  href={`/opportunities/${o.id}`}
                  className="hover:bg-muted/40 flex items-center justify-between gap-3 px-4 py-2.5 text-sm transition-colors"
                >
                  <span className="font-medium">{o.title}</span>
                  <StatusBadge status={o.status} />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
