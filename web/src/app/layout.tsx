import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";
import type { Metadata } from "next";
import type { ReactNode } from "react";

import { DemoBanner, Footer, Header } from "@/components/Shell";
import { getGold } from "@/lib/data";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: "polysignals · comprendre ce que le monde anticipe", template: "%s · polysignals" },
  description:
    "Lecture pédagogique des marchés prédictifs (Fed, BCE, inflation, récession) : probabilités, fiabilité du signal, biais. Lecture seule, aucun pari.",
  robots: { index: true, follow: true },
};

// Pas de serveur : la CSP passe par <meta>. Aucune ressource externe n'est autorisée.
const CSP = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : ""}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "font-src 'self'",
  "connect-src 'self'",
  "base-uri 'self'",
  "form-action 'none'",
  "object-src 'none'",
].join("; ");

export default function RootLayout({ children }: { children: ReactNode }) {
  const gold = getGold();
  return (
    <html lang="fr" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <head>
        <meta httpEquiv="Content-Security-Policy" content={CSP} />
        <meta name="referrer" content="strict-origin-when-cross-origin" />
      </head>
      <body className="min-h-dvh">
        {gold.source_mode === "fixtures" && <DemoBanner />}
        <Header />
        <main className="mx-auto max-w-5xl px-4 pt-10 sm:px-6">{children}</main>
        <Footer generatedAt={gold.generated_at} />
      </body>
    </html>
  );
}
