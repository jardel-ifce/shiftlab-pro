"""
Serviço de Óleos - ShiftLab Pro.

Contém a lógica de negócio para gerenciamento de óleos (produtos).
"""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.oleo import Oleo
from src.schemas.oleo import OleoCreate, OleoListResponse, OleoResponse, OleoUpdate


class OleoService:
    """Serviço para gerenciamento de óleos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, oleo_id: int) -> Oleo | None:
        """Busca óleo por ID."""
        query = select(Oleo).where(Oleo.id == oleo_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        apenas_ativos: bool = True,
        estoque_baixo: bool = False
    ) -> OleoListResponse:
        """Lista óleos com filtros."""
        query = select(Oleo)

        if apenas_ativos:
            query = query.where(Oleo.ativo == True)  # noqa: E712

        if estoque_baixo:
            query = query.where(Oleo.estoque_litros < Oleo.estoque_minimo)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Oleo.nome.ilike(search_term)) |
                (Oleo.marca.ilike(search_term)) |
                (Oleo.tipo_oleo_transmissao.ilike(search_term))
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(Oleo.marca, Oleo.nome)
        result = await self.db.execute(query)
        oleos = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return OleoListResponse(
            items=[OleoResponse.model_validate(o) for o in oleos],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: OleoCreate) -> Oleo:
        """Cria um novo óleo."""
        oleo = Oleo(
            nome=data.nome,
            marca=data.marca,
            modelo=data.modelo,
            tipo_veiculo=data.tipo_veiculo,
            viscosidade=data.viscosidade,
            volume_unidade=data.volume_unidade,
            volume_liquido=data.volume_liquido,
            formato_venda=data.formato_venda,
            tipo_recipiente=data.tipo_recipiente,
            tipo_oleo_transmissao=data.tipo_oleo_transmissao,
            desempenho=data.desempenho,
            codigo_oem=data.codigo_oem,
            custo_litro=data.custo_litro,
            preco_litro=data.preco_litro,
            estoque_litros=data.estoque_litros,
            estoque_minimo=data.estoque_minimo,
            observacoes=data.observacoes,
            ativo=True
        )

        self.db.add(oleo)
        await self.db.flush()
        await self.db.refresh(oleo)

        return oleo

    async def update(self, oleo_id: int, data: OleoUpdate) -> Oleo:
        """Atualiza um óleo existente."""
        oleo = await self.get_by_id(oleo_id)
        if not oleo:
            raise ValueError("Óleo não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(oleo, field, value)

        await self.db.flush()
        await self.db.refresh(oleo)

        return oleo

    async def atualizar_estoque(
        self,
        oleo_id: int,
        quantidade: Decimal,
        operacao: str = "adicionar"
    ) -> Oleo:
        """Adiciona ou remove do estoque."""
        oleo = await self.get_by_id(oleo_id)
        if not oleo:
            raise ValueError("Óleo não encontrado")

        if operacao == "adicionar":
            oleo.estoque_litros += quantidade
        elif operacao == "remover":
            if oleo.estoque_litros < quantidade:
                raise ValueError("Estoque insuficiente")
            oleo.estoque_litros -= quantidade
        else:
            raise ValueError("Operação inválida")

        await self.db.flush()
        await self.db.refresh(oleo)

        return oleo

    async def get_estoque_baixo(self) -> list[Oleo]:
        """Retorna óleos com estoque abaixo do mínimo."""
        query = (
            select(Oleo)
            .where(Oleo.ativo == True)  # noqa: E712
            .where(Oleo.estoque_litros < Oleo.estoque_minimo)
            .order_by(Oleo.estoque_litros)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, oleo_id: int) -> bool:
        """Desativa um óleo (soft delete)."""
        oleo = await self.get_by_id(oleo_id)
        if not oleo:
            raise ValueError("Óleo não encontrado")

        oleo.ativo = False
        await self.db.flush()

        return True
