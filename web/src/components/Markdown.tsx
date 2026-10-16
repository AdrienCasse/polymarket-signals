import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { REPO_URL } from "@/lib/site";

/**
 * Rendu des leçons. Les liens vers une autre leçon restent dans le site ; les liens vers le code
 * pointent vers le dépôt GitHub. Le HTML brut n'est pas interprété (react-markdown l'ignore).
 */
export function Markdown({ source }: { source: string }) {
  return (
    <div className="prose-ps">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href = "", children }) => {
            const lesson = href.match(/^(?:\.\.\/academy\/|\.\/)?(\d{2}-[\w-]+)\.md$/);
            if (lesson) return <Link href={`/academie/${lesson[1]}/`}>{children}</Link>;
            if (/^https?:\/\//.test(href)) {
              return <a href={href} rel="noopener noreferrer" target="_blank">{children}</a>;
            }
            return <a href={`${REPO_URL}/blob/main/${href.replace(/^\.\.\//, "")}`} rel="noopener noreferrer" target="_blank">{children}</a>;
          },
          pre: ({ children, node }) => {
            const code = node?.children[0];
            const lang = code && "properties" in code ? String((code.properties.className as string[] | undefined)?.[0] ?? "") : "";
            if (lang === "language-mermaid") return <ArchitectureDiagram />;
            return <pre>{children}</pre>;
          },
          table: ({ children }) => (
            <div className="table-wrap">
              <table>{children}</table>
            </div>
          ),
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  );
}
