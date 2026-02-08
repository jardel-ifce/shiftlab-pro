"""
API v1 - Endpoints do ShiftLab Pro.

Routers disponíveis:
- clientes: CRUD de clientes
- veiculos: CRUD de veículos
- oleos: CRUD de óleos/produtos
- pecas: CRUD de peças/itens auxiliares
- trocas: Registro de trocas de óleo
"""

from src.api.v1.clientes import router as clientes_router
from src.api.v1.oleos import router as oleos_router
from src.api.v1.pecas import router as pecas_router
from src.api.v1.servicos import router as servicos_router
from src.api.v1.trocas import router as trocas_router
from src.api.v1.veiculos import router as veiculos_router

__all__ = [
    "clientes_router",
    "veiculos_router",
    "oleos_router",
    "pecas_router",
    "servicos_router",
    "trocas_router",
]
