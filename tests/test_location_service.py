import httpx
import pytest

from app.services import location_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeAsyncClient:
    """Substitui httpx.AsyncClient nos testes, sem bater na rede de verdade."""

    def __init__(self, payload, *args, **kwargs):
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, *args, **kwargs):
        return _FakeResponse(self._payload)


class _FakeAsyncClientComErro:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, *args, **kwargs):
        raise httpx.ConnectTimeout("timeout simulado")


@pytest.fixture(autouse=True)
def limpar_cache():
    location_service._cache.clear()
    yield
    location_service._cache.clear()


async def test_buscar_especialistas_retorna_lista_formatada(monkeypatch):
    payload = [
        {"display_name": "Clínica Exemplo, Rua X, Natal", "lat": "-5.79", "lon": "-35.21"}
    ]
    monkeypatch.setattr(location_service.httpx, "AsyncClient", lambda *a, **k: _FakeAsyncClient(payload))

    resultados = await location_service.buscar_especialistas("dermatologista", "Natal")

    assert len(resultados) == 1
    assert resultados[0]["nome"] == "Clínica Exemplo, Rua X, Natal"
    assert resultados[0]["lat"] == "-5.79"
    assert resultados[0]["lng"] == "-35.21"


async def test_buscar_especialistas_usa_cache_na_segunda_chamada(monkeypatch):
    payload = [{"display_name": "Clínica A", "lat": "1", "lon": "2"}]
    chamadas = {"n": 0}

    def fabrica(*args, **kwargs):
        chamadas["n"] += 1
        return _FakeAsyncClient(payload)

    monkeypatch.setattr(location_service.httpx, "AsyncClient", fabrica)

    await location_service.buscar_especialistas("pediatra", "Natal")
    await location_service.buscar_especialistas("pediatra", "Natal")

    assert chamadas["n"] == 1  # segunda chamada veio do cache, não bateu na rede


async def test_buscar_especialistas_levanta_erro_em_falha_http(monkeypatch):
    monkeypatch.setattr(location_service.httpx, "AsyncClient", _FakeAsyncClientComErro)

    with pytest.raises(location_service.LocationServiceError):
        await location_service.buscar_especialistas("urologista", "Natal")
