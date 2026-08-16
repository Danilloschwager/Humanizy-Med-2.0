from unittest.mock import AsyncMock, patch

from app.services.ai_service import AIServiceError, RespostaTriagem
from app.services.location_service import LocationServiceError


async def test_chat_rejeita_mensagem_vazia(client):
    resposta = await client.post("/chat", json={"message": "   "})
    assert resposta.status_code == 422


async def test_chat_retorna_triagem_e_locais(client):
    triagem = RespostaTriagem(mensagem="Procure um dermatologista.", especialista="dermatologista", emergencia=False)
    locais = [{"nome": "Clínica Exemplo", "lat": "-5.79", "lng": "-35.21", "endereco": "Rua Exemplo, 123"}]

    with patch("app.api.routes.chat.ai_service.gerar_resposta", new=AsyncMock(return_value=triagem)), \
         patch("app.api.routes.chat.location_service.buscar_especialistas", new=AsyncMock(return_value=locais)):
        resposta = await client.post("/chat", json={"message": "Estou com manchas na pele", "cidade": "Natal"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["especialista"] == "dermatologista"
    assert corpo["emergencia"] is False
    assert len(corpo["locais"]) == 1


async def test_chat_sem_cidade_nao_busca_locais(client):
    triagem = RespostaTriagem(mensagem="Procure um clínico geral.", especialista="clínico geral", emergencia=False)
    mock_busca = AsyncMock()

    with patch("app.api.routes.chat.ai_service.gerar_resposta", new=AsyncMock(return_value=triagem)), \
         patch("app.api.routes.chat.location_service.buscar_especialistas", new=mock_busca):
        resposta = await client.post("/chat", json={"message": "Estou com dor de cabeça leve"})

    assert resposta.status_code == 200
    assert resposta.json()["locais"] == []
    mock_busca.assert_not_called()


async def test_chat_retorna_502_se_ia_falhar(client):
    with patch("app.api.routes.chat.ai_service.gerar_resposta", new=AsyncMock(side_effect=AIServiceError("falha"))):
        resposta = await client.post("/chat", json={"message": "Estou com febre"})

    assert resposta.status_code == 502


async def test_chat_degrada_graciosamente_se_geolocalizacao_falhar(client):
    triagem = RespostaTriagem(mensagem="Procure um pediatra.", especialista="pediatra", emergencia=False)

    with patch("app.api.routes.chat.ai_service.gerar_resposta", new=AsyncMock(return_value=triagem)), \
         patch(
             "app.api.routes.chat.location_service.buscar_especialistas",
             new=AsyncMock(side_effect=LocationServiceError("indisponível")),
         ):
        resposta = await client.post("/chat", json={"message": "Minha filha está com febre", "cidade": "Natal"})

    # a triagem em si não deve falhar por causa da geolocalização
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["especialista"] == "pediatra"
    assert corpo["locais"] == []
