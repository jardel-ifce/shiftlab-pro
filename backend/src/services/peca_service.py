"""
Serviço de Peças - ShiftLab Pro.

Contém a lógica de negócio para gerenciamento de peças e itens auxiliares.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.peca import Peca
from src.schemas.peca import PecaCreate, PecaListResponse, PecaResponse, PecaUpdate


class PecaService:
    """Serviço para gerenciamento de peças."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, peca_id: int) -> Peca | None:
        """Busca peça por ID."""
        query = select(Peca).where(Peca.id == peca_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        apenas_ativos: bool = True,
        estoque_baixo: bool = False
    ) -> PecaListResponse:
        """Lista peças com filtros."""
        query = select(Peca)

        if apenas_ativos:
            query = query.where(Peca.ativo == True)  # noqa: E712

        if estoque_baixo:
            query = query.where(Peca.estoque < Peca.estoque_minimo)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Peca.nome.ilike(search_term)) |
                (Peca.marca.ilike(search_term))
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(Peca.nome)
        result = await self.db.execute(query)
        pecas = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return PecaListResponse(
            items=[PecaResponse.model_validate(p) for p in pecas],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: PecaCreate) -> Peca:
        """Cria uma nova peça."""
        peca = Peca(
            nome=data.nome,
            marca=data.marca,
            unidade=data.unidade,
            preco_custo=data.preco_custo,
            preco_venda=data.preco_venda,
            estoque=data.estoque,
            estoque_minimo=data.estoque_minimo,
            comentarios=data.comentarios,
            observacoes=data.observacoes,
            ativo=True
        )

        self.db.add(peca)
        await self.db.flush()
        await self.db.refresh(peca)

        return peca

    async def update(self, peca_id: int, data: PecaUpdate) -> Peca:
        """Atualiza uma peça existente."""
        peca = await self.get_by_id(peca_id)
        if not peca:
            raise ValueError("Peça não encontrada")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(peca, field, value)

        await self.db.flush()
        await self.db.refresh(peca)

        return peca

    async def delete(self, peca_id: int) -> bool:
        """Desativa uma peça (soft delete)."""
        peca = await self.get_by_id(peca_id)
        if not peca:
            raise ValueError("Peça não encontrada")

        peca.ativo = False
        await self.db.flush()

        return True
