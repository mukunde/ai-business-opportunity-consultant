"use client";

import { useMutation } from "@tanstack/react-query";
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
    </div>
  );
}
