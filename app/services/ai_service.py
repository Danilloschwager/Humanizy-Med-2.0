"""Camada de integração com a IA (Groq) responsável pela triagem inicial.

Em vez de pedir uma resposta em texto livre e depois "adivinhar" o especialista
com busca de substring (abordagem original, frágil — ver docs/ARQUITETURA.md),
usamos o recurso de Structured Outputs do Groq em modo estrito: o próprio
modelo é obrigado, por decodificação restrita, a retornar um JSON que já vem
com a mensagem ao paciente, o especialista (dentro de um enum fechado) e um
sinalizador de emergência. Isso elimina uma classe inteira de bugs de
parsing e é suportado nativamente por openai/gpt-oss-20b e openai/gpt-oss-120b.
Docs: https://console.groq.com/docs/structured-outputs
"""

import json
import logging
from typing import NamedTuple

from groq import AsyncGroq, GroqError

from app.config import settings
from app.constants import ESPECIALISTA_PADRAO, ESPECIALISTAS
from app.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_cliente = AsyncGroq(api_key=settings.groq_api_key, timeout=settings.groq_timeout_seconds)

_RESPOSTA_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "triagem_medica",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "mensagem": {
                    "type": "string",
                    "description": (
                        "Resposta acolhedora ao paciente, em português, sem diagnósticos "
                        "nem prescrições, orientando a buscar o especialista indicado."
                    ),
                },
                "especialista": {
                    "type": "string",
                    "enum": ESPECIALISTAS,
                    "description": "Tipo de especialista mais adequado aos sintomas relatados.",
                },
                "emergencia": {
                    "type": "boolean",
                    "description": (
                        "true se os sintomas relatados sugerirem risco imediato à saúde e "
                        "exigirem atendimento de emergência."
                    ),
                },
            },
            "required": ["mensagem", "especialista", "emergencia"],
            "additionalProperties": False,
        },
    },
}


class AIServiceError(Exception):
    """Erro ao comunicar com o serviço de IA (rede, autenticação, limite de taxa, etc.)."""


class RespostaTriagem(NamedTuple):
    mensagem: str
    especialista: str
    emergencia: bool


async def gerar_resposta(mensagem_usuario: str) -> RespostaTriagem:
    """Envia a mensagem do usuário ao modelo e retorna a triagem já estruturada.

    Levanta AIServiceError se a chamada falhar (rede, autenticação, limite de
    taxa) ou se, por algum motivo, a resposta não puder ser interpretada.
    """
    try:
        resposta = await _cliente.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensagem_usuario},
            ],
            temperature=settings.groq_temperature,
            response_format=_RESPOSTA_SCHEMA,
        )
    except GroqError as exc:
        logger.warning("Falha ao consultar o Groq: %s", exc)
        raise AIServiceError(str(exc)) from exc

    conteudo = resposta.choices[0].message.content or "{}"

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        logger.error("Resposta da IA não é um JSON válido: %r", conteudo)
        raise AIServiceError("Resposta da IA em formato inesperado.") from exc

    return RespostaTriagem(
        mensagem=dados.get("mensagem", "").strip(),
        especialista=dados.get("especialista") or ESPECIALISTA_PADRAO,
        emergencia=bool(dados.get("emergencia", False)),
    )
