import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-20 text-center">
      <p className="text-5xl font-semibold text-gold">404</p>
      <p className="mt-3 text-text-2">Cette page n&apos;existe pas, ou ce marché n&apos;est plus suivi.</p>
      <Link href="/" className="mt-6 inline-block text-sm text-gold underline underline-offset-2">Retour au tableau de bord</Link>
    </div>
  );
}
