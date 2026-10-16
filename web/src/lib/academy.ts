import "server-only";

import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";

/** Les leçons vivent dans `academy/*.md` (source unique, lisible aussi sur GitHub et Obsidian). */
const DIR = path.join(process.cwd(), "..", "academy");

export interface Lesson {
  slug: string;
  number: string;
  title: string;
  summary: string;
  body: string;
}

export function getLessons(): Lesson[] {
  return readdirSync(DIR)
    .filter((f) => /^\d{2}-.+\.md$/.test(f))
    .sort()
    .map((file) => {
      const body = readFileSync(path.join(DIR, file), "utf8");
      const heading = body.match(/^#\s+(.+)$/m)?.[1] ?? file;
      const [number, ...rest] = heading.split(" · ");
      const firstParagraph = body
        .split(/\n\s*\n/)
        .map((b) => b.trim())
        .find((b) => b && !b.startsWith("#") && !b.startsWith("```") && !b.startsWith("|"));
      return {
        slug: file.replace(/\.md$/, ""),
        number: rest.length ? number!.trim() : file.slice(0, 2),
        title: rest.length ? rest.join(" · ").trim() : heading,
        summary: (firstParagraph ?? "").replace(/[*`]/g, "").replace(/\s+/g, " "),
        body,
      };
    });
}

export function getLesson(slug: string): Lesson | undefined {
  return getLessons().find((l) => l.slug === slug);
}
