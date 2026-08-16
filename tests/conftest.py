"""Configuração compartilhada dos testes.

Define uma GROQ_API_KEY fake ANTES de qualquer import de app.*, já que
app.config.Settings valida a variável de ambiente na importação (fail-fast).
"""

import os

os.environ.setdefault("GROQ_API_KEY", "chave-fake-para-testes")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
