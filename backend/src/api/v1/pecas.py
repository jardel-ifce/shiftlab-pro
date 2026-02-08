"""
Router de Peças - ShiftLab Pro.

Endpoints para gerenciamento de peças e itens auxiliares.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.peca import (
    PecaCreate,
    PecaListResponse,
    PecaResponse,
    PecaUpdate,
)
from src.services.peca_service import PecaService

router = APIRouter(prefix="/pecas", tags=["Peças"])


def get_service(db: AsyncSession = Depends(get_db)) -> PecaService:
    """Injeta o serviço de peças."""
    return PecaService(db)


@router.get(
    "",
    response_model=PecaListResponse,
    summary="Listar peças",
    description="Retorna lista de peças disponíveis."
)
async def listar_pecas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por nome ou marca"),
    apenas_ativos: bool = Query(True, description="Mostrar apenas ativos"),
    estoque_baixo: bool = Query(False, description="Mostrar apenas com estoque baixo"),
    user: CurrentActiveUser = None,
    service: PecaService = Depends(get_service)
) -> PecaListResponse:
    """Lista peças com filtros."""
    return await service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        apenas_ativos=apenas_ativos,
        estoque_baixo=estoque_baixo
    )


@router.get(
    "/{peca_id}",
    response_model=PecaResponse,
    summary="Obter peça",
    description="Retorna dados de uma peça específica."
)
async def obter_peca(
    peca_id: int,
    user: CurrentActiveUser = None,
    service: PecaService = Depends(get_service)
) -> PecaResponse:
    """Busca peça por ID."""
    peca = await service.get_by_id(peca_id)
    if not peca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )
    return PecaResponse.model_validate(peca)


@router.post(
    "",
    response_model=PecaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar peça",
    description="Cadastra uma nova peça/item. Requer permissão de admin."
)
async def criar_peca(
    data: PecaCreate,
    user: CurrentAdminUser = None,
    service: PecaService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> PecaResponse:
    """Cria uma nova peça (admin only)."""
    peca = await service.create(data)
    await db.commit()
    return PecaResponse.model_validate(peca)


@router.patch(
    "/{peca_id}",
    response_model=PecaResponse,
    summary="Atualizar peça",
    description="Atualiza dados de uma peça. Requer permissão de admin."
)
async def atualizar_peca(
    peca_id: int,
    data: PecaUpdate,
    user: CurrentAdminUser = None,
    service: PecaService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> PecaResponse:
    """Atualiza uma peça (admin only)."""
    try:
        peca = await service.update(peca_id, data)
        await db.commit()
        return PecaResponse.model_validate(peca)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{peca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar peça",
    description="Desativa uma peça (soft delete). Requer permissão de admin."
)
async def desativar_peca(
    peca_id: int,
    user: CurrentAdminUser = None,
    service: PecaService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Desativa uma peça (admin only)."""
    try:
        await service.delete(peca_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
