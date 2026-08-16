import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from groq import APIConnectionError

from app.services import ai_service


def _resposta_fake(payload: dict):
    """Imita o formato choices[0].message.content devolvido pelo SDK do Groq."""
    mensagem = SimpleNamespace(content=json.dumps(payload))
    escolha = SimpleNamespace(message=mensagem)
    return SimpleNamespace(choices=[escolha])


async def test_gerar_resposta_retorna_triagem_estruturada():
    payload = {
        "mensagem": "Procure um dermatologista.",
        "especialista": "dermatologista",
        "emergencia": False,
    }
    mock_create = AsyncMock(return_value=_resposta_fake(payload))

    with patch.object(ai_service._cliente.chat.completions, "create", new=mock_create):
        triagem = await ai_service.gerar_resposta("Estou com manchas na pele")

    assert triagem.mensagem == "Procure um dermatologista."
    assert triagem.especialista == "dermatologista"
    assert triagem.emergencia is False
    # garante que o schema estrito foi realmente enviado ao Groq
    _, kwargs = mock_create.call_args
    assert kwargs["response_format"]["json_schema"]["strict"] is True


async def test_gerar_resposta_marca_emergencia():
    payload = {
        "mensagem": "Procure ajuda imediatamente.",
        "especialista": "cardiologista",
        "emergencia": True,
    }
    mock_create = AsyncMock(return_value=_resposta_fake(payload))

    with patch.object(ai_service._cliente.chat.completions, "create", new=mock_create):
        triagem = await ai_service.gerar_resposta("Dor forte no peito e falta de ar")

    assert triagem.emergencia is True
    assert triagem.especialista == "cardiologista"


async def test_gerar_resposta_usa_especialista_padrao_se_ausente():
    payload = {"mensagem": "Beba água e descanse.", "emergencia": False}
    mock_create = AsyncMock(return_value=_resposta_fake(payload))

    with patch.object(ai_service._cliente.chat.completions, "create", new=mock_create):
        triagem = await ai_service.gerar_resposta("Estou me sentindo cansado")

    assert triagem.especialista == "clínico geral"


async def test_gerar_resposta_propaga_erro_de_conexao_como_ai_service_error():
    erro = APIConnectionError(request=httpx.Request("POST", "https://api.groq.com"))
    mock_create = AsyncMock(side_effect=erro)

    with patch.object(ai_service._cliente.chat.completions, "create", new=mock_create), pytest.raises(
        ai_service.AIServiceError
    ):
        await ai_service.gerar_resposta("Mensagem qualquer")


async def test_gerar_resposta_levanta_erro_se_conteudo_nao_for_json():
    mensagem = SimpleNamespace(content="isso não é um JSON")
    escolha = SimpleNamespace(message=mensagem)
    resposta_invalida = SimpleNamespace(choices=[escolha])
    mock_create = AsyncMock(return_value=resposta_invalida)

    with patch.object(ai_service._cliente.chat.completions, "create", new=mock_create), pytest.raises(
        ai_service.AIServiceError
    ):
        await ai_service.gerar_resposta("Mensagem qualquer")
