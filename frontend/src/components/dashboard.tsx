"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
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
import { ApiError, api, type Opportunity } from "@/lib/api";

export function Dashboard() {
  const t = useT();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [businessArea, setBusinessArea] = useState("");

  const opportunities = useQuery({
    queryKey: ["opportunities"],
    queryFn: api.listOpportunities,
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
          {opportunities.data ? (
            <span className="text-muted-foreground font-mono text-xs tabular-nums">
              {opportunities.data.length}
            </span>
          ) : null}
        </div>

        <div className="bg-card overflow-hidden rounded-xl border">
          {opportunities.isLoading ? (
            <div className="divide-y">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 px-5 py-4">
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-5 w-24 rounded-full" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
          ) : opportunities.isError ? (
            <p className="text-destructive px-5 py-6 text-sm" role="alert">
              {t("Could not reach the API. Is the backend running on")}{" "}
              {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}?
            </p>
          ) : opportunities.data && opportunities.data.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-muted-foreground h-11 px-5 text-xs font-medium tracking-wide uppercase">
                    {t("Title")}
                  </TableHead>
                  <TableHead className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
                    {t("Business area")}
                  </TableHead>
                  <TableHead className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
                    {t("Status")}
                  </TableHead>
                  <TableHead className="text-muted-foreground px-5 text-right text-xs font-medium tracking-wide uppercase">
                    {t("Created")}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {opportunities.data.map((o: Opportunity) => (
                  <TableRow key={o.id} className="group">
                    <TableCell className="h-14 px-5 font-medium">
                      <Link
                        href={`/opportunities/${o.id}`}
                        className="group-hover:text-primary transition-colors"
                      >
                        {o.title}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {o.business_area ?? "-"}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={o.status} />
                    </TableCell>
                    <TableCell className="text-muted-foreground px-5 text-right font-mono text-xs tabular-nums">
                      {new Date(o.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="px-5 py-14 text-center">
              <p className="text-sm font-medium">{t("No opportunities yet")}</p>
              <p className="text-muted-foreground mx-auto mt-1 max-w-sm text-sm">
                {t(
                  "Create one above to start a context-driven interview, then score it and get a recommendation.",
                )}
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
