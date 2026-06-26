import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Fira_Code, Fira_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";

// Design system (see DESIGN.md): Fira Sans drives the UI; Fira Code is the mono
// used for data and numerics; Space Grotesk is the brand/logo face for the
// "Alfred AI" wordmark.
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

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Alfred AI - AI use-case qualification",
  description:
    "Alfred AI qualifies AI and tech use cases through adaptive interviews, context engineering, scoring and decision-ready recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${firaSans.variable} ${firaCode.variable} ${spaceGrotesk.variable} h-full antialiased`}
    >
      <body className="bg-background text-foreground min-h-full flex flex-col">
        <Providers>
          <header className="bg-card/80 supports-[backdrop-filter]:bg-card/60 sticky top-0 z-30 border-b backdrop-blur">
            <div className="flex h-14 items-center gap-2 px-6">
              <Link href="/" className="flex items-baseline gap-2.5">
                <Image
                  src="/logo.png"
                  alt="Alfred AI"
                  width={23}
                  height={30}
                  priority
                  className="mix-blend-multiply"
                />
                <span
                  className="text-base font-semibold tracking-tight"
                  style={{ fontFamily: "var(--font-space-grotesk)" }}
                >
                  Alfred AI
                </span>
                <span className="text-muted-foreground hidden text-xs sm:inline">
                  · AI use-case qualification
                </span>
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
