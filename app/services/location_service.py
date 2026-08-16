"""Camada de integração com o Nominatim (geocodificação via OpenStreetMap).

IMPORTANTE — leia antes de alterar este arquivo:
A API pública do Nominatim roda em servidores doados e tem política de uso
restritiva: no máximo 1 requisição/segundo, User-Agent identificável
obrigatório e cache dos resultados do seu lado.
Política completa: https://operations.osmfoundation.org/policies/nominatim/

Este serviço faz, no máximo, uma requisição por mensagem de chat (nunca em
loop/lote), o que já está dentro do uso "disparado pelo usuário final"
permitido pela política. Para reduzir ainda mais a carga no serviço público
(e a chance de bloqueio por excesso de uso), os resultados são cacheados em
memória por um tempo configurável. Esse cache é por processo: em produção
com múltiplos workers, substitua por um cache compartilhado (Redis, por
exemplo) — ver docs/ARQUITETURA.md.
"""

import logging
import time

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# cache muito simples: chave -> (timestamp_monotonico, resultados)
_cache: dict[str, tuple[float, list[dict]]] = {}


class LocationServiceError(Exception):
    """Erro ao consultar o serviço de geolocalização."""


def _chave_cache(tipo: str, cidade: str) -> str:
    return f"{tipo.strip().lower()}::{cidade.strip().lower()}"


async def buscar_especialistas(tipo: str, cidade: str) -> list[dict]:
    """Busca profissionais/clínicas do tipo informado na cidade informada."""
    chave = _chave_cache(tipo, cidade)
    em_cache = _cache.get(chave)
    if em_cache is not None:
        salvo_em, resultados = em_cache
        if (time.monotonic() - salvo_em) < settings.nominatim_cache_ttl_seconds:
            logger.debug("Cache hit para '%s'", chave)
            return resultados

    params = {
        "q": f"{tipo} {cidade}",
        "format": "json",
        "limit": 5,
        "addressdetails": 1,
    }
    headers = {
        "User-Agent": f"{settings.app_name}/{settings.app_version} ({settings.nominatim_contact_email})"
    }

    try:
        async with httpx.AsyncClient(timeout=settings.nominatim_timeout_seconds) as client:
            resposta = await client.get(settings.nominatim_url, params=params, headers=headers)
            resposta.raise_for_status()
            dados = resposta.json()
    except httpx.HTTPError as exc:
        logger.warning("Falha ao consultar o Nominatim: %s", exc)
        raise LocationServiceError(str(exc)) from exc

    resultados = [
        {
            "nome": lugar.get("display_name", "Nome não disponível"),
            "lat": lugar.get("lat"),
            "lng": lugar.get("lon"),
            "endereco": lugar.get("display_name"),
        }
        for lugar in dados
    ]

    _cache[chave] = (time.monotonic(), resultados)
    return resultados
