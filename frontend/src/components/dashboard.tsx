"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import { ApiError, api, type Opportunity } from "@/lib/api";

export function Dashboard() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [businessArea, setBusinessArea] = useState("");

  const opportunities = useQuery({
    queryKey: ["opportunities"],
    queryFn: api.listOpportunities,
  });

  const create = useMutation({
    mutationFn: () =>
      api.createOpportunity({
        title,
        business_area: businessArea || null,
      }),
    onSuccess: () => {
      setTitle("");
      setBusinessArea("");
      void queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      toast.success("Opportunity created");
    },
    onError: (e) =>
      toast.error(e instanceof ApiError ? e.message : "Failed to create"),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Qualify AI opportunities through context-driven interviews.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4 sm:flex-row sm:items-end"
            onSubmit={(e) => {
              e.preventDefault();
              if (title.trim()) create.mutate();
            }}
          >
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="title">Opportunity title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Customer Support Automation"
                required
              />
            </div>
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="area">Business area</Label>
              <Input
                id="area"
                value={businessArea}
                onChange={(e) => setBusinessArea(e.target.value)}
                placeholder="Support"
              />
            </div>
            <Button type="submit" disabled={!title.trim() || create.isPending}>
              {create.isPending ? "Creating..." : "Start assessment"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center justify-between space-y-0">
          <CardTitle className="text-base">Opportunities</CardTitle>
          {opportunities.data ? (
            <span className="text-muted-foreground font-mono text-sm tabular-nums">
              {opportunities.data.length}
            </span>
          ) : null}
        </CardHeader>
        <CardContent>
          {opportunities.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-5 w-20 rounded-full" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
          ) : opportunities.isError ? (
            <p className="text-destructive text-sm">
              Could not reach the API. Is the backend running on{" "}
              {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}?
            </p>
          ) : opportunities.data && opportunities.data.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Business area</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {opportunities.data.map((o: Opportunity) => (
                  <TableRow key={o.id}>
                    <TableCell className="font-medium">
                      <Link
                        href={`/opportunities/${o.id}`}
                        className="hover:text-primary transition-colors"
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
                    <TableCell className="text-muted-foreground text-right font-mono text-xs tabular-nums">
                      {new Date(o.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-10 text-center">
              <p className="text-sm font-medium">No opportunities yet</p>
              <p className="text-muted-foreground mt-1 text-sm">
                Create one above to start a context-driven interview, then score
                it and get a recommendation.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
