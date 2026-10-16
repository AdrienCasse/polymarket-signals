"""Le client HTTP est le seul point de sortie réseau : ses garde-fous sont testés un par un."""

from __future__ import annotations

import httpx
import pytest
import respx

from polysignals.config import Settings
from polysignals.http import HostNotAllowedError, ReadOnlyClient, ReadOnlyClientError

GAMMA = "https://gamma-api.polymarket.com"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("polysignals.http.time.sleep", lambda _s: None)


def test_refuses_hosts_outside_allowlist(settings: Settings) -> None:
    with ReadOnlyClient(settings) as client, pytest.raises(HostNotAllowedError):
        client.get_json("https://evil.example.com/events")


def test_refuses_plain_http(settings: Settings) -> None:
    with ReadOnlyClient(settings) as client, pytest.raises(HostNotAllowedError):
        client.get_json("http://gamma-api.polymarket.com/events")


def test_only_get_is_exposed() -> None:
    public = {n for n in dir(ReadOnlyClient) if not n.startswith("_")}
    assert public == {"get_json"}


@respx.mock
def test_retries_on_429_then_succeeds(settings: Settings) -> None:
    route = respx.get(f"{GAMMA}/events").mock(
        side_effect=[
            httpx.Response(429, headers={"retry-after": "1"}),
            httpx.Response(200, json=[]),
        ]
    )
    with ReadOnlyClient(settings) as client:
        assert client.get_json(f"{GAMMA}/events") == []
    assert route.call_count == 2


@respx.mock
def test_gives_up_after_max_retries(settings: Settings) -> None:
    route = respx.get(f"{GAMMA}/events").mock(return_value=httpx.Response(503))
    with ReadOnlyClient(settings) as client, pytest.raises(ReadOnlyClientError, match="503"):
        client.get_json(f"{GAMMA}/events")
    assert route.call_count == settings.max_retries + 1


@respx.mock
def test_does_not_follow_redirects(settings: Settings) -> None:
    respx.get(f"{GAMMA}/events").mock(
        return_value=httpx.Response(302, headers={"location": "https://ailleurs.example/"})
    )
    with (
        ReadOnlyClient(settings) as client,
        pytest.raises(ReadOnlyClientError, match="Redirection"),
    ):
        client.get_json(f"{GAMMA}/events")


@respx.mock
def test_caps_response_size(settings: Settings) -> None:
    small = settings.model_copy(update={"max_response_bytes": 10})
    respx.get(f"{GAMMA}/events").mock(
        return_value=httpx.Response(200, content=b"[" + b"1," * 50 + b"1]")
    )
    with ReadOnlyClient(small) as client, pytest.raises(ReadOnlyClientError, match="volumineuse"):
        client.get_json(f"{GAMMA}/events")


@respx.mock
def test_client_errors_are_not_retried(settings: Settings) -> None:
    route = respx.get(f"{GAMMA}/events").mock(return_value=httpx.Response(404))
    with ReadOnlyClient(settings) as client, pytest.raises(ReadOnlyClientError, match="404"):
        client.get_json(f"{GAMMA}/events")
    assert route.call_count == 1
