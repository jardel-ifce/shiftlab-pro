"""Serviço de Despesas - ShiftLab Pro."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.despesa import Despesa
from src.schemas.despesa import (
    DespesaCreate,
    DespesaListResponse,
    DespesaResponse,
    DespesaUpdate,
)


class DespesaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, despesa_id: int) -> Despesa | None:
        query = select(Despesa).where(Despesa.id == despesa_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        categoria: str | None = None,
    ) -> DespesaListResponse:
        query = select(Despesa)
        if data_inicio:
            query = query.where(Despesa.data >= data_inicio)
        if data_fim:
            query = query.where(Despesa.data <= data_fim)
        if categoria:
            query = query.where(Despesa.categoria == categoria)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset(skip).limit(limit).order_by(Despesa.data.desc())
        result = await self.db.execute(query)
        despesas = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return DespesaListResponse(
            items=[DespesaResponse.model_validate(d) for d in despesas],
            total=total,
            page=page,
            pages=pages,
        )

    async def get_total_periodo(
        self, data_inicio: date | None = None, data_fim: date | None = None
    ) -> float:
        """Soma total de despesas no período."""
        query = select(func.sum(Despesa.valor))
        if data_inicio:
            query = query.where(Despesa.data >= data_inicio)
        if data_fim:
            query = query.where(Despesa.data <= data_fim)
        total = await self.db.scalar(query)
        return float(total or 0)

    async def create(self, data: DespesaCreate) -> Despesa:
        despesa = Despesa(**data.model_dump())
        self.db.add(despesa)
        await self.db.flush()
        await self.db.refresh(despesa)
        return despesa

    async def update(self, despesa_id: int, data: DespesaUpdate) -> Despesa:
        despesa = await self.get_by_id(despesa_id)
        if not despesa:
            raise ValueError("Despesa não encontrada")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(despesa, field, value)
        await self.db.flush()
        await self.db.refresh(despesa)
        return despesa

    async def delete(self, despesa_id: int) -> bool:
        despesa = await self.get_by_id(despesa_id)
        if not despesa:
            raise ValueError("Despesa não encontrada")
        await self.db.delete(despesa)
        await self.db.flush()
        return True
