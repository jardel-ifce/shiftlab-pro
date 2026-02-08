"""
Router de Óleos - ShiftLab Pro.

Endpoints para gerenciamento de óleos (produtos).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.oleo import (
    OleoCreate,
    OleoEstoqueUpdate,
    OleoListResponse,
    OleoResponse,
    OleoUpdate,
)
from src.services.oleo_service import OleoService

router = APIRouter(prefix="/oleos", tags=["Óleos"])


def get_service(db: AsyncSession = Depends(get_db)) -> OleoService:
    """Injeta o serviço de óleos."""
    return OleoService(db)


@router.get(
    "",
    response_model=OleoListResponse,
    summary="Listar óleos",
    description="Retorna lista de óleos disponíveis."
)
async def listar_oleos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por nome ou marca"),
    tipo: str | None = Query(None, description="Filtrar por tipo (atf, cvt, manual, etc)"),
    apenas_ativos: bool = Query(True, description="Mostrar apenas ativos"),
    estoque_baixo: bool = Query(False, description="Mostrar apenas com estoque baixo"),
    user: CurrentActiveUser = None,
    service: OleoService = Depends(get_service)
) -> OleoListResponse:
    """Lista óleos com filtros."""
    return await service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        tipo=tipo,
        apenas_ativos=apenas_ativos,
        estoque_baixo=estoque_baixo
    )


@router.get(
    "/estoque-baixo",
    response_model=list[OleoResponse],
    summary="Óleos com estoque baixo",
    description="Lista óleos que precisam de reposição."
)
async def oleos_estoque_baixo(
    user: CurrentActiveUser = None,
    service: OleoService = Depends(get_service)
) -> list[OleoResponse]:
    """Lista óleos com estoque baixo."""
    oleos = await service.get_estoque_baixo()
    return [OleoResponse.model_validate(o) for o in oleos]


@router.get(
    "/{oleo_id}",
    response_model=OleoResponse,
    summary="Obter óleo",
    description="Retorna dados de um óleo específico."
)
async def obter_oleo(
    oleo_id: int,
    user: CurrentActiveUser = None,
    service: OleoService = Depends(get_service)
) -> OleoResponse:
    """Busca óleo por ID."""
    oleo = await service.get_by_id(oleo_id)
    if not oleo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Óleo não encontrado"
        )
    return OleoResponse.model_validate(oleo)


@router.post(
    "",
    response_model=OleoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar óleo",
    description="Cadastra um novo tipo de óleo. Requer permissão de admin."
)
async def criar_oleo(
    data: OleoCreate,
    user: CurrentAdminUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> OleoResponse:
    """Cria um novo óleo (admin only)."""
    oleo = await service.create(data)
    await db.commit()
    return OleoResponse.model_validate(oleo)


@router.patch(
    "/{oleo_id}",
    response_model=OleoResponse,
    summary="Atualizar óleo",
    description="Atualiza dados de um óleo. Requer permissão de admin."
)
async def atualizar_oleo(
    oleo_id: int,
    data: OleoUpdate,
    user: CurrentAdminUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> OleoResponse:
    """Atualiza um óleo (admin only)."""
    try:
        oleo = await service.update(oleo_id, data)
        await db.commit()
        return OleoResponse.model_validate(oleo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{oleo_id}/estoque",
    response_model=OleoResponse,
    summary="Ajustar estoque",
    description="Adiciona ou remove quantidade do estoque."
)
async def ajustar_estoque(
    oleo_id: int,
    data: OleoEstoqueUpdate,
    user: CurrentActiveUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> OleoResponse:
    """Ajusta estoque de um óleo."""
    try:
        oleo = await service.atualizar_estoque(
            oleo_id,
            data.quantidade,
            data.operacao
        )
        await db.commit()
        return OleoResponse.model_validate(oleo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{oleo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar óleo",
    description="Desativa um óleo (soft delete). Requer permissão de admin."
)
async def desativar_oleo(
    oleo_id: int,
    user: CurrentAdminUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Desativa um óleo (admin only)."""
    try:
        await service.delete(oleo_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
