"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useT } from "@/lib/i18n";
import { ApiError, api, type DiscoveredOpportunity } from "@/lib/api";

// The context dict is keyed by backend slot slugs; show readable labels instead.
const CONTEXT_LABEL: Record<string, string> = {
  sector: "Sector",
  objectives: "Objectives & KPIs",
  process_name: "Process",
  process_steps: "Process steps",
};

export default function DiscoverySessionPage() {
  const t = useT();
  const router = useRouter();
  const qc = useQueryClient();
  const { id } = useParams<{ id: string }>();
  const [draft, setDraft] = useState("");
  const [label, setLabel] = useState("");
  const [value, setValue] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const session = useQuery({
    queryKey: ["discovery", id],
    queryFn: () => api.getDiscovery(id),
    retry: false,
  });
  const done = session.data?.done ?? false;

  const candidates = useQuery({
    queryKey: ["discovery-candidates", id],
    queryFn: () => api.listDiscoveryCandidates(id),
    enabled: done,
  });

  const onError = (e: unknown) =>
    toast.error(e instanceof ApiError ? e.message : t("Request failed"));
  const refresh = () => {
    void qc.invalidateQueries({ queryKey: ["discovery", id] });
    void qc.invalidateQueries({ queryKey: ["discovery-candidates", id] });
  };

  const answer = useMutation({
    mutationFn: (a: string) => api.continueDiscovery(id, a),
    onSuccess: refresh,
    onError,
  });
  const signal = useMutation({
    mutationFn: () => api.ingestSignal(id, label.trim(), value.trim()),
    onSuccess: () => {
      setLabel("");
      setValue("");
      refresh();
    },
    onError,
  });
  const promote = useMutation({
    mutationFn: (candidateId: string) => api.promoteCandidate(id, candidateId),
    onSuccess: (opp) => router.push(`/opportunities/${opp.id}`),
    onError,
  });

  // Keep the conversation pinned to the latest message as it grows.
  const turnCount = session.data?.turns.length ?? 0;
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turnCount, answer.isPending]);

  if (session.isLoading) {
    return <Skeleton className="h-[60vh] w-full rounded-xl" />;
  }
  if (session.isError || !session.data) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 text-center">
        <p className="text-destructive text-sm" role="alert">
          {t("Discovery session not found.")}
        </p>
        <Link href="/discovery" className={buttonVariants({ variant: "outline" })}>
          {t("New discovery")}
        </Link>
      </div>
    );
  }

  const s = session.data;
  const send = () => {
    const v = draft.trim();
    if (!v || answer.isPending) return;
    answer.mutate(v);
    setDraft("");
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header>
        <Link
          href="/discovery"
          className="text-muted-foreground hover:text-foreground text-sm"
        >
          ← {t("Discovery")}
        </Link>
        <h1 className="mt-1 text-lg font-semibold tracking-tight">{s.title}</h1>
      </header>

      <div className="grid gap-5 lg:grid-cols-[1fr_minmax(260px,32%)]">
        {/* Conversation */}
        <section className="bg-card flex h-[64vh] flex-col rounded-xl border p-5">
          <div className="flex-1 space-y-4 overflow-y-auto pr-1" aria-live="polite">
            {s.turns.map((turn, i) => (
              <div
                key={i}
                className="animate-in fade-in slide-in-from-bottom-2 duration-300 motion-reduce:animate-none"
              >
                {turn.role === "CONSULTANT" ? (
                  <div className="max-w-[85%] space-y-1.5">
                    <span className="text-muted-foreground font-mono text-[0.7rem] tracking-wide">
                      {t("Consultant · AI")}
                    </span>
                    <div className="bg-background rounded-lg rounded-tl-sm border px-3.5 py-2.5 text-sm">
                      {turn.message}
                    </div>
                  </div>
                ) : (
                  <div className="bg-primary text-primary-foreground ml-auto max-w-[85%] rounded-lg rounded-tr-sm px-3.5 py-2.5 text-sm">
                    {turn.message}
                  </div>
                )}
              </div>
            ))}
            {answer.isPending ? (
              <p className="text-muted-foreground text-sm">
                {t("Consultant is thinking…")}
              </p>
            ) : null}
            <div ref={bottomRef} />
          </div>

          <div className="mt-4 border-t pt-4">
            {done ? (
              <p className="text-muted-foreground text-center text-sm">
                {t("Discovery complete. Candidate opportunities are ready.")}
              </p>
            ) : (
              <form
                className="flex items-end gap-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  send();
                }}
              >
                <Textarea
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send();
                    }
                  }}
                  placeholder={t("Type your answer…")}
                  rows={2}
                  className="resize-none"
                  disabled={answer.isPending}
                />
                <Button type="submit" disabled={!draft.trim() || answer.isPending}>
                  {t("Send")}
                </Button>
              </form>
            )}
          </div>
        </section>

        {/* Side: progress, context, pain points, signals */}
        <aside className="bg-card space-y-5 rounded-xl border p-5">
          <div>
            <div className="text-muted-foreground flex items-center justify-between text-xs font-medium tracking-wide uppercase">
              <span>{t("Business context")}</span>
              <span className="font-mono tabular-nums">
                {Math.round(s.completeness * 100)}%
              </span>
            </div>
            <dl className="mt-3 space-y-2">
              {Object.entries(s.context).map(([k, v]) => (
                <div key={k} className="text-sm">
                  <dt className="text-muted-foreground text-xs">
                    {t(CONTEXT_LABEL[k] ?? k)}
                  </dt>
                  <dd className="font-medium">{v}</dd>
                </div>
              ))}
              {Object.keys(s.context).length === 0 ? (
                <p className="text-muted-foreground text-sm">{t("Nothing yet.")}</p>
              ) : null}
            </dl>
          </div>

          <div>
            <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
              {t("Pain points")}
            </h2>
            {s.pain_points.length > 0 ? (
              <ul className="mt-3 space-y-1.5 text-sm">
                {s.pain_points.map((p, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="bg-highlight size-1.5 rounded-full" aria-hidden />
                    {p}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground mt-3 text-sm">{t("None yet.")}</p>
            )}
          </div>

          <div>
            <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
              {t("Signals")}
            </h2>
            {s.signals.length > 0 ? (
              <ul className="text-muted-foreground mt-3 space-y-1 text-xs">
                {s.signals.map((sig, i) => (
                  <li key={i}>
                    <span className="text-foreground font-medium">{sig.label}</span>:{" "}
                    {sig.value}
                  </li>
                ))}
              </ul>
            ) : null}
            <form
              className="mt-3 space-y-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (label.trim() && value.trim()) signal.mutate();
              }}
            >
              <Input
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder={t("Signal label")}
                className="h-8 text-xs"
              />
              <Input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={t("Signal value")}
                className="h-8 text-xs"
              />
              <Button
                type="submit"
                variant="outline"
                size="sm"
                disabled={!label.trim() || !value.trim() || signal.isPending}
              >
                {t("Add signal")}
              </Button>
            </form>
          </div>
        </aside>
      </div>

      {/* Detected opportunities */}
      {done ? (
        <section className="space-y-3">
          <h2 className="text-base font-semibold tracking-tight">
            {t("Detected opportunities")}
          </h2>
          <p className="text-muted-foreground max-w-prose text-sm">
            {t(
              "Promote a candidate to turn it into an opportunity you can qualify and score; once scored it appears in the Portfolio.",
            )}
          </p>
          {candidates.data && candidates.data.length > 0 ? (
            <ul className="space-y-3">
              {candidates.data.map((c: DiscoveredOpportunity) => (
                <li key={c.id} className="bg-card rounded-xl border p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-medium">{c.title}</p>
                      <p className="text-muted-foreground mt-0.5 text-sm">
                        {t("Targets")}: {c.target_pain_point}
                      </p>
                      <p className="text-muted-foreground mt-1 text-sm">
                        {c.rationale}
                      </p>
                    </div>
                    {c.promoted_opportunity_id ? (
                      <Link
                        href={`/opportunities/${c.promoted_opportunity_id}`}
                        className={buttonVariants({ variant: "outline", size: "sm" })}
                      >
                        {t("View opportunity")}
                      </Link>
                    ) : (
                      <Button
                        size="sm"
                        disabled={promote.isPending}
                        onClick={() => promote.mutate(c.id)}
                      >
                        {t("Promote to qualification")}
                      </Button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground text-sm">
              {t("No opportunity candidates were detected.")}
            </p>
          )}
        </section>
      ) : null}
    </div>
  );
}
