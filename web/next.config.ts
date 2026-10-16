import type { NextConfig } from "next";

// Site 100 % statique (GitHub Pages) : aucun serveur, aucune API, aucune donnée à l'exécution.
// Le chemin de base vaut "/<dépôt>" sur GitHub Pages, "" en local.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const config: NextConfig = {
  output: "export",
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
  reactStrictMode: true,
};

export default config;
