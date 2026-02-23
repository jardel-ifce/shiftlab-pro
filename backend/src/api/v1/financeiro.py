"""
Router Financeiro - ShiftLab Pro.

Endpoints para visualização de lucro por troca e por produto.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.schemas.troca_oleo import (
    FinanceiroListResponse,
    ProdutoFinanceiroListResponse,
)
from src.services.configuracao_service import ConfiguracaoService
from src.services.despesa_service import DespesaService
from src.services.troca_service import TrocaOleoService

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


def get_service(db: AsyncSession = Depends(get_db)) -> TrocaOleoService:
    return TrocaOleoService(db)


@router.get(
    "",
    response_model=FinanceiroListResponse,
    summary="Lucro por troca",
    description="Retorna dados financeiros com lucro de cada troca.",
)
async def listar_financeiro(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    cliente_id: int | None = Query(None, description="Filtrar por cliente"),
    data_inicio: date | None = Query(None, description="Data início"),
    data_fim: date | None = Query(None, description="Data fim"),
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> FinanceiroListResponse:
    config_service = ConfiguracaoService(db)
    imposto_percentual = await config_service.get_imposto_percentual()

    despesa_service = DespesaService(db)
    despesas_total = await despesa_service.get_total_periodo(
        data_inicio=data_inicio, data_fim=data_fim
    )

    return await service.get_financeiro(
        skip=skip,
        limit=limit,
        cliente_id=cliente_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        imposto_percentual=imposto_percentual,
        despesas_total=despesas_total,
    )


@router.get(
    "/produtos",
    response_model=ProdutoFinanceiroListResponse,
    summary="Lucro por produto",
    description="Retorna dados financeiros unificados de óleos, filtros e peças.",
)
async def listar_produtos_financeiro(
    tipo: str | None = Query(None, description="Filtrar por tipo: oleo, filtro, peca"),
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service),
) -> ProdutoFinanceiroListResponse:
    return await service.get_financeiro_produtos(tipo=tipo)
