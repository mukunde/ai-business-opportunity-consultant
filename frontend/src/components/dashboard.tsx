"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useT } from "@/lib/i18n";
import {
  ApiError,
  api,
  type OpportunityStatus,
  type OpportunitySummary,
} from "@/lib/api";
import { cn } from "@/lib/utils";

const STATUSES: OpportunityStatus[] = [
  "DRAFT",
  "INTERVIEW_ACTIVE",
  "STRUCTURED",
  "SCORING",
  "RECOMMENDED",
  "REVIEW",
];

const STATUS_LABEL: Record<OpportunityStatus, string> = {
  DRAFT: "Draft",
  INTERVIEW_ACTIVE: "Interview",
  STRUCTURED: "Structured",
  SCORING: "Scoring",
  RECOMMENDED: "Recommended",
  REVIEW: "Review",
};

const REC_TYPES = [
  "PROCEED",
  "PROCEED_WITH_CONDITIONS",
  "DEFER",
  "DO_NOT_PURSUE",
] as const;

const REC_LABEL: Record<string, string> = {
  PROCEED: "Proceed",
  PROCEED_WITH_CONDITIONS: "Proceed with conditions",
  DEFER: "Defer",
  DO_NOT_PURSUE: "Do not pursue",
};

const REC_COLOR: Record<string, string> = {
  PROCEED: "text-emerald-600 dark:text-emerald-400",
  PROCEED_WITH_CONDITIONS: "text-amber-600 dark:text-amber-400",
  DEFER: "text-muted-foreground",
  DO_NOT_PURSUE: "text-red-600 dark:text-red-400",
};

const selectClass =
  "border-input bg-transparent h-9 rounded-md border px-2 text-sm shadow-xs outline-none focus-visible:border-ring";

