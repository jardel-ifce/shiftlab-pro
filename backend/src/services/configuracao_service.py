"""Serviço de Configurações - ShiftLab Pro."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.configuracao import Configuracao
from src.schemas.configuracao import ConfiguracaoUpdate


class ConfiguracaoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_chave(self, chave: str) -> Configuracao | None:
        query = select(Configuracao).where(Configuracao.chave == chave)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_imposto_percentual(self) -> float:
        """Retorna o percentual de imposto configurado (default 0)."""
        config = await self.get_by_chave("imposto_percentual")
        if config:
            try:
                return float(config.valor)
            except ValueError:
                return 0.0
        return 0.0

    async def update_by_chave(self, chave: str, data: ConfiguracaoUpdate) -> Configuracao:
        config = await self.get_by_chave(chave)
        if not config:
            raise ValueError(f"Configuração '{chave}' não encontrada")
        config.valor = data.valor
        await self.db.flush()
        await self.db.refresh(config)
        return config
