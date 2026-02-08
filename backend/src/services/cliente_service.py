"""
Serviço de Clientes - ShiftLab Pro.

Contém a lógica de negócio para operações com clientes.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteListResponse, ClienteResponse, ClienteUpdate


class ClienteService:
    """Serviço para gerenciamento de clientes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, cliente_id: int) -> Cliente | None:
        """Busca cliente por ID."""
        query = select(Cliente).where(Cliente.id == cliente_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Cliente | None:
        """Busca cliente por CPF/CNPJ."""
        query = select(Cliente).where(Cliente.cpf_cnpj == cpf_cnpj)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None
    ) -> ClienteListResponse:
        """Lista clientes com paginação e busca."""
        query = select(Cliente)

        # Busca por nome, telefone ou CPF/CNPJ
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Cliente.nome.ilike(search_term)) |
                (Cliente.telefone.ilike(search_term)) |
                (Cliente.cpf_cnpj.ilike(search_term))
            )

        # Total de registros
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(Cliente.nome)
        result = await self.db.execute(query)
        clientes = result.scalars().all()

        # Calcula páginas
        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return ClienteListResponse(
            items=[ClienteResponse.model_validate(c) for c in clientes],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: ClienteCreate) -> Cliente:
        """Cria um novo cliente."""
        # Verifica se CPF/CNPJ já existe
        existing = await self.get_by_cpf_cnpj(data.cpf_cnpj)
        if existing:
            raise ValueError("CPF/CNPJ já cadastrado no sistema")

        cliente = Cliente(
            nome=data.nome,
            telefone=data.telefone,
            email=data.email,
            cpf_cnpj=data.cpf_cnpj,
            endereco=data.endereco,
            observacoes=data.observacoes
        )

        self.db.add(cliente)
        await self.db.flush()
        await self.db.refresh(cliente)

        return cliente

    async def update(self, cliente_id: int, data: ClienteUpdate) -> Cliente:
        """Atualiza um cliente existente."""
        cliente = await self.get_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(cliente, field, value)

        await self.db.flush()
        await self.db.refresh(cliente)

        return cliente

    async def delete(self, cliente_id: int) -> bool:
        """Remove um cliente (e seus veículos em cascata)."""
        cliente = await self.get_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado")

        await self.db.delete(cliente)
        await self.db.flush()

        return True
