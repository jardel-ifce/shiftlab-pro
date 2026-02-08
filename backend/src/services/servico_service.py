"""
Serviço de Serviços - ShiftLab Pro.

Contém a lógica de negócio para gerenciamento de tipos de serviço.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.servico import Servico
from src.schemas.servico import ServicoCreate, ServicoListResponse, ServicoResponse, ServicoUpdate


class ServicoService:
    """Serviço para gerenciamento de tipos de serviço."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, servico_id: int) -> Servico | None:
        """Busca serviço por ID."""
        query = select(Servico).where(Servico.id == servico_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        apenas_ativos: bool = True,
    ) -> ServicoListResponse:
        """Lista serviços com filtros."""
        query = select(Servico)

        if apenas_ativos:
            query = query.where(Servico.ativo == True)  # noqa: E712

        if search:
            search_term = f"%{search}%"
            query = query.where(Servico.nome.ilike(search_term))

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(Servico.nome)
        result = await self.db.execute(query)
        servicos = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return ServicoListResponse(
            items=[ServicoResponse.model_validate(s) for s in servicos],
            total=total,
            page=page,
            pages=pages,
        )

    async def create(self, data: ServicoCreate) -> Servico:
        """Cria um novo serviço."""
        servico = Servico(
            nome=data.nome,
            descricao=data.descricao,
            preco=data.preco,
            observacoes=data.observacoes,
            ativo=True,
        )

        self.db.add(servico)
        await self.db.flush()
        await self.db.refresh(servico)

        return servico

    async def update(self, servico_id: int, data: ServicoUpdate) -> Servico:
        """Atualiza um serviço existente."""
        servico = await self.get_by_id(servico_id)
        if not servico:
            raise ValueError("Serviço não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(servico, field, value)

        await self.db.flush()
        await self.db.refresh(servico)

        return servico

    async def delete(self, servico_id: int) -> bool:
        """Desativa um serviço (soft delete)."""
        servico = await self.get_by_id(servico_id)
        if not servico:
            raise ValueError("Serviço não encontrado")

        servico.ativo = False
        await self.db.flush()

        return True
