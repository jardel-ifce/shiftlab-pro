"""
API v1 - Endpoints do ShiftLab Pro.

Routers disponíveis:
- clientes: CRUD de clientes
- veiculos: CRUD de veículos
- oleos: CRUD de óleos/produtos
- pecas: CRUD de peças/itens auxiliares
- trocas: Registro de trocas de óleo
- catalogo: Catálogo de montadoras e modelos
- filtros: CRUD de filtros de óleo
"""

from src.api.v1.catalogo import router as catalogo_router
from src.api.v1.clientes import router as clientes_router
from src.api.v1.financeiro import router as financeiro_router
from src.api.v1.filtros import router as filtros_router
from src.api.v1.oleos import router as oleos_router
from src.api.v1.pecas import router as pecas_router
from src.api.v1.retiradas import router as retiradas_router
from src.api.v1.servicos import router as servicos_router
from src.api.v1.trocas import router as trocas_router
from src.api.v1.veiculos import router as veiculos_router

__all__ = [
    "catalogo_router",
    "clientes_router",
    "financeiro_router",
    "filtros_router",
    "veiculos_router",
    "oleos_router",
    "pecas_router",
    "retiradas_router",
    "servicos_router",
    "trocas_router",
]
