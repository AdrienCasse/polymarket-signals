"""Client HTTP en lecture seule.

C'est le seul point de sortie réseau du projet. Il garantit par construction :

- **GET uniquement** : aucune méthode ne permet d'écrire (ni ordre, ni signature, ni wallet) ;
- **liste blanche d'hôtes** : impossible d'appeler autre chose que les API publiques prévues ;
- **TLS toujours vérifié** : en France, le DNS des FAI redirige Polymarket vers la page de
  blocage de l'ANJ ; la vérification du certificat est exactement ce qui le détecte ;
- **timeouts, taille de réponse bornée, débit limité, retries avec backoff** sur 429/5xx.
"""

from __future__ import annotations

import json
import logging
import random
import time
from types import TracebackType
from typing import Any, Self
from urllib.parse import urlsplit

import httpx

from polysignals import __version__
from polysignals.config import Settings

log = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class ReadOnlyClientError(RuntimeError):
    """Erreur réseau ou protocole, avec un message actionnable."""


class HostNotAllowedError(ReadOnlyClientError):
    pass


class TLSInterceptionError(ReadOnlyClientError):
    pass


class ReadOnlyClient:
    def __init__(self, settings: Settings, transport: httpx.BaseTransport | None = None) -> None:
        self._settings = settings
        self._allowed_hosts = frozenset(
            urlsplit(u).hostname for u in (settings.gamma_base_url, settings.clob_base_url)
        )
        self._last_request_at = 0.0
        self._client = httpx.Client(
            timeout=settings.timeout_s,
            verify=True,  # jamais désactivé, voir docs/security.md
            follow_redirects=False,  # une redirection pourrait sortir de la liste blanche
            headers={
                # En-têtes HTTP : ASCII uniquement (un accent fait planter httpx)
                "User-Agent": f"polysignals/{__version__} (read-only; educational)",
                "Accept": "application/json",
            },
            transport=transport,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._client.close()

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        host = urlsplit(url).hostname
        if urlsplit(url).scheme != "https" or host not in self._allowed_hosts:
            raise HostNotAllowedError(f"Hôte non autorisé : {url!r}")

        attempt = 0
        while True:
            self._throttle()
            try:
                body = self._fetch(url, params)
            except httpx.ConnectError as exc:
                if "CERTIFICATE_VERIFY_FAILED" in str(exc):
                    raise TLSInterceptionError(
                        f"Certificat TLS invalide pour {host}. En France, c'est le signe de la "
                        "redirection DNS vers la page de blocage de l'ANJ. "
                        "Lance `make doctor` pour le diagnostic."
                    ) from exc
                if attempt >= self._settings.max_retries:
                    raise ReadOnlyClientError(f"Connexion impossible à {host} : {exc}") from exc
            except _RetryableStatusError as exc:
                if attempt >= self._settings.max_retries:
                    raise ReadOnlyClientError(
                        f"{host} répond {exc.status} après {attempt + 1} tentatives"
                    ) from exc
                if exc.retry_after is not None:
                    time.sleep(min(exc.retry_after, 30.0))
            else:
                try:
                    return json.loads(body)
                except json.JSONDecodeError as exc:
                    raise ReadOnlyClientError(f"Réponse non JSON de {host}") from exc

            attempt += 1
            # Backoff exponentiel + jitter : 0.5s, 1s, 2s, 4s (± 25 %)
            delay = 0.5 * 2 ** (attempt - 1) * random.uniform(0.75, 1.25)  # noqa: S311
            log.warning("Nouvelle tentative %s vers %s dans %.1fs", attempt, host, delay)
            time.sleep(delay)

    def _fetch(self, url: str, params: dict[str, Any] | None) -> bytes:
        with self._client.stream("GET", url, params=params) as response:
            if response.status_code in RETRYABLE_STATUS:
                raise _RetryableStatusError(response.status_code, _retry_after(response))
            if response.is_redirect:
                raise ReadOnlyClientError(
                    f"Redirection refusée ({response.status_code}) vers "
                    f"{response.headers.get('location')!r}"
                )
            if response.status_code >= 400:
                raise ReadOnlyClientError(f"HTTP {response.status_code} sur {url}")

            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > self._settings.max_response_bytes:
                    raise ReadOnlyClientError(
                        f"Réponse trop volumineuse (> {self._settings.max_response_bytes} octets)"
                    )
                chunks.append(chunk)
            return b"".join(chunks)

    def _throttle(self) -> None:
        wait = self._settings.min_interval_s - (time.monotonic() - self._last_request_at)
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()


class _RetryableStatusError(Exception):
    def __init__(self, status: int, retry_after: float | None) -> None:
        super().__init__(status)
        self.status = status
        self.retry_after = retry_after


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("retry-after")
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None
