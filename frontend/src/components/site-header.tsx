"use client";

import Image from "next/image";
import Link from "next/link";

import { LanguageToggle } from "@/components/language-toggle";
import { useT } from "@/lib/i18n";

export function SiteHeader() {
  const t = useT();
  return (
    <header className="bg-card/80 supports-[backdrop-filter]:bg-card/60 sticky top-0 z-30 border-b backdrop-blur">
      <div className="flex h-14 items-center gap-2 px-6">
        <Link href="/" className="flex items-baseline gap-2.5">
          <Image src="/logo.png" alt="Alfred AI" width={26} height={30} priority />
          <span
            className="text-base font-semibold tracking-tight"
            style={{ fontFamily: "var(--font-space-grotesk)" }}
          >
            Alfred AI
          </span>
          <span className="text-muted-foreground hidden text-xs sm:inline">
            · {t("AI use-case qualification")}
          </span>
        </Link>
        <LanguageToggle />
      </div>
    </header>
  );
}
