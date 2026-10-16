"""Diagnostic réseau : pourquoi Polymarket est-il (in)joignable depuis cette machine ?

En France, Polymarket est bloqué par l'ANJ (Autorité nationale des jeux). Le blocage se fait au
niveau DNS des fournisseurs d'accès : le nom `*.polymarket.com` est résolu vers un serveur de
l'ANJ, qui présente un certificat `*.anj.fr`. Le client HTTP refuse alors la connexion, car le
certificat ne correspond pas au nom demandé. C'est voulu : on ne désactive jamais la
vérification TLS.

Ce module ne contourne rien : il constate et explique.
"""

from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urlsplit

from polysignals.config import Settings


@dataclass(frozen=True)
class HostDiagnosis:
    host: str
    addresses: list[str]
    tls_ok: bool
    detail: str

    @property
    def likely_blocked(self) -> bool:
        return not self.tls_ok and (
            "anj" in self.detail.lower() or "hostname mismatch" in self.detail.lower()
        )


def diagnose(settings: Settings, timeout: float = 5.0) -> list[HostDiagnosis]:
    hosts = sorted(
        {urlsplit(u).hostname or "" for u in (settings.gamma_base_url, settings.clob_base_url)}
    )
    return [_diagnose_host(h, timeout) for h in hosts if h]


def _diagnose_host(host: str, timeout: float) -> HostDiagnosis:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return HostDiagnosis(host, [], False, f"Résolution DNS impossible : {exc}")
    addresses = sorted({str(i[4][0]) for i in infos})

    ctx = ssl.create_default_context()
    try:
        with (
            socket.create_connection((host, 443), timeout=timeout) as sock,
            ctx.wrap_socket(sock, server_hostname=host) as tls,
        ):
            cert = tls.getpeercert() or {}
            subject = dict(x[0] for x in cert.get("subject", ()))  # type: ignore[misc]
            return HostDiagnosis(
                host, addresses, True, f"TLS valide (certificat : {subject.get('commonName')})"
            )
    except ssl.SSLCertVerificationError as exc:
        return HostDiagnosis(host, addresses, False, f"{exc.verify_message} → {_peer_cn(host)}")
    except OSError as exc:
        return HostDiagnosis(host, addresses, False, f"Connexion impossible : {exc}")


def _peer_cn(host: str) -> str:
    """Lit le nom du certificat présenté SANS lui faire confiance (diagnostic uniquement :
    aucune donnée n'est échangée sur cette connexion)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with (
            socket.create_connection((host, 443), timeout=5) as sock,
            ctx.wrap_socket(sock, server_hostname=host) as tls,
        ):
            der = tls.getpeercert(binary_form=True) or b""
    except OSError:
        return "certificat illisible"
    # Extraction minimale du CN sans dépendance : on cherche un nom de domaine connu
    text = der.decode("latin-1")
    for marker in ("anj.fr", "polymarket.com"):
        if marker in text:
            return f"certificat présenté pour *.{marker}"
    return "certificat inattendu"
