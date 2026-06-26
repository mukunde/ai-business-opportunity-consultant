import type { Metadata } from "next";
import { Fira_Code, Fira_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { SiteHeader } from "@/components/site-header";
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
          <SiteHeader />
          <main className="w-full flex-1 px-6 py-8">{children}</main>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
