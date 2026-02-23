"""
Serviço de Filtros de Óleo - ShiftLab Pro.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.filtro import FiltroOleo
from src.schemas.filtro import FiltroCreate, FiltroListResponse, FiltroResponse, FiltroUpdate


class FiltroService:
    """Serviço para gerenciamento de filtros de óleo."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, filtro_id: int) -> FiltroOleo | None:
        query = select(FiltroOleo).where(FiltroOleo.id == filtro_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        apenas_ativos: bool = True,
        estoque_baixo: bool = False
    ) -> FiltroListResponse:
        query = select(FiltroOleo)

        if apenas_ativos:
            query = query.where(FiltroOleo.ativo == True)  # noqa: E712

        if estoque_baixo:
            query = query.where(FiltroOleo.estoque < FiltroOleo.estoque_minimo)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (FiltroOleo.nome.ilike(search_term)) |
                (FiltroOleo.marca.ilike(search_term)) |
                (FiltroOleo.codigo_produto.ilike(search_term)) |
                (FiltroOleo.codigo_oem.ilike(search_term))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset(skip).limit(limit).order_by(FiltroOleo.marca, FiltroOleo.nome)
        result = await self.db.execute(query)
        filtros = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return FiltroListResponse(
            items=[FiltroResponse.model_validate(f) for f in filtros],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: FiltroCreate) -> FiltroOleo:
        filtro = FiltroOleo(
            codigo_produto=data.codigo_produto,
            nome=data.nome,
            marca=data.marca,
            codigo_oem=data.codigo_oem,
            custo_unitario=data.custo_unitario,
            preco_unitario=data.preco_unitario,
            estoque=data.estoque,
            estoque_minimo=data.estoque_minimo,
            observacoes=data.observacoes,
            ativo=True
        )

        self.db.add(filtro)
        await self.db.flush()
        await self.db.refresh(filtro)

        return filtro

    async def update(self, filtro_id: int, data: FiltroUpdate) -> FiltroOleo:
        filtro = await self.get_by_id(filtro_id)
        if not filtro:
            raise ValueError("Filtro não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(filtro, field, value)

        await self.db.flush()
        await self.db.refresh(filtro)

        return filtro

    async def delete(self, filtro_id: int) -> bool:
        filtro = await self.get_by_id(filtro_id)
        if not filtro:
            raise ValueError("Filtro não encontrado")

        filtro.ativo = False
        await self.db.flush()

        return True
