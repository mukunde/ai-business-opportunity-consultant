"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { ContextStatusPanel } from "@/components/cockpit/context-status-panel";
import { ConversationPanel } from "@/components/cockpit/conversation-panel";
import { OpportunityModelPanel } from "@/components/cockpit/opportunity-model-panel";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useT } from "@/lib/i18n";
import { ApiError, api } from "@/lib/api";

export function Cockpit({ opportunityId }: { opportunityId: string }) {
  const t = useT();
  const queryClient = useQueryClient();

  const interview = useQuery({
    queryKey: ["interview", opportunityId],
    queryFn: () => api.getInterview(opportunityId),
    retry: false,
  });
  const context = useQuery({
    queryKey: ["context", opportunityId],
    queryFn: () => api.getContext(opportunityId),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["interview", opportunityId] });
    void queryClient.invalidateQueries({ queryKey: ["context", opportunityId] });
    void queryClient.invalidateQueries({ queryKey: ["opportunity", opportunityId] });
  };

  const start = useMutation({
    mutationFn: (message: string) => api.startInterview(opportunityId, message),
    onSuccess: invalidate,
    onError: (e) =>
      toast.error(e instanceof ApiError ? e.message : "Could not start"),
  });
  const answer = useMutation({
    mutationFn: (text: string) => api.continueInterview(opportunityId, text),
    onSuccess: invalidate,
    onError: (e) =>
      toast.error(e instanceof ApiError ? e.message : "Could not send"),
  });

  if (interview.isLoading) {
    return <Skeleton className="h-[70vh] w-full" />;
  }

  const notStarted =
    interview.isError &&
    interview.error instanceof ApiError &&
    interview.error.status === 404;

  if (notStarted) {
    return <StartInterview pending={start.isPending} onStart={start.mutate} />;
  }

  if (interview.isError || !interview.data) {
    return (
      <p className="text-destructive text-sm" role="alert">
        {t("Could not load the interview. Is the API running?")}
      </p>
    );
  }

  const session = interview.data;
  const nodes = context.data?.nodes ?? [];

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(190px,22%)_1fr_minmax(210px,28%)]">
      <aside className="bg-card order-2 rounded-xl border p-5 lg:order-1 lg:sticky lg:top-20 lg:self-start">
        <ContextStatusPanel
          completeness={context.data?.completeness ?? null}
          nodes={nodes}
        />
      </aside>

      <section className="bg-card order-1 flex h-[72vh] flex-col rounded-xl border p-5 lg:order-2">
        <h2 className="text-muted-foreground mb-4 shrink-0 text-xs font-medium tracking-wide uppercase">
          {t("Conversation")}
        </h2>
        <div className="min-h-0 flex-1">
          <ConversationPanel
            turns={session.turns}
            completed={session.status === "COMPLETED"}
            onSend={answer.mutate}
            sending={answer.isPending}
          />
        </div>
      </section>

      <aside className="bg-card order-3 rounded-xl border p-5 lg:sticky lg:top-20 lg:self-start">
        <OpportunityModelPanel nodes={nodes} />
      </aside>
    </div>
  );
}

function StartInterview({
  pending,
  onStart,
}: {
  pending: boolean;
  onStart: (message: string) => void;
}) {
  const t = useT();
  const [message, setMessage] = useState("");
  return (
    <div className="bg-card mx-auto max-w-xl rounded-xl border p-6">
      <h2 className="font-semibold">
        {t("Start the qualification interview")}
      </h2>
      <p className="text-muted-foreground mt-1 text-sm">
        {t(
          "Describe the idea or problem in your own words. The consultant will ask adaptive questions to build the context.",
        )}
      </p>
      <form
        className="mt-4 space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (message.trim()) onStart(message.trim());
        }}
      >
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={3}
          placeholder={t("We receive too many customer support emails…")}
          required
        />
        <Button type="submit" disabled={!message.trim() || pending}>
          {pending ? t("Starting…") : t("Start interview")}
        </Button>
      </form>
    </div>
  );
}
