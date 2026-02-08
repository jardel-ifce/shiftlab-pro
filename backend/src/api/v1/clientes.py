"""
Router de Clientes - ShiftLab Pro.

Endpoints para gerenciamento de clientes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.schemas.cliente import (
    ClienteCreate,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdate,
)
from src.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def get_service(db: AsyncSession = Depends(get_db)) -> ClienteService:
    """Injeta o serviço de clientes."""
    return ClienteService(db)


@router.get(
    "",
    response_model=ClienteListResponse,
    summary="Listar clientes",
    description="Retorna lista paginada de clientes com busca opcional."
)
async def listar_clientes(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    search: str | None = Query(None, description="Busca por nome, telefone ou CPF/CNPJ"),
    user: CurrentActiveUser = None,
    service: ClienteService = Depends(get_service)
) -> ClienteListResponse:
    """Lista clientes com paginação."""
    return await service.get_all(skip=skip, limit=limit, search=search)


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obter cliente",
    description="Retorna dados de um cliente específico."
)
async def obter_cliente(
    cliente_id: int,
    user: CurrentActiveUser = None,
    service: ClienteService = Depends(get_service)
) -> ClienteResponse:
    """Busca cliente por ID."""
    cliente = await service.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return ClienteResponse.model_validate(cliente)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cliente",
    description="Cadastra um novo cliente no sistema."
)
async def criar_cliente(
    data: ClienteCreate,
    user: CurrentActiveUser = None,
    service: ClienteService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> ClienteResponse:
    """Cria um novo cliente."""
    try:
        cliente = await service.create(data)
        await db.commit()
        return ClienteResponse.model_validate(cliente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Atualizar cliente",
    description="Atualiza dados de um cliente existente."
)
async def atualizar_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    user: CurrentActiveUser = None,
    service: ClienteService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> ClienteResponse:
    """Atualiza um cliente."""
    try:
        cliente = await service.update(cliente_id, data)
        await db.commit()
        return ClienteResponse.model_validate(cliente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover cliente",
    description="Remove um cliente e todos os seus veículos."
)
async def remover_cliente(
    cliente_id: int,
    user: CurrentActiveUser = None,
    service: ClienteService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove um cliente."""
    try:
        await service.delete(cliente_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
