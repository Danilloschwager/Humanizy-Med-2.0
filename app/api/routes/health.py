"""Rota de verificação de disponibilidade do serviço."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Usado por load balancers, orquestradores (Docker/K8s) e uptime checks."""
    return {"status": "ok"}
