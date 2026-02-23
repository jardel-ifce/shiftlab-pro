"""Router de Configurações - ShiftLab Pro."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentActiveUser, CurrentAdminUser
from src.database import get_db
from src.schemas.configuracao import ConfiguracaoUpdate, ImpostoResponse
from src.services.configuracao_service import ConfiguracaoService

router = APIRouter(prefix="/configuracoes", tags=["Configurações"])


def get_service(db: AsyncSession = Depends(get_db)) -> ConfiguracaoService:
    return ConfiguracaoService(db)


@router.get("/imposto", response_model=ImpostoResponse, summary="Obter % de imposto")
async def obter_imposto(
    user: CurrentActiveUser = None,
    service: ConfiguracaoService = Depends(get_service),
) -> ImpostoResponse:
    percentual = await service.get_imposto_percentual()
    return ImpostoResponse(percentual=percentual)


@router.put("/imposto", response_model=ImpostoResponse, summary="Atualizar % de imposto")
async def atualizar_imposto(
    data: ConfiguracaoUpdate,
    user: CurrentAdminUser = None,
    service: ConfiguracaoService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
) -> ImpostoResponse:
    try:
        float(data.valor)
    except ValueError:
        raise HTTPException(status_code=400, detail="Valor deve ser um número válido")
    try:
        await service.update_by_chave("imposto_percentual", data)
        await db.commit()
        return ImpostoResponse(percentual=float(data.valor))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
