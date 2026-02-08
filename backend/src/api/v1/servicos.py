"""
Router de Serviços - ShiftLab Pro.

Endpoints para gerenciamento de tipos de serviço.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.servico import (
    ServicoCreate,
    ServicoListResponse,
    ServicoResponse,
    ServicoUpdate,
)
from src.services.servico_service import ServicoService

router = APIRouter(prefix="/servicos", tags=["Serviços"])


def get_service(db: AsyncSession = Depends(get_db)) -> ServicoService:
    """Injeta o serviço de serviços."""
    return ServicoService(db)


@router.get(
    "",
    response_model=ServicoListResponse,
    summary="Listar serviços",
    description="Retorna lista de serviços disponíveis.",
)
async def listar_servicos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por nome"),
    apenas_ativos: bool = Query(True, description="Mostrar apenas ativos"),
    user: CurrentActiveUser = None,
    service: ServicoService = Depends(get_service),
) -> ServicoListResponse:
    """Lista serviços com filtros."""
    return await service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        apenas_ativos=apenas_ativos,
    )


@router.get(
    "/{servico_id}",
    response_model=ServicoResponse,
    summary="Obter serviço",
    description="Retorna dados de um serviço específico.",
)
async def obter_servico(
    servico_id: int,
    user: CurrentActiveUser = None,
    service: ServicoService = Depends(get_service),
) -> ServicoResponse:
    """Busca serviço por ID."""
    servico = await service.get_by_id(servico_id)
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado",
        )
    return ServicoResponse.model_validate(servico)


@router.post(
    "",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar serviço",
    description="Cadastra um novo tipo de serviço. Requer permissão de admin.",
)
async def criar_servico(
    data: ServicoCreate,
    user: CurrentAdminUser = None,
    service: ServicoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> ServicoResponse:
    """Cria um novo serviço (admin only)."""
    servico = await service.create(data)
    await db.commit()
    return ServicoResponse.model_validate(servico)


@router.patch(
    "/{servico_id}",
    response_model=ServicoResponse,
    summary="Atualizar serviço",
    description="Atualiza dados de um serviço. Requer permissão de admin.",
)
async def atualizar_servico(
    servico_id: int,
    data: ServicoUpdate,
    user: CurrentAdminUser = None,
    service: ServicoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> ServicoResponse:
    """Atualiza um serviço (admin only)."""
    try:
        servico = await service.update(servico_id, data)
        await db.commit()
        return ServicoResponse.model_validate(servico)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar serviço",
    description="Desativa um serviço (soft delete). Requer permissão de admin.",
)
async def desativar_servico(
    servico_id: int,
    user: CurrentAdminUser = None,
    service: ServicoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Desativa um serviço (admin only)."""
    try:
        await service.delete(servico_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
