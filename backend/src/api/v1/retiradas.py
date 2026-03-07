"""Router de Retiradas - ShiftLab Pro."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.retirada import (
    RetiradaCreate,
    RetiradaListResponse,
    RetiradaResponse,
    RetiradaUpdate,
)
from src.services.retirada_service import RetiradaService

router = APIRouter(prefix="/retiradas", tags=["Retiradas"])


def get_service(db: AsyncSession = Depends(get_db)) -> RetiradaService:
    return RetiradaService(db)


@router.get("", response_model=RetiradaListResponse, summary="Listar retiradas")
async def listar_retiradas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    user: CurrentActiveUser = None,
    service: RetiradaService = Depends(get_service),
) -> RetiradaListResponse:
    return await service.get_all(
        skip=skip, limit=limit,
        data_inicio=data_inicio, data_fim=data_fim,
    )


@router.get("/{retirada_id}", response_model=RetiradaResponse, summary="Obter retirada")
async def obter_retirada(
    retirada_id: int,
    user: CurrentActiveUser = None,
    service: RetiradaService = Depends(get_service),
) -> RetiradaResponse:
    retirada = await service.get_by_id(retirada_id)
    if not retirada:
        raise HTTPException(status_code=404, detail="Retirada não encontrada")
    return RetiradaResponse.model_validate(retirada)


@router.post(
    "", response_model=RetiradaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar retirada",
)
async def criar_retirada(
    data: RetiradaCreate,
    user: CurrentAdminUser = None,
    service: RetiradaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> RetiradaResponse:
    retirada = await service.create(data)
    await db.commit()
    return RetiradaResponse.model_validate(retirada)


@router.patch("/{retirada_id}", response_model=RetiradaResponse, summary="Atualizar retirada")
async def atualizar_retirada(
    retirada_id: int,
    data: RetiradaUpdate,
    user: CurrentAdminUser = None,
    service: RetiradaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> RetiradaResponse:
    try:
        retirada = await service.update(retirada_id, data)
        await db.commit()
        return RetiradaResponse.model_validate(retirada)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{retirada_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir retirada")
async def excluir_retirada(
    retirada_id: int,
    user: CurrentAdminUser = None,
    service: RetiradaService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await service.delete(retirada_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
