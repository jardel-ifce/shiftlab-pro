"""
Router de Óleos - ShiftLab Pro.

Endpoints para gerenciamento de óleos (produtos).
"""

import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.config import settings
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
    search: str | None = Query(None, description="Busca por nome, marca ou tipo"),
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


# =============================================================================
# UPLOAD DE FOTO
# =============================================================================

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "oleos"


@router.post(
    "/{oleo_id}/foto",
    response_model=OleoResponse,
    summary="Upload de foto do óleo",
    description="Envia uma imagem do produto (JPG/PNG, máx 10MB). Requer admin.",
)
async def upload_foto(
    oleo_id: int,
    file: UploadFile,
    user: CurrentAdminUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> OleoResponse:
    """Faz upload da foto de um óleo."""
    oleo = await service.get_by_id(oleo_id)
    if not oleo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Óleo não encontrado",
        )

    # Validar extensão
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Use JPG ou PNG.",
        )

    # Validar tamanho
    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Deletar foto anterior se existir
    if oleo.foto_url:
        old_path = Path(settings.UPLOAD_DIR) / oleo.foto_url.removeprefix("/uploads/")
        if old_path.exists():
            old_path.unlink()

    # Salvar novo arquivo
    filename = f"{oleo_id}_{int(time.time())}.{ext}"
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    # Atualizar no banco
    oleo.foto_url = f"/uploads/oleos/{filename}"
    await db.flush()
    await db.refresh(oleo)
    await db.commit()

    return OleoResponse.model_validate(oleo)


@router.delete(
    "/{oleo_id}/foto",
    response_model=OleoResponse,
    summary="Remover foto do óleo",
    description="Remove a imagem do produto. Requer admin.",
)
async def remover_foto(
    oleo_id: int,
    user: CurrentAdminUser = None,
    service: OleoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> OleoResponse:
    """Remove a foto de um óleo."""
    oleo = await service.get_by_id(oleo_id)
    if not oleo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Óleo não encontrado",
        )

    if oleo.foto_url:
        old_path = Path(settings.UPLOAD_DIR) / oleo.foto_url.removeprefix("/uploads/")
        if old_path.exists():
            old_path.unlink()

    oleo.foto_url = None
    await db.flush()
    await db.refresh(oleo)
    await db.commit()

    return OleoResponse.model_validate(oleo)
