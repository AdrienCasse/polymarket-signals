"""Contrats de données des API Polymarket (ce qu'on attend de la source).

Ces modèles ne transforment pas les données : la couche bronze stocke toujours la réponse brute.
Ils servent de **contrat** : chaque enregistrement est validé à l'ingestion et le résultat
(`contract_ok`, `contract_errors`) voyage avec lui jusqu'aux tests dbt. Si Polymarket change
son format, on le voit tout de suite au lieu de produire des chiffres faux en silence.

`extra="allow"` : un champ nouveau côté API n'est pas une erreur, un champ attendu manquant
ou mal typé en est une.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


def _json_list(value: Any) -> Any:
    """Gamma encode certaines listes en chaîne JSON : '["Yes","No"]'."""
    if isinstance(value, str):
        return json.loads(value)
    return value


class _Contract(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class GammaTag(_Contract):
    id: str
    slug: str
    label: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def _id_as_str(cls, v: Any) -> Any:
        return str(v) if isinstance(v, int) else v


class GammaMarket(_Contract):
    id: str
    slug: str
    question: str
    condition_id: str = Field(alias="conditionId")
    outcomes: list[str]
    outcome_prices: list[float] = Field(alias="outcomePrices")
    clob_token_ids: list[str] = Field(default_factory=list, alias="clobTokenIds")
    end_date: datetime | None = Field(default=None, alias="endDate")
    active: bool
    closed: bool
    best_bid: float | None = Field(default=None, alias="bestBid", ge=0, le=1)
    best_ask: float | None = Field(default=None, alias="bestAsk", ge=0, le=1)
    last_trade_price: float | None = Field(default=None, alias="lastTradePrice", ge=0, le=1)
    liquidity: float | None = Field(default=None, alias="liquidityNum", ge=0)
    volume: float | None = Field(default=None, alias="volumeNum", ge=0)

    _parse_lists = field_validator("outcomes", "outcome_prices", "clob_token_ids", mode="before")(
        _json_list
    )

    @field_validator("outcome_prices")
    @classmethod
    def _prices_are_probabilities(cls, v: list[float]) -> list[float]:
        if any(not 0.0 <= p <= 1.0 for p in v):
            raise ValueError("un prix d'issue doit être compris entre 0 et 1")
        return v


class GammaEvent(_Contract):
    id: str
    slug: str
    title: str
    end_date: datetime | None = Field(default=None, alias="endDate")
    active: bool
    closed: bool
    tags: list[GammaTag] = Field(default_factory=list)
    markets: list[GammaMarket] = Field(default_factory=list)


class PricePoint(_Contract):
    t: int = Field(gt=0, description="horodatage Unix (secondes)")
    p: float = Field(ge=0, le=1)


class ClobPriceHistory(_Contract):
    history: list[PricePoint]


def check_contract(model: type[BaseModel], payload: Any) -> list[str]:
    """Retourne la liste des violations de contrat (vide si l'enregistrement est conforme)."""
    try:
        model.model_validate(payload)
    except ValidationError as exc:
        return [
            f"{'.'.join(str(p) for p in err['loc']) or '<racine>'}: {err['msg']}"
            for err in exc.errors(include_url=False)
        ][:20]
    return []
