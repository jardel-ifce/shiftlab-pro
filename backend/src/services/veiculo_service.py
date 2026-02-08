"""
Serviço de Veículos - ShiftLab Pro.

Contém a lógica de negócio para operações com veículos.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.veiculo import Veiculo
from src.domain.cliente import Cliente
from src.schemas.veiculo import VeiculoCreate, VeiculoListResponse, VeiculoResponse, VeiculoUpdate


class VeiculoService:
    """Serviço para gerenciamento de veículos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, veiculo_id: int) -> Veiculo | None:
        """Busca veículo por ID com relacionamentos."""
        query = (
            select(Veiculo)
            .options(selectinload(Veiculo.cliente))
            .where(Veiculo.id == veiculo_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_placa(self, placa: str) -> Veiculo | None:
        """Busca veículo pela placa."""
        query = select(Veiculo).where(Veiculo.placa == placa.upper())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cliente(self, cliente_id: int, apenas_ativos: bool = True) -> list[Veiculo]:
        """Lista veículos de um cliente."""
        query = (
            select(Veiculo)
            .where(Veiculo.cliente_id == cliente_id)
            .order_by(Veiculo.marca, Veiculo.modelo)
        )
        if apenas_ativos:
            query = query.where(Veiculo.ativo.is_(True))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        cliente_id: int | None = None,
        apenas_ativos: bool = True
    ) -> VeiculoListResponse:
        """Lista veículos com paginação e filtros."""
        query = select(Veiculo)

        # Filtro por ativos
        if apenas_ativos:
            query = query.where(Veiculo.ativo.is_(True))

        # Filtro por cliente
        if cliente_id:
            query = query.where(Veiculo.cliente_id == cliente_id)

        # Busca por placa, marca ou modelo
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Veiculo.placa.ilike(search_term)) |
                (Veiculo.marca.ilike(search_term)) |
                (Veiculo.modelo.ilike(search_term))
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(Veiculo.placa)
        result = await self.db.execute(query)
        veiculos = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return VeiculoListResponse(
            items=[VeiculoResponse.model_validate(v) for v in veiculos],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: VeiculoCreate) -> Veiculo:
        """Cria um novo veículo."""
        # Verifica se cliente existe
        cliente_query = select(Cliente).where(Cliente.id == data.cliente_id)
        cliente = await self.db.scalar(cliente_query)
        if not cliente:
            raise ValueError("Cliente não encontrado")

        # Verifica se placa já existe
        existing = await self.get_by_placa(data.placa)
        if existing:
            raise ValueError("Placa já cadastrada no sistema")

        veiculo = Veiculo(
            cliente_id=data.cliente_id,
            placa=data.placa.upper(),
            marca=data.marca,
            modelo=data.modelo,
            ano=data.ano,
            tipo_cambio=data.tipo_cambio,
            quilometragem_atual=data.quilometragem_atual,
            cor=data.cor,
            observacoes=data.observacoes
        )

        self.db.add(veiculo)
        await self.db.flush()
        await self.db.refresh(veiculo)

        return veiculo

    async def update(self, veiculo_id: int, data: VeiculoUpdate) -> Veiculo:
        """Atualiza um veículo existente."""
        veiculo = await self.get_by_id(veiculo_id)
        if not veiculo:
            raise ValueError("Veículo não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        # Se está mudando de cliente, verifica se novo cliente existe
        if "cliente_id" in update_data:
            cliente_query = select(Cliente).where(Cliente.id == update_data["cliente_id"])
            cliente = await self.db.scalar(cliente_query)
            if not cliente:
                raise ValueError("Cliente não encontrado")

        for field, value in update_data.items():
            setattr(veiculo, field, value)

        await self.db.flush()
        await self.db.refresh(veiculo)

        return veiculo

    async def update_quilometragem(self, veiculo_id: int, km: int) -> Veiculo:
        """Atualiza apenas a quilometragem."""
        veiculo = await self.get_by_id(veiculo_id)
        if not veiculo:
            raise ValueError("Veículo não encontrado")

        if km < veiculo.quilometragem_atual:
            raise ValueError("Quilometragem não pode ser menor que a atual")

        veiculo.quilometragem_atual = km
        await self.db.flush()
        await self.db.refresh(veiculo)

        return veiculo

    async def delete(self, veiculo_id: int) -> bool:
        """Desativa um veículo (soft delete). Preserva histórico de trocas."""
        veiculo = await self.get_by_id(veiculo_id)
        if not veiculo:
            raise ValueError("Veículo não encontrado")

        veiculo.ativo = False
        await self.db.flush()

        return True
