import { isNoise, pts } from "@/lib/format";

/** Variation en points de probabilité. Neutre (gris) sous 3 points : souvent du bruit. */
export function Change({ value, label }: { value: number | null; label?: string }) {
  const tone =
    value == null || isNoise(value) ? "text-text-3" : value > 0 ? "text-teal" : "text-red";
  return (
    <span className={`tabular text-sm ${tone}`} title={isNoise(value) ? "Moins de 3 points : souvent du bruit" : undefined}>
      {pts(value)}
      {label ? <span className="ml-1 text-text-3">{label}</span> : null}
    </span>
  );
}
