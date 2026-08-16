"""Configurações da aplicação, carregadas de variáveis de ambiente ou de um arquivo .env.

Usar pydantic-settings aqui garante duas coisas importantes:
1. "Fail fast": se GROQ_API_KEY não estiver definida, a aplicação falha ao subir
   (em vez de falhar de forma confusa na primeira requisição de um usuário real).
2. Validação de tipos: valores numéricos/booleanos vindos do .env são convertidos
   e validados automaticamente.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Groq (IA) ---
    groq_api_key: str
    # openai/gpt-oss-20b é o substituto recomendado pelo Groq para o antigo
    # llama-3.1-8b-instant (desativado em 16/08/2026) e suporta Structured
    # Outputs em modo estrito: https://console.groq.com/docs/deprecations
    groq_model: str = "openai/gpt-oss-20b"
    groq_temperature: float = 0.5
    groq_timeout_seconds: float = 15.0

    # --- Nominatim (OpenStreetMap) ---
    # Política de uso (LEIA ANTES DE ALTERAR): https://operations.osmfoundation.org/policies/nominatim/
    # Máximo de 1 requisição/segundo, User-Agent identificável e cache obrigatório.
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    nominatim_contact_email: str = "contato@humanizymed.com.br"
    nominatim_timeout_seconds: float = 10.0
    nominatim_cache_ttl_seconds: int = 3600

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- Aplicação ---
    app_name: str = "Humanizy Med"
    app_version: str = "0.2.0"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def montar_lista_cors(cls, valor: object) -> object:
        """Permite CORS_ORIGINS=http://a.com,http://b.com no .env, além de listas JSON."""
        if isinstance(valor, str):
            return [origem.strip() for origem in valor.split(",") if origem.strip()]
        return valor


settings = Settings()
