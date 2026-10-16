import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Markdown } from "@/components/Markdown";
import { SpreadSimulator } from "@/components/SpreadSimulator";
import { getLesson, getLessons } from "@/lib/academy";

export const dynamicParams = false;

// Leçons qui gagnent à être manipulées plutôt que lues
const WITH_SIMULATOR = new Set(["01-prix-probabilite", "02-carnet-ordres-liquidite"]);

export function generateStaticParams() {
  return getLessons().map((l) => ({ slug: l.slug }));
}

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const lesson = getLesson((await params).slug);
  return { title: lesson ? `${lesson.number} · ${lesson.title}` : "Leçon" };
}

export default async function LessonPage({ params }: Props) {
  const { slug } = await params;
  const lessons = getLessons();
  const index = lessons.findIndex((l) => l.slug === slug);
  const lesson = lessons[index];
  if (!lesson) notFound();
  const prev = lessons[index - 1];
  const next = lessons[index + 1];

  return (
    <article className="max-w-2xl">
      <Link href="/academie/" className="text-sm text-text-3 hover:text-text-1">← Académie</Link>
      <p className="mt-6 text-xs font-medium uppercase tracking-wider text-gold">Leçon {lesson.number}</p>
      <h1 className="mt-2 text-3xl font-semibold leading-tight tracking-tight text-text-1">{lesson.title}</h1>
      <div className="mt-8"><Markdown source={lesson.body} /></div>
      {WITH_SIMULATOR.has(lesson.slug) && <div className="mt-10"><SpreadSimulator /></div>}
      <nav className="mt-12 flex justify-between gap-4 border-t border-line pt-6 text-sm" aria-label="Leçons">
        {prev ? <Link href={`/academie/${prev.slug}/`} className="text-text-2 hover:text-gold">← {prev.title}</Link> : <span />}
        {next ? <Link href={`/academie/${next.slug}/`} className="text-right text-text-2 hover:text-gold">{next.title} →</Link> : <span />}
      </nav>
    </article>
  );
}
