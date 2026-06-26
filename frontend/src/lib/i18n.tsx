"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { fr } from "./messages";

export type Locale = "en" | "fr";

const LocaleContext = createContext<{
  locale: Locale;
  setLocale: (l: Locale) => void;
}>({ locale: "en", setLocale: () => {} });

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    // Read the persisted choice only after mount, so SSR and the first client
    // render agree on "en" (no hydration mismatch).
    const saved = localStorage.getItem("locale");
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (saved === "fr" || saved === "en") setLocaleState(saved);
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    try {
      localStorage.setItem("locale", l);
    } catch {
      // ignore storage failures (private mode, etc.)
    }
    document.documentElement.lang = l;
  };

  return (
    <LocaleContext.Provider value={{ locale, setLocale }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocale() {
  return useContext(LocaleContext);
}

/** Returns a translator: `t("English string")` -> localized string. */
export function useT() {
  const { locale } = useContext(LocaleContext);
  return (s: string) => (locale === "fr" ? (fr[s] ?? s) : s);
}
