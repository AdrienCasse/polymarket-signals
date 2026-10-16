import type { Metadata } from "next";
import Link from "next/link";

import { getLessons } from "@/lib/academy";

export const metadata: Metadata = { title: "Académie" };

export default function Academy() {
  const lessons = getLessons();
  return (
    <>
      <h1 className="text-3xl font-semibold tracking-tight text-text-1">Académie</h1>
      <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-text-2">
        Sept leçons courtes pour comprendre les marchés prédictifs, et la façon dont ce site les lit. Chacune se
        termine par « À retenir ».
      </p>
      <ol className="mt-8 grid gap-3">
        {lessons.map((l) => (
          <li key={l.slug}>
            <Link
              href={`/academie/${l.slug}/`}
              className="flex gap-4 rounded-[var(--radius-card)] border border-line bg-card p-4 transition-colors hover:border-line-hi hover:bg-hover"
            >
              <span className="tabular text-sm font-medium text-gold">{l.number}</span>
              <span>
                <span className="block text-[15px] font-medium text-text-1">{l.title}</span>
                <span className="mt-1 line-clamp-2 block text-sm text-text-3">{l.summary}</span>
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </>
  );
}
