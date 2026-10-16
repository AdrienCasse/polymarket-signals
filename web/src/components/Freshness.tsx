"use client";

import { useSyncExternalStore } from "react";

/**
 * Fraîcheur calculée DANS LE NAVIGATEUR : le site est statique, seule la visite connaît l'heure.
 * Au-delà de 48 h sans run réussi, on le dit clairement (pipeline en panne ou en pause).
 */
export function Freshness({ lastSuccessAt }: { lastSuccessAt: string | null }) {
  const now = useSyncExternalStore(subscribe, () => Math.floor(Date.now() / 60_000), () => null);
  if (!lastSuccessAt || now == null) return null;
  const hours = (now * 60_000 - new Date(lastSuccessAt).getTime()) / 3_600_000;
  const stale = hours > 48;
  const label = hours < 1 ? "il y a moins d'une heure" : hours < 48 ? `il y a ${Math.round(hours)} h` : `il y a ${Math.round(hours / 24)} jours`;
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs ${stale ? "text-amber" : "text-text-3"}`}>
      <span aria-hidden className={`size-1.5 rounded-full ${stale ? "bg-amber" : "bg-teal"}`} />
      Dernière mise à jour {label}
      {stale ? " : données possiblement périmées" : ""}
    </span>
  );
}

function subscribe(onChange: () => void) {
  const id = setInterval(onChange, 60_000);
  return () => clearInterval(id);
}
