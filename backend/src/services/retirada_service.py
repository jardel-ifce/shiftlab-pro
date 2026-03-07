"""Serviço de Retiradas - ShiftLab Pro."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.retirada import Retirada
from src.schemas.retirada import (
    RetiradaCreate,
    RetiradaListResponse,
    RetiradaResponse,
    RetiradaUpdate,
)


class RetiradaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, retirada_id: int) -> Retirada | None:
        query = select(Retirada).where(Retirada.id == retirada_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> RetiradaListResponse:
        query = select(Retirada)
        if data_inicio:
            query = query.where(Retirada.data >= data_inicio)
        if data_fim:
            query = query.where(Retirada.data <= data_fim)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset(skip).limit(limit).order_by(Retirada.data.desc())
        result = await self.db.execute(query)
        retiradas = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return RetiradaListResponse(
            items=[RetiradaResponse.model_validate(r) for r in retiradas],
            total=total,
            page=page,
            pages=pages,
        )

    async def get_total_periodo(
        self, data_inicio: date | None = None, data_fim: date | None = None
    ) -> float:
        """Soma total de retiradas no período."""
        query = select(func.sum(Retirada.valor))
        if data_inicio:
            query = query.where(Retirada.data >= data_inicio)
        if data_fim:
            query = query.where(Retirada.data <= data_fim)
        total = await self.db.scalar(query)
        return float(total or 0)

    async def create(self, data: RetiradaCreate) -> Retirada:
        retirada = Retirada(**data.model_dump())
        self.db.add(retirada)
        await self.db.flush()
        await self.db.refresh(retirada)
        return retirada

    async def update(self, retirada_id: int, data: RetiradaUpdate) -> Retirada:
        retirada = await self.get_by_id(retirada_id)
        if not retirada:
            raise ValueError("Retirada não encontrada")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(retirada, field, value)
        await self.db.flush()
        await self.db.refresh(retirada)
        return retirada

    async def delete(self, retirada_id: int) -> bool:
        retirada = await self.get_by_id(retirada_id)
        if not retirada:
            raise ValueError("Retirada não encontrada")
        await self.db.delete(retirada)
        await self.db.flush()
        return True
