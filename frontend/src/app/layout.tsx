import type { Metadata } from "next";
import Link from "next/link";
import { Fira_Code, Fira_Sans } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";

// Design system (see DESIGN.md): Fira Sans drives the UI; Fira Code is the
// mono used for data, numerics and the wordmark - a restrained "analytical"
// signal rather than mono everywhere.
const firaSans = Fira_Sans({
  variable: "--font-fira-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const firaCode = Fira_Code({
  variable: "--font-fira-code",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AI Business Opportunity Consultant",
  description:
    "Qualify AI opportunities through adaptive interviews, context engineering, scoring and decision-ready recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${firaSans.variable} ${firaCode.variable} h-full antialiased`}
    >
      <body className="bg-background text-foreground min-h-full flex flex-col">
        <Providers>
          <header className="bg-card/80 supports-[backdrop-filter]:bg-card/60 sticky top-0 z-30 border-b backdrop-blur">
            <div className="flex h-14 items-center gap-2 px-6">
              <Link
                href="/"
                className="flex items-center gap-2 font-mono text-sm font-semibold tracking-tight"
              >
                <span className="bg-primary size-4 rounded-[5px]" aria-hidden />
                opportunity<span className="text-muted-foreground">/consultant</span>
              </Link>
            </div>
          </header>
          <main className="w-full flex-1 px-6 py-8">{children}</main>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
