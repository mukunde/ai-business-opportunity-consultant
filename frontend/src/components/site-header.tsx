"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { LanguageToggle } from "@/components/language-toggle";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const t = useT();
  const pathname = usePathname();
  const nav = [
    { href: "/", label: t("Dashboard") },
    { href: "/portfolio", label: t("Portfolio") },
  ];

  return (
    <header className="bg-card/80 supports-[backdrop-filter]:bg-card/60 sticky top-0 z-30 border-b backdrop-blur">
      <div className="flex h-14 items-center gap-5 px-6">
        <Link href="/" className="flex items-baseline gap-2.5">
          <Image src="/logo.png" alt="Alfred AI" width={26} height={30} priority />
          <span
            className="text-base font-semibold tracking-tight"
            style={{ fontFamily: "var(--font-space-grotesk)" }}
          >
            Alfred AI
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {nav.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-2.5 py-1 transition-colors",
                  active
                    ? "bg-muted text-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto">
          <LanguageToggle />
        </div>
      </div>
    </header>
  );
}
