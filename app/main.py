"""Ponto de entrada da aplicação: cria a app FastAPI e registra middlewares/rotas.

Rodar localmente: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Assistente médico virtual que sugere o especialista ideal com base nos sintomas relatados.",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
