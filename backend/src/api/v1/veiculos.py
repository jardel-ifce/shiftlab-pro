"""
Router de Veículos - ShiftLab Pro.

Endpoints para gerenciamento de veículos.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.schemas.veiculo import (
    VeiculoCreate,
    VeiculoListResponse,
    VeiculoResponse,
    VeiculoUpdate,
)
from src.services.veiculo_service import VeiculoService

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


def get_service(db: AsyncSession = Depends(get_db)) -> VeiculoService:
    """Injeta o serviço de veículos."""
    return VeiculoService(db)


@router.get(
    "",
    response_model=VeiculoListResponse,
    summary="Listar veículos",
    description="Retorna lista paginada de veículos com filtros."
)
async def listar_veiculos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por placa, marca ou modelo"),
    cliente_id: int | None = Query(None, description="Filtrar por cliente"),
    apenas_ativos: bool = Query(True, description="Mostrar apenas veículos ativos"),
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service)
) -> VeiculoListResponse:
    """Lista veículos com paginação e filtros."""
    return await service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        cliente_id=cliente_id,
        apenas_ativos=apenas_ativos
    )


@router.get(
    "/{veiculo_id}",
    response_model=VeiculoResponse,
    summary="Obter veículo",
    description="Retorna dados de um veículo específico."
)
async def obter_veiculo(
    veiculo_id: int,
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service)
) -> VeiculoResponse:
    """Busca veículo por ID."""
    veiculo = await service.get_by_id(veiculo_id)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return VeiculoResponse.model_validate(veiculo)


@router.get(
    "/placa/{placa}",
    response_model=VeiculoResponse,
    summary="Buscar por placa",
    description="Busca veículo pela placa."
)
async def buscar_por_placa(
    placa: str,
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service)
) -> VeiculoResponse:
    """Busca veículo pela placa."""
    veiculo = await service.get_by_placa(placa)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return VeiculoResponse.model_validate(veiculo)


@router.post(
    "",
    response_model=VeiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar veículo",
    description="Cadastra um novo veículo vinculado a um cliente."
)
async def criar_veiculo(
    data: VeiculoCreate,
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> VeiculoResponse:
    """Cria um novo veículo."""
    try:
        veiculo = await service.create(data)
        await db.commit()
        return VeiculoResponse.model_validate(veiculo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{veiculo_id}",
    response_model=VeiculoResponse,
    summary="Atualizar veículo",
    description="Atualiza dados de um veículo existente."
)
async def atualizar_veiculo(
    veiculo_id: int,
    data: VeiculoUpdate,
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> VeiculoResponse:
    """Atualiza um veículo."""
    try:
        veiculo = await service.update(veiculo_id, data)
        await db.commit()
        return VeiculoResponse.model_validate(veiculo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{veiculo_id}/quilometragem",
    response_model=VeiculoResponse,
    summary="Atualizar quilometragem",
    description="Atualiza apenas a quilometragem do veículo."
)
async def atualizar_quilometragem(
    veiculo_id: int,
    km: int = Query(..., ge=0, description="Nova quilometragem"),
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> VeiculoResponse:
    """Atualiza quilometragem."""
    try:
        veiculo = await service.update_quilometragem(veiculo_id, km)
        await db.commit()
        return VeiculoResponse.model_validate(veiculo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{veiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar veículo",
    description="Desativa um veículo (soft delete). O histórico de trocas é preservado."
)
async def remover_veiculo(
    veiculo_id: int,
    user: CurrentActiveUser = None,
    service: VeiculoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove um veículo."""
    try:
        await service.delete(veiculo_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
