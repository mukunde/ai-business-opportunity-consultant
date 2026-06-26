"use client";

import { type Locale, useLocale } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const LOCALES: Locale[] = ["en", "fr"];

export function LanguageToggle() {
  const { locale, setLocale } = useLocale();
  return (
    <div className="ml-auto flex items-center gap-0.5 rounded-md border p-0.5 text-xs font-medium">
      {LOCALES.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLocale(l)}
          aria-pressed={locale === l}
          className={cn(
            "rounded px-2 py-0.5 uppercase transition-colors",
            locale === l
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
