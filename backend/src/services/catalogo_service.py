"""
Serviço de Catálogo de Veículos - ShiftLab Pro.

Contém a lógica de negócio para gerenciamento do catálogo
de montadoras e modelos de referência.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.modelo_referencia import ModeloReferencia
from src.domain.montadora import Montadora
from src.schemas.modelo_referencia import ModeloReferenciaCreate, ModeloReferenciaUpdate
from src.schemas.montadora import MontadoraCreate, MontadoraUpdate


class CatalogoService:
    """Serviço para gerenciamento do catálogo de veículos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # MONTADORAS
    # =========================================================================

    async def get_montadoras(self, apenas_ativas: bool = True) -> list[Montadora]:
        """Lista todas as montadoras ordenadas alfabeticamente."""
        query = select(Montadora).order_by(Montadora.nome)

        if apenas_ativas:
            query = query.where(Montadora.ativo == True)  # noqa: E712

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_montadora_by_id(self, montadora_id: int) -> Montadora | None:
        """Busca montadora por ID com seus modelos."""
        query = (
            select(Montadora)
            .options(selectinload(Montadora.modelos))
            .where(Montadora.id == montadora_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_montadora(self, data: MontadoraCreate) -> Montadora:
        """Cria uma nova montadora."""
        existing = await self.db.execute(
            select(Montadora).where(Montadora.nome == data.nome.upper())
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Montadora '{data.nome}' já existe")

        montadora = Montadora(
            nome=data.nome.upper(),
            pais_origem=data.pais_origem,
            ativo=True,
        )

        self.db.add(montadora)
        await self.db.flush()
        await self.db.refresh(montadora)

        return montadora

    async def update_montadora(self, montadora_id: int, data: MontadoraUpdate) -> Montadora:
        """Atualiza uma montadora existente."""
        montadora = await self.get_montadora_by_id(montadora_id)
        if not montadora:
            raise ValueError("Montadora não encontrada")

        update_data = data.model_dump(exclude_unset=True)

        if "nome" in update_data:
            update_data["nome"] = update_data["nome"].upper()

        for field, value in update_data.items():
            setattr(montadora, field, value)

        await self.db.flush()
        await self.db.refresh(montadora)

        return montadora

    # =========================================================================
    # MODELOS DE REFERÊNCIA
    # =========================================================================

    async def get_modelos_by_montadora(
        self, montadora_id: int, apenas_ativos: bool = True
    ) -> list[ModeloReferencia]:
        """Lista modelos de uma montadora específica."""
        query = (
            select(ModeloReferencia)
            .where(ModeloReferencia.montadora_id == montadora_id)
            .order_by(ModeloReferencia.nome, ModeloReferencia.ano_inicio)
        )

        if apenas_ativos:
            query = query.where(ModeloReferencia.ativo == True)  # noqa: E712

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_modelos(self, search: str, limit: int = 20) -> list[ModeloReferencia]:
        """Busca modelos por texto em todas as montadoras."""
        search_term = f"%{search}%"
        query = (
            select(ModeloReferencia)
            .where(ModeloReferencia.ativo == True)  # noqa: E712
            .where(
                (ModeloReferencia.nome.ilike(search_term)) |
                (ModeloReferencia.descricao.ilike(search_term))
            )
            .order_by(ModeloReferencia.nome)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_modelo_by_id(self, modelo_id: int) -> ModeloReferencia | None:
        """Busca modelo por ID."""
        query = select(ModeloReferencia).where(ModeloReferencia.id == modelo_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_modelo(self, data: ModeloReferenciaCreate) -> ModeloReferencia:
        """Cria um novo modelo de referência."""
        montadora = await self.db.execute(
            select(Montadora).where(Montadora.id == data.montadora_id)
        )
        if not montadora.scalar_one_or_none():
            raise ValueError("Montadora não encontrada")

        modelo = ModeloReferencia(
            montadora_id=data.montadora_id,
            nome=data.nome.upper(),
            descricao=data.descricao.upper(),
            tipo_cambio=data.tipo_cambio,
            ano_inicio=data.ano_inicio,
            ano_fim=data.ano_fim,
            motor=data.motor,
            observacoes=data.observacoes,
            ativo=True,
        )

        self.db.add(modelo)
        await self.db.flush()
        await self.db.refresh(modelo)

        return modelo

    async def update_modelo(self, modelo_id: int, data: ModeloReferenciaUpdate) -> ModeloReferencia:
        """Atualiza um modelo de referência existente."""
        modelo = await self.get_modelo_by_id(modelo_id)
        if not modelo:
            raise ValueError("Modelo não encontrado")

        update_data = data.model_dump(exclude_unset=True)

        if "nome" in update_data and update_data["nome"]:
            update_data["nome"] = update_data["nome"].upper()
        if "descricao" in update_data and update_data["descricao"]:
            update_data["descricao"] = update_data["descricao"].upper()

        for field, value in update_data.items():
            setattr(modelo, field, value)

        await self.db.flush()
        await self.db.refresh(modelo)

        return modelo
