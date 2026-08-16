"""Modelos Pydantic de entrada e saída do endpoint /chat."""

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensagem do usuário descrevendo os sintomas.",
    )
    cidade: str | None = Field(
        default=None,
        max_length=100,
        description="Cidade para busca de especialistas próximos (opcional).",
    )

    @field_validator("message")
    @classmethod
    def mensagem_nao_pode_ser_vazia(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("A mensagem não pode ser vazia.")
        return valor

    @field_validator("cidade")
    @classmethod
    def normalizar_cidade(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        valor = valor.strip()
        return valor or None


class Local(BaseModel):
    nome: str
    lat: str | None = None
    lng: str | None = None
    endereco: str | None = None


class ChatResponse(BaseModel):
    mensagem: str
    especialista: str
    emergencia: bool = False
    locais: list[Local] = []
