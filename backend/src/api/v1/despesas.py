"""Router de Despesas - ShiftLab Pro."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.despesa import (
    DespesaCreate,
    DespesaListResponse,
    DespesaResponse,
    DespesaUpdate,
)
from src.services.despesa_service import DespesaService

router = APIRouter(prefix="/despesas", tags=["Despesas"])


def get_service(db: AsyncSession = Depends(get_db)) -> DespesaService:
    return DespesaService(db)


@router.get("", response_model=DespesaListResponse, summary="Listar despesas")
async def listar_despesas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    categoria: str | None = Query(None),
    user: CurrentActiveUser = None,
    service: DespesaService = Depends(get_service),
) -> DespesaListResponse:
    return await service.get_all(
        skip=skip, limit=limit,
        data_inicio=data_inicio, data_fim=data_fim,
        categoria=categoria,
    )


@router.get("/{despesa_id}", response_model=DespesaResponse, summary="Obter despesa")
async def obter_despesa(
    despesa_id: int,
    user: CurrentActiveUser = None,
    service: DespesaService = Depends(get_service),
) -> DespesaResponse:
    despesa = await service.get_by_id(despesa_id)
    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return DespesaResponse.model_validate(despesa)


@router.post(
    "", response_model=DespesaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar despesa",
)
async def criar_despesa(
    data: DespesaCreate,
    user: CurrentAdminUser = None,
    service: DespesaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> DespesaResponse:
    despesa = await service.create(data)
    await db.commit()
    return DespesaResponse.model_validate(despesa)


@router.patch("/{despesa_id}", response_model=DespesaResponse, summary="Atualizar despesa")
async def atualizar_despesa(
    despesa_id: int,
    data: DespesaUpdate,
    user: CurrentAdminUser = None,
    service: DespesaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> DespesaResponse:
    try:
        despesa = await service.update(despesa_id, data)
        await db.commit()
        return DespesaResponse.model_validate(despesa)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{despesa_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir despesa")
async def excluir_despesa(
    despesa_id: int,
    user: CurrentAdminUser = None,
    service: DespesaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await service.delete(despesa_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
