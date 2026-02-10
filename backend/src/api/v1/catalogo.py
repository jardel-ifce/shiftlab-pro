"""
Router de Catálogo de Veículos - ShiftLab Pro.

Endpoints para gerenciamento do catálogo de montadoras e modelos de referência,
e proxy para consulta à Tabela FIPE (API parallelum).
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.modelo_referencia import (
    ModeloReferenciaCreate,
    ModeloReferenciaListResponse,
    ModeloReferenciaResponse,
    ModeloReferenciaUpdate,
)
from src.schemas.montadora import (
    MontadoraComModelosResponse,
    MontadoraCreate,
    MontadoraListResponse,
    MontadoraResponse,
    MontadoraUpdate,
)
from src.services.catalogo_service import CatalogoService
from src.services.fipe_service import fipe_get_anos, fipe_get_marcas, fipe_get_modelos

router = APIRouter(prefix="/catalogo", tags=["Catálogo de Veículos"])


def get_service(db: AsyncSession = Depends(get_db)) -> CatalogoService:
    """Injeta o serviço de catálogo."""
    return CatalogoService(db)


# =============================================================================
# MONTADORAS
# =============================================================================


@router.get(
    "/montadoras",
    response_model=MontadoraListResponse,
    summary="Listar montadoras",
    description="Retorna lista de montadoras ordenadas alfabeticamente."
)
async def listar_montadoras(
    apenas_ativas: bool = Query(True, description="Mostrar apenas ativas"),
    user: CurrentActiveUser = None,
    service: CatalogoService = Depends(get_service)
) -> MontadoraListResponse:
    """Lista todas as montadoras."""
    montadoras = await service.get_montadoras(apenas_ativas=apenas_ativas)
    return MontadoraListResponse(
        items=[MontadoraResponse.model_validate(m) for m in montadoras],
        total=len(montadoras)
    )


@router.get(
    "/montadoras/{montadora_id}",
    response_model=MontadoraComModelosResponse,
    summary="Obter montadora com modelos",
    description="Retorna dados de uma montadora e seus modelos."
)
async def obter_montadora(
    montadora_id: int,
    user: CurrentActiveUser = None,
    service: CatalogoService = Depends(get_service)
) -> MontadoraComModelosResponse:
    """Busca montadora por ID com seus modelos."""
    montadora = await service.get_montadora_by_id(montadora_id)
    if not montadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Montadora não encontrada"
        )
    return MontadoraComModelosResponse.model_validate(montadora)


@router.post(
    "/montadoras",
    response_model=MontadoraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar montadora",
    description="Cadastra uma nova montadora. Requer permissão de admin."
)
async def criar_montadora(
    data: MontadoraCreate,
    user: CurrentAdminUser = None,
    service: CatalogoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> MontadoraResponse:
    """Cria uma nova montadora (admin only)."""
    try:
        montadora = await service.create_montadora(data)
        await db.commit()
        return MontadoraResponse.model_validate(montadora)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/montadoras/{montadora_id}",
    response_model=MontadoraResponse,
    summary="Atualizar montadora",
    description="Atualiza dados de uma montadora. Requer permissão de admin."
)
async def atualizar_montadora(
    montadora_id: int,
    data: MontadoraUpdate,
    user: CurrentAdminUser = None,
    service: CatalogoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> MontadoraResponse:
    """Atualiza uma montadora (admin only)."""
    try:
        montadora = await service.update_montadora(montadora_id, data)
        await db.commit()
        return MontadoraResponse.model_validate(montadora)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =============================================================================
# MODELOS DE REFERÊNCIA
# =============================================================================


@router.get(
    "/modelos",
    response_model=ModeloReferenciaListResponse,
    summary="Listar modelos por montadora",
    description="Retorna modelos filtrados por montadora."
)
async def listar_modelos(
    montadora_id: int = Query(..., description="ID da montadora"),
    apenas_ativos: bool = Query(True, description="Mostrar apenas ativos"),
    user: CurrentActiveUser = None,
    service: CatalogoService = Depends(get_service)
) -> ModeloReferenciaListResponse:
    """Lista modelos de uma montadora."""
    modelos = await service.get_modelos_by_montadora(
        montadora_id=montadora_id,
        apenas_ativos=apenas_ativos
    )
    return ModeloReferenciaListResponse(
        items=[ModeloReferenciaResponse.model_validate(m) for m in modelos],
        total=len(modelos)
    )


@router.get(
    "/modelos/busca",
    response_model=ModeloReferenciaListResponse,
    summary="Buscar modelos",
    description="Busca modelos por texto em todas as montadoras."
)
async def buscar_modelos(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    limit: int = Query(20, ge=1, le=50),
    user: CurrentActiveUser = None,
    service: CatalogoService = Depends(get_service)
) -> ModeloReferenciaListResponse:
    """Busca modelos por texto."""
    modelos = await service.search_modelos(search=q, limit=limit)
    return ModeloReferenciaListResponse(
        items=[ModeloReferenciaResponse.model_validate(m) for m in modelos],
        total=len(modelos)
    )


@router.get(
    "/modelos/{modelo_id}",
    response_model=ModeloReferenciaResponse,
    summary="Obter modelo",
    description="Retorna dados de um modelo específico."
)
async def obter_modelo(
    modelo_id: int,
    user: CurrentActiveUser = None,
    service: CatalogoService = Depends(get_service)
) -> ModeloReferenciaResponse:
    """Busca modelo por ID."""
    modelo = await service.get_modelo_by_id(modelo_id)
    if not modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo não encontrado"
        )
    return ModeloReferenciaResponse.model_validate(modelo)


@router.post(
    "/modelos",
    response_model=ModeloReferenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar modelo",
    description="Cadastra um novo modelo de referência. Requer permissão de admin."
)
async def criar_modelo(
    data: ModeloReferenciaCreate,
    user: CurrentAdminUser = None,
    service: CatalogoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> ModeloReferenciaResponse:
    """Cria um novo modelo (admin only)."""
    try:
        modelo = await service.create_modelo(data)
        await db.commit()
        return ModeloReferenciaResponse.model_validate(modelo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/modelos/{modelo_id}",
    response_model=ModeloReferenciaResponse,
    summary="Atualizar modelo",
    description="Atualiza dados de um modelo. Requer permissão de admin."
)
async def atualizar_modelo(
    modelo_id: int,
    data: ModeloReferenciaUpdate,
    user: CurrentAdminUser = None,
    service: CatalogoService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> ModeloReferenciaResponse:
    """Atualiza um modelo (admin only)."""
    try:
        modelo = await service.update_modelo(modelo_id, data)
        await db.commit()
        return ModeloReferenciaResponse.model_validate(modelo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =============================================================================
# FIPE - Proxy para API Tabela FIPE (parallelum)
# =============================================================================


@router.get(
    "/fipe/marcas",
    summary="Listar marcas da FIPE",
    description="Retorna marcas de carros da Tabela FIPE. Cache de 24h.",
)
async def fipe_marcas(
    user: CurrentActiveUser = None,
) -> list[dict]:
    """Lista marcas da Tabela FIPE."""
    try:
        return await fipe_get_marcas()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Erro ao consultar API FIPE",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API FIPE indisponível no momento",
        )


@router.get(
    "/fipe/modelos",
    summary="Listar modelos da FIPE por marca",
    description="Retorna modelos de uma marca da Tabela FIPE. Cache de 24h.",
)
async def fipe_modelos(
    marca_code: str = Query(..., description="Código da marca na FIPE"),
    user: CurrentActiveUser = None,
) -> list[dict]:
    """Lista modelos de uma marca na FIPE."""
    try:
        return await fipe_get_modelos(marca_code)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Erro ao consultar API FIPE",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API FIPE indisponível no momento",
        )


@router.get(
    "/fipe/anos",
    summary="Listar anos de um modelo da FIPE",
    description="Retorna anos disponíveis de um modelo na Tabela FIPE. Cache de 24h.",
)
async def fipe_anos(
    marca_code: str = Query(..., description="Código da marca na FIPE"),
    modelo_code: str = Query(..., description="Código do modelo na FIPE"),
    user: CurrentActiveUser = None,
) -> list[dict]:
    """Lista anos disponíveis de um modelo na FIPE."""
    try:
        return await fipe_get_anos(marca_code, modelo_code)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Erro ao consultar API FIPE",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API FIPE indisponível no momento",
        )
