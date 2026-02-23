"""
Router de Filtros de Óleo - ShiftLab Pro.
"""

import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.config import settings
from src.database import get_db
from src.schemas.filtro import (
    FiltroCreate,
    FiltroListResponse,
    FiltroResponse,
    FiltroUpdate,
)
from src.services.filtro_service import FiltroService

router = APIRouter(prefix="/filtros", tags=["Filtros de Óleo"])


def get_service(db: AsyncSession = Depends(get_db)) -> FiltroService:
    return FiltroService(db)


@router.get("", response_model=FiltroListResponse, summary="Listar filtros")
async def listar_filtros(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por nome, marca, código ou OEM"),
    apenas_ativos: bool = Query(True),
    estoque_baixo: bool = Query(False),
    user: CurrentActiveUser = None,
    service: FiltroService = Depends(get_service)
) -> FiltroListResponse:
    return await service.get_all(
        skip=skip, limit=limit, search=search,
        apenas_ativos=apenas_ativos, estoque_baixo=estoque_baixo
    )


@router.get("/{filtro_id}", response_model=FiltroResponse, summary="Obter filtro")
async def obter_filtro(
    filtro_id: int,
    user: CurrentActiveUser = None,
    service: FiltroService = Depends(get_service)
) -> FiltroResponse:
    filtro = await service.get_by_id(filtro_id)
    if not filtro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filtro não encontrado")
    return FiltroResponse.model_validate(filtro)


@router.post("", response_model=FiltroResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar filtro")
async def criar_filtro(
    data: FiltroCreate,
    user: CurrentAdminUser = None,
    service: FiltroService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> FiltroResponse:
    filtro = await service.create(data)
    await db.commit()
    return FiltroResponse.model_validate(filtro)


@router.patch("/{filtro_id}", response_model=FiltroResponse, summary="Atualizar filtro")
async def atualizar_filtro(
    filtro_id: int,
    data: FiltroUpdate,
    user: CurrentAdminUser = None,
    service: FiltroService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> FiltroResponse:
    try:
        filtro = await service.update(filtro_id, data)
        await db.commit()
        return FiltroResponse.model_validate(filtro)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{filtro_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desativar filtro")
async def desativar_filtro(
    filtro_id: int,
    user: CurrentAdminUser = None,
    service: FiltroService = Depends(get_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    try:
        await service.delete(filtro_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# =============================================================================
# UPLOAD DE FOTO
# =============================================================================

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "filtros"


@router.post("/{filtro_id}/foto", response_model=FiltroResponse, summary="Upload de foto do filtro")
async def upload_foto(
    filtro_id: int,
    file: UploadFile,
    user: CurrentAdminUser = None,
    service: FiltroService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> FiltroResponse:
    filtro = await service.get_by_id(filtro_id)
    if not filtro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filtro não encontrado")

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato inválido. Use JPG ou PNG.")

    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    if filtro.foto_url:
        old_path = Path(settings.UPLOAD_DIR) / filtro.foto_url.removeprefix("/uploads/")
        if old_path.exists():
            old_path.unlink()

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{filtro_id}_{int(time.time())}.{ext}"
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    filtro.foto_url = f"/uploads/filtros/{filename}"
    await db.flush()
    await db.refresh(filtro)
    await db.commit()

    return FiltroResponse.model_validate(filtro)


@router.delete("/{filtro_id}/foto", response_model=FiltroResponse, summary="Remover foto do filtro")
async def remover_foto(
    filtro_id: int,
    user: CurrentAdminUser = None,
    service: FiltroService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> FiltroResponse:
    filtro = await service.get_by_id(filtro_id)
    if not filtro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filtro não encontrado")

    if filtro.foto_url:
        old_path = Path(settings.UPLOAD_DIR) / filtro.foto_url.removeprefix("/uploads/")
        if old_path.exists():
            old_path.unlink()

    filtro.foto_url = None
    await db.flush()
    await db.refresh(filtro)
    await db.commit()

    return FiltroResponse.model_validate(filtro)
