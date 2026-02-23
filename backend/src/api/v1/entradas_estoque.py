"""
Router de Entradas de Estoque - ShiftLab Pro.

Endpoints para registrar compras/aquisições de produtos.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser
from src.database import get_db
from src.schemas.entrada_estoque import (
    EntradaEstoqueCreate,
    EntradaEstoqueListResponse,
    EntradaEstoqueResponse,
    ProdutoBuscaResponse,
)
from src.services.entrada_estoque_service import EntradaEstoqueService

router = APIRouter(prefix="/entradas-estoque", tags=["Entradas de Estoque"])


def get_service(db: AsyncSession = Depends(get_db)) -> EntradaEstoqueService:
    return EntradaEstoqueService(db)


@router.get(
    "/buscar-produto",
    response_model=list[ProdutoBuscaResponse],
    summary="Buscar produtos para entrada",
)
async def buscar_produto(
    q: str = Query(..., min_length=1, description="Termo de busca"),
    tipo: str | None = Query(None, description="Filtrar por tipo: oleo, filtro, peca"),
    user: CurrentActiveUser = None,
    service: EntradaEstoqueService = Depends(get_service),
) -> list[ProdutoBuscaResponse]:
    """Busca produtos por nome ou código para seleção na entrada."""
    return await service.buscar_produtos(q, tipo)


@router.get(
    "",
    response_model=EntradaEstoqueListResponse,
    summary="Listar entradas de estoque",
)
async def listar_entradas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    oleo_id: int | None = Query(None, description="Filtrar por óleo"),
    user: CurrentActiveUser = None,
    service: EntradaEstoqueService = Depends(get_service),
) -> EntradaEstoqueListResponse:
    return await service.get_all(skip=skip, limit=limit, oleo_id=oleo_id)


@router.get(
    "/{entrada_id}",
    response_model=EntradaEstoqueResponse,
    summary="Obter entrada",
)
async def obter_entrada(
    entrada_id: int,
    user: CurrentActiveUser = None,
    service: EntradaEstoqueService = Depends(get_service),
) -> EntradaEstoqueResponse:
    entrada = await service.get_by_id(entrada_id)
    if not entrada:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return service._to_response(entrada)


@router.post(
    "",
    response_model=EntradaEstoqueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada de estoque",
)
async def criar_entrada(
    data: EntradaEstoqueCreate,
    user: CurrentActiveUser = None,
    service: EntradaEstoqueService = Depends(get_service),
) -> EntradaEstoqueResponse:
    try:
        entrada = await service.create(data)
        return service._to_response(entrada)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{entrada_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir entrada",
)
async def excluir_entrada(
    entrada_id: int,
    user: CurrentActiveUser = None,
    service: EntradaEstoqueService = Depends(get_service),
) -> None:
    try:
        await service.delete(entrada_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
