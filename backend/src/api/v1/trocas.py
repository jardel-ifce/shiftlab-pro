"""
Router de Trocas de Óleo - ShiftLab Pro.

Endpoints para registro e consulta de trocas de óleo.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.schemas.troca_oleo import (
    ProximasTrocasResponse,
    TrocaOleoCreate,
    TrocaOleoDetailResponse,
    TrocaOleoListResponse,
    TrocaOleoResponse,
    TrocaOleoUpdate,
)
from src.services.troca_service import TrocaOleoService

router = APIRouter(prefix="/trocas", tags=["Trocas de Óleo"])


def get_service(db: AsyncSession = Depends(get_db)) -> TrocaOleoService:
    """Injeta o serviço de trocas."""
    return TrocaOleoService(db)


@router.get(
    "",
    response_model=TrocaOleoListResponse,
    summary="Listar trocas",
    description="Retorna lista de trocas de óleo com filtros."
)
async def listar_trocas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    veiculo_id: int | None = Query(None, description="Filtrar por veículo"),
    cliente_id: int | None = Query(None, description="Filtrar por cliente"),
    data_inicio: date | None = Query(None, description="Data inicial"),
    data_fim: date | None = Query(None, description="Data final"),
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service)
) -> TrocaOleoListResponse:
    """Lista trocas com filtros."""
    return await service.get_all(
        skip=skip,
        limit=limit,
        veiculo_id=veiculo_id,
        cliente_id=cliente_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@router.get(
    "/proximas",
    response_model=list[ProximasTrocasResponse],
    summary="Próximas trocas",
    description="Lista veículos que precisam de troca em breve."
)
async def proximas_trocas(
    dias_alerta: int = Query(30, ge=1, le=365, description="Dias de antecedência"),
    km_alerta: int = Query(1000, ge=100, le=10000, description="KM de antecedência"),
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service)
) -> list[ProximasTrocasResponse]:
    """Lista veículos que precisam de troca."""
    return await service.get_proximas_trocas(
        dias_alerta=dias_alerta,
        km_alerta=km_alerta
    )


@router.get(
    "/estatisticas",
    summary="Estatísticas",
    description="Retorna estatísticas de trocas realizadas."
)
async def estatisticas(
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service)
) -> dict:
    """Retorna estatísticas de trocas."""
    return await service.get_estatisticas(
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@router.get(
    "/veiculo/{veiculo_id}",
    response_model=list[TrocaOleoResponse],
    summary="Histórico do veículo",
    description="Retorna histórico de trocas de um veículo."
)
async def historico_veiculo(
    veiculo_id: int,
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service)
) -> list[TrocaOleoResponse]:
    """Histórico de trocas de um veículo."""
    trocas = await service.get_by_veiculo(veiculo_id)
    return [TrocaOleoResponse.model_validate(t) for t in trocas]


@router.get(
    "/{troca_id}",
    response_model=TrocaOleoDetailResponse,
    summary="Obter troca",
    description="Retorna dados detalhados de uma troca."
)
async def obter_troca(
    troca_id: int,
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service)
) -> TrocaOleoDetailResponse:
    """Busca troca por ID."""
    troca = await service.get_by_id(troca_id)
    if not troca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Troca não encontrada"
        )
    return TrocaOleoDetailResponse.model_validate(troca)


@router.post(
    "",
    response_model=TrocaOleoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar troca",
    description="Registra uma nova troca de óleo."
)
async def registrar_troca(
    data: TrocaOleoCreate,
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> TrocaOleoResponse:
    """Registra uma nova troca."""
    try:
        user_id = user.id if user else None
        troca = await service.create(data, user_id=user_id)
        await db.commit()
        return TrocaOleoResponse.model_validate(troca)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{troca_id}",
    response_model=TrocaOleoResponse,
    summary="Atualizar troca",
    description="Atualiza dados de uma troca existente."
)
async def atualizar_troca(
    troca_id: int,
    data: TrocaOleoUpdate,
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> TrocaOleoResponse:
    """Atualiza uma troca."""
    try:
        troca = await service.update(troca_id, data)
        await db.commit()
        return TrocaOleoResponse.model_validate(troca)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{troca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover troca",
    description="Remove uma troca (não recomendado - perde histórico)."
)
async def remover_troca(
    troca_id: int,
    user: CurrentActiveUser = None,
    service: TrocaOleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove uma troca."""
    try:
        await service.delete(troca_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
