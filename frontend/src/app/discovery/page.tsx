"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useT } from "@/lib/i18n";
import { ApiError, api } from "@/lib/api";

export default function DiscoveryStartPage() {
  const t = useT();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");

  const sessions = useQuery({
    queryKey: ["discovery-sessions"],
    queryFn: api.listDiscoverySessions,
  });

  const start = useMutation({
    mutationFn: () => api.startDiscovery(title, message),
    onSuccess: (session) => router.push(`/discovery/${session.id}`),
    onError: (e) =>
      toast.error(e instanceof ApiError ? e.message : t("Request failed")),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <header>
        <h1 className="text-lg font-semibold tracking-tight">
          {t("New discovery")}
        </h1>
        <p className="text-muted-foreground mt-1 max-w-prose text-sm">
          {t(
            "Explore a business or a process to surface AI opportunities, before qualifying them.",
          )}
        </p>
      </header>

      <form
        className="bg-card space-y-4 rounded-xl border p-5 sm:p-6"
        onSubmit={(e) => {
          e.preventDefault();
          if (title.trim() && message.trim()) start.mutate();
        }}
      >
        <div className="space-y-1.5">
          <Label htmlFor="title">{t("What are we exploring?")}</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Service ADV"
            required
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="message">
            {t("Describe the business or process in your own words.")}
          </Label>
          <Textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            placeholder={t("We sell custom kitchens; the sales cycle is long…")}
            required
          />
        </div>
        <Button
          type="submit"
          disabled={!title.trim() || !message.trim() || start.isPending}
        >
          {start.isPending ? t("Starting…") : t("Start discovery")}
        </Button>
      </form>

      {sessions.data && sessions.data.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-sm font-medium">{t("Your discoveries")}</h2>
          <ul className="bg-card divide-y overflow-hidden rounded-xl border">
            {sessions.data.map((s) => (
              <li key={s.id}>
                <Link
                  href={`/discovery/${s.id}`}
                  className="hover:bg-muted/40 group flex items-center justify-between gap-3 px-4 py-3 transition-colors"
                >
                  <span className="group-hover:text-primary font-medium transition-colors">
                    {s.title}
                  </span>
                  <span className="text-muted-foreground flex items-center gap-3 text-xs">
                    <span>{s.done ? t("Completed") : t("Active")}</span>
                    <span className="font-mono tabular-nums">
                      {Math.round(s.completeness * 100)}%
                    </span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
