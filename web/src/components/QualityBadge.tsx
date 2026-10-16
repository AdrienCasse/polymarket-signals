import type { SignalQuality } from "@/lib/data";

const STYLES: Record<SignalQuality, { label: string; cls: string; dot: string }> = {
  solide: { label: "Signal solide", cls: "text-teal border-teal/30 bg-teal/10", dot: "bg-teal" },
  fragile: { label: "Signal fragile", cls: "text-amber border-amber/30 bg-amber/10", dot: "bg-amber" },
  inexploitable: { label: "Inexploitable", cls: "text-red border-red/30 bg-red/10", dot: "bg-red" },
};

export function QualityBadge({ quality }: { quality: SignalQuality }) {
  const s = STYLES[quality];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${s.cls}`}>
      <span aria-hidden className={`size-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  );
}
