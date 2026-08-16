"""Rota principal do chatbot: recebe sintomas e devolve triagem + locais próximos."""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ai_service, location_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:

    try:
        triagem = await ai_service.gerar_resposta(request.message)
    except ai_service.AIServiceError:
        logger.exception("Falha ao consultar o serviço de IA")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível processar sua mensagem no momento. Tente novamente em instantes.",
        )

    locais = []
    if request.cidade:
        try:
            locais = await location_service.buscar_especialistas(triagem.especialista, request.cidade)
        except location_service.LocationServiceError:
            logger.warning("Falha ao buscar locais próximos; devolvendo lista vazia")

    return ChatResponse(
        mensagem=triagem.mensagem,
        especialista=triagem.especialista,
        emergencia=triagem.emergencia,
        locais=locais,
    )
