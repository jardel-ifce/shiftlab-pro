"""
Serviço de integração com a API FIPE (Tabela FIPE) - ShiftLab Pro.

Utiliza a API pública parallelum (https://fipe.parallelum.com.br/api/v2)
para consultar marcas, modelos e anos de veículos.

Cache em memória com TTL de 24h para minimizar chamadas
(limite gratuito: 500 req/dia sem token).
"""

import time
from typing import Any

import httpx

FIPE_BASE_URL = "https://fipe.parallelum.com.br/api/v2"
CACHE_TTL = 86400  # 24 horas em segundos
HTTP_TIMEOUT = 15.0  # segundos

# Cache em memória: { chave: (timestamp, dados) }
_cache: dict[str, tuple[float, Any]] = {}


def _get_cached(key: str) -> Any | None:
    """Retorna dados do cache se ainda válidos."""
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cached(key: str, data: Any) -> None:
    """Armazena dados no cache."""
    _cache[key] = (time.time(), data)


async def fipe_get_marcas() -> list[dict]:
    """
    Lista todas as marcas de carros da FIPE.

    Retorna: [{"code": "59", "name": "CHEVROLET"}, ...]
    """
    cache_key = "fipe:marcas"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(f"{FIPE_BASE_URL}/cars/brands")
        resp.raise_for_status()
        data = resp.json()

    _set_cached(cache_key, data)
    return data


async def fipe_get_modelos(marca_code: str) -> list[dict]:
    """
    Lista modelos de uma marca da FIPE.

    Retorna: [{"code": "4828", "name": "COROLLA XEI 2.0 FLEX 16V AUT."}, ...]
    """
    cache_key = f"fipe:modelos:{marca_code}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(f"{FIPE_BASE_URL}/cars/brands/{marca_code}/models")
        resp.raise_for_status()
        data = resp.json()

    _set_cached(cache_key, data)
    return data


async def fipe_get_anos(marca_code: str, modelo_code: str) -> list[dict]:
    """
    Lista anos disponíveis de um modelo da FIPE.

    Retorna: [{"code": "2024-1", "name": "2024 Gasolina"}, ...]
    """
    cache_key = f"fipe:anos:{marca_code}:{modelo_code}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(
            f"{FIPE_BASE_URL}/cars/brands/{marca_code}/models/{modelo_code}/years"
        )
        resp.raise_for_status()
        data = resp.json()

    _set_cached(cache_key, data)
    return data