export function Dashboard() {
  const t = useT();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [businessArea, setBusinessArea] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"ALL" | OpportunityStatus>(
    "ALL",
  );
  const [recFilter, setRecFilter] = useState<string>("ALL");
  const [sort, setSort] = useState<"recent" | "score_desc" | "score_asc">(
    "recent",
  );

  const opportunities = useQuery({
    queryKey: ["opportunities", "summary"],
    queryFn: api.listOpportunitySummaries,
  });

  const create = useMutation({
    mutationFn: () =>
      api.createOpportunity({ title, business_area: businessArea || null }),
    onSuccess: () => {
      setTitle("");
      setBusinessArea("");
      void queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      toast.success(t("Opportunity created"));
    },
    onError: (e) =>
      toast.error(e instanceof ApiError ? e.message : t("Failed to create")),
  });

  const all = useMemo(() => opportunities.data ?? [], [opportunities.data]);
  const rows = useMemo(() => {
    const q = search.trim().toLowerCase();
    const filtered = all.filter((o) => {
      if (q && !`${o.title} ${o.business_area ?? ""}`.toLowerCase().includes(q))
        return false;
      if (statusFilter !== "ALL" && o.status !== statusFilter) return false;
      if (recFilter === "NONE" && o.recommendation_type) return false;
      if (recFilter !== "ALL" && recFilter !== "NONE" && o.recommendation_type !== recFilter)
        return false;
      return true;
    });
    if (sort === "recent") return filtered;
    const score = (o: OpportunitySummary) =>
      o.final_score ?? (sort === "score_desc" ? -1 : Infinity);
    return [...filtered].sort((a, b) =>
      sort === "score_desc" ? score(b) - score(a) : score(a) - score(b),
    );
  }, [all, search, statusFilter, recFilter, sort]);

  return (
    <div className="mx-auto max-w-6xl space-y-10">
      <header>
        <h1 className="text-lg font-semibold tracking-tight">{t("Dashboard")}</h1>
        <p className="text-muted-foreground mt-1 max-w-prose text-sm">
          {t(
            "Turn a vague idea into a structured, scored, decision-ready AI opportunity assessment.",
          )}
        </p>
      </header>

      <section className="bg-card rounded-xl border p-5 sm:p-6">
        <h2 className="text-sm font-medium">{t("New assessment")}</h2>
        <form
          className="mt-4 grid gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end"
          onSubmit={(e) => {
            e.preventDefault();
            if (title.trim()) create.mutate();
          }}
        >
          <div className="space-y-1.5">
            <Label htmlFor="title">{t("Opportunity title")}</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Customer Support Automation"
              required
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="area">{t("Business area")}</Label>
            <Input
              id="area"
              value={businessArea}
              onChange={(e) => setBusinessArea(e.target.value)}
              placeholder="Support"
            />
          </div>
          <Button type="submit" disabled={!title.trim() || create.isPending}>
            {create.isPending ? t("Creating…") : t("Start assessment")}
          </Button>
        </form>
      </section>

      <section className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h2 className="text-sm font-medium">{t("Opportunities")}</h2>
          <span className="text-muted-foreground font-mono text-xs tabular-nums">
            {rows.length}
            {rows.length !== all.length ? ` / ${all.length}` : ""}
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("Search opportunities…")}
            className="h-9 max-w-xs"
          />
          <select
            className={cn(selectClass)}
            value={statusFilter}
            onChange={(e) =>
              setStatusFilter(e.target.value as "ALL" | OpportunityStatus)
            }
            aria-label={t("Status")}
          >
            <option value="ALL">{t("All statuses")}</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {t(STATUS_LABEL[s])}
              </option>
            ))}
          </select>
          <select
            className={cn(selectClass)}
            value={recFilter}
            onChange={(e) => setRecFilter(e.target.value)}
            aria-label={t("Recommendation")}
          >
            <option value="ALL">{t("All recommendations")}</option>
            {REC_TYPES.map((r) => (
              <option key={r} value={r}>
                {t(REC_LABEL[r])}
              </option>
            ))}
            <option value="NONE">{t("No recommendation")}</option>
          </select>
          <select
            className={cn(selectClass)}
            value={sort}
            onChange={(e) =>
              setSort(e.target.value as "recent" | "score_desc" | "score_asc")
            }
            aria-label={t("Sort by")}
          >
            <option value="recent">{t("Newest")}</option>
            <option value="score_desc">{t("Highest score")}</option>
            <option value="score_asc">{t("Lowest score")}</option>
          </select>
        </div>

        <div className="bg-card overflow-hidden rounded-xl border">
          {opportunities.isLoading ? (
            <div className="divide-y">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 px-5 py-4">
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-5 w-24 rounded-full" />
                  <Skeleton className="h-4 w-12" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          ) : opportunities.isError ? (
            <p className="text-destructive px-5 py-6 text-sm" role="alert">
              {t("Could not reach the API. Is the backend running on")}{" "}
              {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}?
            </p>
          ) : all.length === 0 ? (
            <div className="px-5 py-14 text-center">
              <p className="text-sm font-medium">{t("No opportunities yet")}</p>
              <p className="text-muted-foreground mx-auto mt-1 max-w-sm text-sm">
                {t(
                  "Create one above to start a context-driven interview, then score it and get a recommendation.",
                )}
              </p>
            </div>
          ) : rows.length === 0 ? (
            <p className="text-muted-foreground px-5 py-10 text-center text-sm">
              {t("No opportunities match these filters.")}
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-muted-foreground h-11 px-5 text-xs font-medium tracking-wide uppercase">
                    {t("Title")}
                  </TableHead>
                  <TableHead className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
                    {t("Status")}
                  </TableHead>
                  <TableHead className="text-muted-foreground text-right text-xs font-medium tracking-wide uppercase">
                    {t("Score")}
                  </TableHead>
                  <TableHead className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
                    {t("Recommendation")}
                  </TableHead>
                  <TableHead className="text-muted-foreground px-5 text-right text-xs font-medium tracking-wide uppercase">
                    {t("Created")}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((o) => (
                  <TableRow key={o.id} className="group">
                    <TableCell className="h-14 px-5 font-medium">
                      <Link
                        href={`/opportunities/${o.id}`}
                        className="group-hover:text-primary transition-colors"
                      >
                        {o.title}
                      </Link>
                      {o.business_area ? (
                        <span className="text-muted-foreground ml-2 text-xs">
                          {o.business_area}
                        </span>
                      ) : null}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={o.status} />
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm tabular-nums">
                      {typeof o.final_score === "number" ? (
                        o.final_score.toFixed(1)
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell
                      className={cn(
                        "text-sm",
                        o.recommendation_type
                          ? REC_COLOR[o.recommendation_type]
                          : "text-muted-foreground",
                      )}
                    >
                      {o.recommendation_type
                        ? t(REC_LABEL[o.recommendation_type] ?? o.recommendation_type)
                        : "-"}
                    </TableCell>
                    <TableCell className="text-muted-foreground px-5 text-right font-mono text-xs tabular-nums">
                      {new Date(o.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </section>
    </div>
  );
}
