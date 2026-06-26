"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import type { Turn } from "@/lib/api";

function ConsultantTurn({ turn }: { turn: Turn }) {
  const t = useT();
  return (
    <div className="max-w-[85%] space-y-1.5">
      <span className="text-muted-foreground font-mono text-[0.7rem] tracking-wide">
        {t("Consultant · AI")}
      </span>
      <div className="bg-card rounded-lg rounded-tl-sm border px-3.5 py-2.5 text-sm">
        {turn.message}
      </div>
      {turn.reasoning_trace ? (
        <details className="group text-muted-foreground text-xs">
          <summary className="hover:text-foreground cursor-pointer list-none transition-colors">
            {t("Why I'm asking")}
          </summary>
          <p className="border-border mt-1.5 border-l pl-3">
            {turn.reasoning_trace}
          </p>
        </details>
      ) : null}
    </div>
  );
}

function UserTurn({ turn }: { turn: Turn }) {
  return (
    <div className="bg-primary text-primary-foreground ml-auto max-w-[85%] rounded-lg rounded-tr-sm px-3.5 py-2.5 text-sm">
      {turn.message}
    </div>
  );
}

export function ConversationPanel({
  turns,
  completed,
  onSend,
  sending,
}: {
  turns: Turn[];
  completed: boolean;
  onSend: (answer: string) => void;
  sending: boolean;
}) {
  const t = useT();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Keep the scroll pinned to the latest message as the conversation grows.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns.length, sending]);

  const submit = () => {
    const value = draft.trim();
    if (!value || sending) return;
    onSend(value);
    setDraft("");
  };

  return (
    <div className="flex h-full flex-col">
      <div
        className="flex-1 space-y-5 overflow-y-auto pr-1"
        aria-live="polite"
        aria-busy={sending}
      >
        {turns.map((turn) => (
          <div key={turn.created_at + turn.role}>
            {turn.role === "CONSULTANT" ? (
              <ConsultantTurn turn={turn} />
            ) : (
              <UserTurn turn={turn} />
            )}
          </div>
        ))}
        {sending ? (
          <p className="text-muted-foreground text-sm">
            {t("Consultant is thinking…")}
          </p>
        ) : null}
        <div ref={bottomRef} />
      </div>

      <div className="mt-4 border-t pt-4">
        {completed ? (
          <p className="text-muted-foreground text-center text-sm">
            {t(
              "Interview complete. The opportunity is structured and ready to score.",
            )}
          </p>
        ) : (
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              submit();
            }}
          >
            <Textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
                }
              }}
              placeholder={t("Type your answer…")}
              rows={2}
              className={cn("resize-none")}
              disabled={sending}
            />
            <Button type="submit" disabled={!draft.trim() || sending}>
              {t("Send")}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
