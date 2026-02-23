"""
Serviço de Entradas de Estoque - ShiftLab Pro.

Registra compras de qualquer produto (óleo, filtro, peça),
atualiza estoque e custo médio automaticamente.
"""

from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entrada_estoque import EntradaEstoque
from src.domain.filtro import FiltroOleo
from src.domain.oleo import Oleo
from src.domain.peca import Peca
from src.schemas.entrada_estoque import (
    EntradaEstoqueCreate,
    EntradaEstoqueListResponse,
    EntradaEstoqueResponse,
    ProdutoBuscaResponse,
)


class EntradaEstoqueService:
    """Serviço para gerenciamento de entradas de estoque."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, entrada_id: int) -> EntradaEstoque | None:
        query = select(EntradaEstoque).where(EntradaEstoque.id == entrada_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        oleo_id: int | None = None,
    ) -> EntradaEstoqueListResponse:
        query = select(EntradaEstoque)

        if oleo_id:
            query = query.where(EntradaEstoque.oleo_id == oleo_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset(skip).limit(limit).order_by(EntradaEstoque.data_compra.desc())
        result = await self.db.execute(query)
        entradas = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return EntradaEstoqueListResponse(
            items=[self._to_response(e) for e in entradas],
            total=total,
            page=page,
            pages=pages,
        )

    async def _get_produto(self, tipo: str, produto_id: int):
        """Busca o produto pelo tipo e ID."""
        if tipo == "oleo":
            return await self.db.get(Oleo, produto_id)
        elif tipo == "filtro":
            return await self.db.get(FiltroOleo, produto_id)
        elif tipo == "peca":
            return await self.db.get(Peca, produto_id)
        return None

    async def create(self, data: EntradaEstoqueCreate) -> EntradaEstoque:
        """Cria entrada e atualiza estoque + custo do produto."""
        produto = await self._get_produto(data.tipo_produto, data.produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        custo_total = data.quantidade_litros * data.custo_unitario

        entrada = EntradaEstoque(
            tipo_produto=data.tipo_produto,
            produto_id=data.produto_id,
            produto_nome=produto.nome,
            produto_marca=produto.marca or "",
            oleo_id=data.produto_id if data.tipo_produto == "oleo" else None,
            quantidade_litros=data.quantidade_litros,
            custo_unitario=data.custo_unitario,
            custo_total=custo_total,
            fornecedor=data.fornecedor,
            nota_fiscal=data.nota_fiscal,
            data_compra=data.data_compra,
            observacoes=data.observacoes,
        )

        self.db.add(entrada)

        # Atualiza estoque e custo médio do produto
        if data.tipo_produto == "oleo":
            estoque_atual = produto.estoque_litros or Decimal("0")
            custo_atual = produto.custo_litro or Decimal("0")
            total_valor = (estoque_atual * custo_atual) + custo_total
            novo_estoque = estoque_atual + data.quantidade_litros
            if novo_estoque > 0:
                produto.custo_litro = total_valor / novo_estoque
            produto.estoque_litros = novo_estoque

        elif data.tipo_produto == "filtro":
            qtd = int(data.quantidade_litros)
            estoque_atual = produto.estoque or 0
            custo_atual = produto.custo_unitario or Decimal("0")
            total_valor = (Decimal(estoque_atual) * custo_atual) + custo_total
            novo_estoque = estoque_atual + qtd
            if novo_estoque > 0:
                produto.custo_unitario = total_valor / Decimal(novo_estoque)
            produto.estoque = novo_estoque

        elif data.tipo_produto == "peca":
            estoque_atual = produto.estoque or Decimal("0")
            custo_atual = produto.preco_custo or Decimal("0")
            total_valor = (estoque_atual * custo_atual) + custo_total
            novo_estoque = estoque_atual + data.quantidade_litros
            if novo_estoque > 0:
                produto.preco_custo = total_valor / novo_estoque
            produto.estoque = novo_estoque

        await self.db.flush()
        await self.db.refresh(entrada)

        return entrada

    async def delete(self, entrada_id: int) -> bool:
        """Remove entrada e reverte estoque."""
        entrada = await self.get_by_id(entrada_id)
        if not entrada:
            raise ValueError("Entrada não encontrada")

        produto = await self._get_produto(entrada.tipo_produto, entrada.produto_id)
        if produto:
            if entrada.tipo_produto == "oleo":
                produto.estoque_litros = max(
                    Decimal("0"),
                    produto.estoque_litros - entrada.quantidade_litros,
                )
            elif entrada.tipo_produto == "filtro":
                produto.estoque = max(0, produto.estoque - int(entrada.quantidade_litros))
            elif entrada.tipo_produto == "peca":
                produto.estoque = max(
                    Decimal("0"),
                    produto.estoque - entrada.quantidade_litros,
                )

        await self.db.delete(entrada)
        await self.db.flush()

        return True

    async def buscar_produtos(
        self, q: str, tipo: str | None = None, limit: int = 10
    ) -> list[ProdutoBuscaResponse]:
        """Busca produtos por nome ou código."""
        resultados: list[ProdutoBuscaResponse] = []
        search_term = f"%{q}%"

        tipos = [tipo] if tipo else ["oleo", "filtro", "peca"]

        for t in tipos:
            if t == "oleo":
                query = (
                    select(Oleo)
                    .where(Oleo.ativo == True)  # noqa: E712
                    .where(or_(
                        Oleo.nome.ilike(search_term),
                        Oleo.marca.ilike(search_term),
                        Oleo.codigo_produto.ilike(search_term),
                    ))
                    .limit(limit)
                )
                result = await self.db.execute(query)
                for o in result.scalars().all():
                    cod = f"[{o.codigo_produto}] " if o.codigo_produto else ""
                    resultados.append(ProdutoBuscaResponse(
                        tipo="oleo", id=o.id,
                        codigo_produto=o.codigo_produto,
                        nome=o.nome, marca=o.marca,
                        label=f"{cod}{o.marca} {o.nome}",
                    ))

            elif t == "filtro":
                query = (
                    select(FiltroOleo)
                    .where(FiltroOleo.ativo == True)  # noqa: E712
                    .where(or_(
                        FiltroOleo.nome.ilike(search_term),
                        FiltroOleo.marca.ilike(search_term),
                        FiltroOleo.codigo_produto.ilike(search_term),
                        FiltroOleo.codigo_oem.ilike(search_term),
                    ))
                    .limit(limit)
                )
                result = await self.db.execute(query)
                for f in result.scalars().all():
                    cod = f"[{f.codigo_produto}] " if f.codigo_produto else ""
                    resultados.append(ProdutoBuscaResponse(
                        tipo="filtro", id=f.id,
                        codigo_produto=f.codigo_produto,
                        nome=f.nome, marca=f.marca,
                        label=f"{cod}{f.marca} {f.nome}",
                    ))

            elif t == "peca":
                query = (
                    select(Peca)
                    .where(Peca.ativo == True)  # noqa: E712
                    .where(or_(
                        Peca.nome.ilike(search_term),
                        Peca.marca.ilike(search_term),
                    ))
                    .limit(limit)
                )
                result = await self.db.execute(query)
                for p in result.scalars().all():
                    marca = f"{p.marca} " if p.marca else ""
                    resultados.append(ProdutoBuscaResponse(
                        tipo="peca", id=p.id,
                        codigo_produto=None,
                        nome=p.nome, marca=p.marca or "",
                        label=f"{marca}{p.nome}",
                    ))

        return resultados[:limit]

    def _to_response(self, entrada: EntradaEstoque) -> EntradaEstoqueResponse:
        return EntradaEstoqueResponse(
            id=entrada.id,
            tipo_produto=entrada.tipo_produto,
            produto_id=entrada.produto_id,
            produto_nome=entrada.produto_nome,
            produto_marca=entrada.produto_marca,
            quantidade_litros=entrada.quantidade_litros,
            custo_unitario=entrada.custo_unitario,
            custo_total=entrada.custo_total,
            fornecedor=entrada.fornecedor,
            nota_fiscal=entrada.nota_fiscal,
            data_compra=entrada.data_compra,
            observacoes=entrada.observacoes,
            created_at=entrada.created_at,
            updated_at=entrada.updated_at,
        )
