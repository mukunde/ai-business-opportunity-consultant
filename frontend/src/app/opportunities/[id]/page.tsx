"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";

import { StatusBadge } from "@/components/status-badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const opportunity = useQuery({
    queryKey: ["opportunity", id],
    queryFn: () => api.getOpportunity(id),
    enabled: Boolean(id),
  });

  if (opportunity.isLoading) {
    return <p className="text-muted-foreground text-sm">Loading...</p>;
  }
  if (opportunity.isError || !opportunity.data) {
    return (
      <div className="space-y-4">
        <p className="text-destructive text-sm">Opportunity not found.</p>
        <Link href="/" className={buttonVariants({ variant: "outline" })}>
          Back to dashboard
        </Link>
      </div>
    );
  }

  const o = opportunity.data;
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{o.title}</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {o.business_area ?? "No business area"}
          </p>
        </div>
        <StatusBadge status={o.status} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Assessment</CardTitle>
        </CardHeader>
        <CardContent className="text-muted-foreground text-sm">
          The interview cockpit (conversation, live context model, scoring and
          recommendation) lands in the next slice.
        </CardContent>
      </Card>

      <Link href="/" className={buttonVariants({ variant: "outline" })}>
        Back to dashboard
      </Link>
    </div>
  );
}
