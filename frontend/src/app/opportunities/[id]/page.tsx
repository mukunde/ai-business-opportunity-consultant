"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef } from "react";

import { Cockpit } from "@/components/cockpit/cockpit";
import { DecisionPanel } from "@/components/decision/decision-panel";
import { VersionHistory } from "@/components/decision/version-history";
import { StatusBadge } from "@/components/status-badge";
import { buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useT } from "@/lib/i18n";
import { api } from "@/lib/api";

const DECISION_STATUSES = ["STRUCTURED", "SCORING", "RECOMMENDED", "REVIEW"];

export default function OpportunityDetailPage() {
  const t = useT();
  const { id } = useParams<{ id: string }>();
  const opportunity = useQuery({
    queryKey: ["opportunity", id],
    queryFn: () => api.getOpportunity(id),
    enabled: Boolean(id),
  });

  // When the interview just completes (status enters the decision phase), glide
  // the viewport down to the scoring section.
  const decisionRef = useRef<HTMLDivElement>(null);
  const prevStatus = useRef<string | undefined>(undefined);
  const status = opportunity.data?.status;
  useEffect(() => {
    if (!status) return;
    const justEntered =
      prevStatus.current !== undefined &&
      !DECISION_STATUSES.includes(prevStatus.current) &&
      DECISION_STATUSES.includes(status);
    prevStatus.current = status;
    if (justEntered) {
      const reduce = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
      decisionRef.current?.scrollIntoView({
        behavior: reduce ? "auto" : "smooth",
        block: "start",
      });
    }
  }, [status]);

  if (opportunity.isLoading) {
    return <Skeleton className="h-[70vh] w-full" />;
  }
  if (opportunity.isError || !opportunity.data) {
    return (
      <div className="space-y-4">
        <p className="text-destructive text-sm" role="alert">
          {t("Opportunity not found.")}
        </p>
        <Link href="/" className={buttonVariants({ variant: "outline" })}>
          {t("Back to dashboard")}
        </Link>
      </div>
    );
  }

  const o = opportunity.data;
  return (
    <div className="mx-auto max-w-[1680px] space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/"
            className="text-muted-foreground hover:text-foreground text-xs transition-colors"
          >
            ← {t("Dashboard")}
          </Link>
          <h1 className="mt-1 text-lg font-semibold tracking-tight">{o.title}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {o.business_area ?? t("No business area")}
          </p>
        </div>
        <StatusBadge status={o.status} />
      </div>

      <Cockpit opportunityId={id} />

      {DECISION_STATUSES.includes(o.status) ? (
        <div
          ref={decisionRef}
          className="animate-in fade-in slide-in-from-bottom-2 scroll-mt-20 space-y-4 duration-500 motion-reduce:animate-none"
        >
          <h2 className="text-base font-semibold tracking-tight">
            {t("Decision")}
          </h2>
          <DecisionPanel opportunityId={id} />
          <VersionHistory opportunityId={id} />
        </div>
      ) : null}
    </div>
  );
}
