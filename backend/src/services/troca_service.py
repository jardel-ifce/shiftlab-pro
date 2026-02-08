"""
Serviço de Troca de Óleo - ShiftLab Pro.

Contém a lógica de negócio principal do sistema.
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.domain.cliente import Cliente
from src.domain.item_troca import ItemTroca
from src.domain.oleo import Oleo
from src.domain.peca import Peca
from src.domain.troca_oleo import TrocaOleo
from src.domain.veiculo import Veiculo
from src.schemas.troca_oleo import (
    ProximasTrocasResponse,
    TrocaOleoCreate,
    TrocaOleoListResponse,
    TrocaOleoResponse,
    TrocaOleoUpdate,
)


class TrocaOleoService:
    """Serviço para gerenciamento de trocas de óleo."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, troca_id: int) -> TrocaOleo | None:
        """Busca troca por ID com relacionamentos."""
        query = (
            select(TrocaOleo)
            .options(
                selectinload(TrocaOleo.veiculo).selectinload(Veiculo.cliente),
                selectinload(TrocaOleo.oleo),
                selectinload(TrocaOleo.user),
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.peca),
            )
            .where(TrocaOleo.id == troca_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_veiculo(self, veiculo_id: int) -> list[TrocaOleo]:
        """Lista trocas de um veículo (histórico)."""
        query = (
            select(TrocaOleo)
            .options(selectinload(TrocaOleo.oleo))
            .where(TrocaOleo.veiculo_id == veiculo_id)
            .order_by(TrocaOleo.data_troca.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        veiculo_id: int | None = None,
        cliente_id: int | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> TrocaOleoListResponse:
        """Lista trocas com filtros."""
        query = select(TrocaOleo)

        if veiculo_id:
            query = query.where(TrocaOleo.veiculo_id == veiculo_id)

        if cliente_id:
            query = query.join(Veiculo).where(Veiculo.cliente_id == cliente_id)

        if data_inicio:
            query = query.where(TrocaOleo.data_troca >= data_inicio)

        if data_fim:
            query = query.where(TrocaOleo.data_troca <= data_fim)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Paginação
        query = (
            query.options(
                selectinload(TrocaOleo.veiculo).selectinload(Veiculo.cliente),
                selectinload(TrocaOleo.oleo),
                selectinload(TrocaOleo.user),
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.peca),
            )
            .offset(skip)
            .limit(limit)
            .order_by(TrocaOleo.data_troca.desc())
        )
        result = await self.db.execute(query)
        trocas = result.scalars().all()

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return TrocaOleoListResponse(
            items=[TrocaOleoResponse.model_validate(t) for t in trocas],
            total=total,
            page=page,
            pages=pages
        )

    async def create(self, data: TrocaOleoCreate, user_id: int | None = None) -> TrocaOleo:
        """Registra uma nova troca de óleo."""
        # Verifica veículo
        veiculo_query = select(Veiculo).where(Veiculo.id == data.veiculo_id)
        veiculo = await self.db.scalar(veiculo_query)
        if not veiculo:
            raise ValueError("Veículo não encontrado")

        # Verifica óleo
        oleo_query = select(Oleo).where(Oleo.id == data.oleo_id)
        oleo = await self.db.scalar(oleo_query)
        if not oleo:
            raise ValueError("Óleo não encontrado")
        if not oleo.ativo:
            raise ValueError("Este óleo está inativo")

        # Verifica estoque do óleo
        if oleo.estoque_litros < data.quantidade_litros:
            raise ValueError(f"Estoque insuficiente. Disponível: {oleo.estoque_litros}L")

        # Valida quilometragem
        if data.quilometragem_troca < veiculo.quilometragem_atual:
            raise ValueError("Quilometragem não pode ser menor que a atual do veículo")

        # Valida peças e calcula valor total das peças
        pecas_to_deduct: list[tuple[Peca, Decimal]] = []
        valor_pecas = Decimal("0")

        for item_data in data.itens:
            peca_query = select(Peca).where(Peca.id == item_data.peca_id)
            peca = await self.db.scalar(peca_query)
            if not peca:
                raise ValueError(f"Peça ID {item_data.peca_id} não encontrada")
            if not peca.ativo:
                raise ValueError(f"Peça '{peca.nome}' está inativa")
            if peca.estoque < item_data.quantidade:
                raise ValueError(
                    f"Estoque insuficiente para '{peca.nome}'. "
                    f"Disponível: {peca.estoque}, Solicitado: {item_data.quantidade}"
                )
            item_total = item_data.quantidade * item_data.valor_unitario
            valor_pecas += item_total
            pecas_to_deduct.append((peca, item_data.quantidade))

        # Calcula valor total com descontos (agora inclui peças)
        subtotal = data.valor_oleo + data.valor_servico + valor_pecas
        desconto_perc = subtotal * (data.desconto_percentual / 100)
        valor_total = subtotal - desconto_perc - data.desconto_valor

        if valor_total < 0:
            valor_total = Decimal("0")

        # Cria a troca
        troca = TrocaOleo(
            veiculo_id=data.veiculo_id,
            oleo_id=data.oleo_id,
            user_id=user_id,
            data_troca=data.data_troca,
            quilometragem_troca=data.quilometragem_troca,
            quantidade_litros=data.quantidade_litros,
            valor_oleo=data.valor_oleo,
            valor_servico=data.valor_servico,
            desconto_percentual=data.desconto_percentual,
            desconto_valor=data.desconto_valor,
            motivo_desconto=data.motivo_desconto,
            valor_total=valor_total,
            proxima_troca_km=data.proxima_troca_km,
            proxima_troca_data=data.proxima_troca_data,
            observacoes=data.observacoes
        )

        self.db.add(troca)

        # Atualiza quilometragem do veículo
        veiculo.quilometragem_atual = data.quilometragem_troca

        # Baixa estoque do óleo
        oleo.estoque_litros -= data.quantidade_litros

        # Cria itens e baixa estoque das peças
        for i, item_data in enumerate(data.itens):
            peca_obj, quantidade = pecas_to_deduct[i]
            item = ItemTroca(
                troca=troca,
                peca_id=item_data.peca_id,
                quantidade=item_data.quantidade,
                valor_unitario=item_data.valor_unitario,
                valor_total=item_data.quantidade * item_data.valor_unitario,
            )
            self.db.add(item)
            peca_obj.estoque -= quantidade

        await self.db.flush()

        # Recarrega com todos os relacionamentos (itens.peca, veiculo, oleo, etc.)
        troca = await self.get_by_id(troca.id)
        return troca

    async def update(self, troca_id: int, data: TrocaOleoUpdate) -> TrocaOleo:
        """Atualiza uma troca existente."""
        troca = await self.get_by_id(troca_id)
        if not troca:
            raise ValueError("Troca não encontrada")

        update_data = data.model_dump(exclude_unset=True)

        # Separa itens do update_data
        new_items_data = update_data.pop("itens", None)

        # Se mudou o óleo, verifica se existe
        if "oleo_id" in update_data:
            oleo_query = select(Oleo).where(Oleo.id == update_data["oleo_id"])
            oleo = await self.db.scalar(oleo_query)
            if not oleo:
                raise ValueError("Óleo não encontrado")

        # Gerencia substituição de itens (replace-all strategy)
        valor_pecas = Decimal("0")
        if new_items_data is not None:
            # Restaura estoque dos itens antigos
            for old_item in troca.itens:
                peca_query = select(Peca).where(Peca.id == old_item.peca_id)
                peca = await self.db.scalar(peca_query)
                if peca:
                    peca.estoque += old_item.quantidade
                await self.db.delete(old_item)

            # Valida e cria novos itens
            for item_dict in new_items_data:
                peca_query = select(Peca).where(Peca.id == item_dict["peca_id"])
                peca = await self.db.scalar(peca_query)
                if not peca:
                    raise ValueError(f"Peça ID {item_dict['peca_id']} não encontrada")
                if not peca.ativo:
                    raise ValueError(f"Peça '{peca.nome}' está inativa")

                qty = Decimal(str(item_dict["quantidade"]))
                unit_price = Decimal(str(item_dict["valor_unitario"]))

                if peca.estoque < qty:
                    raise ValueError(f"Estoque insuficiente para '{peca.nome}'")

                item_total = qty * unit_price
                valor_pecas += item_total

                item = ItemTroca(
                    troca=troca,
                    peca_id=item_dict["peca_id"],
                    quantidade=qty,
                    valor_unitario=unit_price,
                    valor_total=item_total,
                )
                self.db.add(item)
                peca.estoque -= qty
        else:
            # Itens não alterados — soma existentes para recálculo do total
            for existing_item in troca.itens:
                valor_pecas += existing_item.valor_total

        # Recalcula valor total se necessário
        campos_valor = ["valor_oleo", "valor_servico", "desconto_percentual", "desconto_valor"]
        if any(campo in update_data for campo in campos_valor) or new_items_data is not None:
            valor_oleo = update_data.get("valor_oleo", troca.valor_oleo)
            valor_servico = update_data.get("valor_servico", troca.valor_servico)
            desc_perc = update_data.get("desconto_percentual", troca.desconto_percentual)
            desc_valor = update_data.get("desconto_valor", troca.desconto_valor)

            subtotal = valor_oleo + valor_servico + valor_pecas
            desconto_perc = subtotal * (desc_perc / 100)
            valor_total = subtotal - desconto_perc - desc_valor

            if valor_total < 0:
                valor_total = Decimal("0")

            update_data["valor_total"] = valor_total

        for field, value in update_data.items():
            setattr(troca, field, value)

        await self.db.flush()

        troca = await self.get_by_id(troca_id)
        return troca

    async def delete(self, troca_id: int) -> bool:
        """Remove uma troca (não recomendado - perde histórico)."""
        troca = await self.get_by_id(troca_id)
        if not troca:
            raise ValueError("Troca não encontrada")

        # Devolve estoque do óleo
        oleo_query = select(Oleo).where(Oleo.id == troca.oleo_id)
        oleo = await self.db.scalar(oleo_query)
        if oleo:
            oleo.estoque_litros += troca.quantidade_litros

        # Devolve estoque das peças
        for item in troca.itens:
            peca_query = select(Peca).where(Peca.id == item.peca_id)
            peca = await self.db.scalar(peca_query)
            if peca:
                peca.estoque += item.quantidade

        await self.db.delete(troca)
        await self.db.flush()

        return True

    async def get_proximas_trocas(
        self,
        dias_alerta: int = 30,
        km_alerta: int = 1000
    ) -> list[ProximasTrocasResponse]:
        """Lista veículos que precisam de troca em breve."""
        hoje = date.today()
        data_limite = hoje + timedelta(days=dias_alerta)

        # Busca última troca de cada veículo
        subquery = (
            select(
                TrocaOleo.veiculo_id,
                func.max(TrocaOleo.data_troca).label("ultima_troca")
            )
            .group_by(TrocaOleo.veiculo_id)
            .subquery()
        )

        query = (
            select(TrocaOleo, Veiculo, Cliente)
            .join(subquery, (TrocaOleo.veiculo_id == subquery.c.veiculo_id) &
                           (TrocaOleo.data_troca == subquery.c.ultima_troca))
            .join(Veiculo, TrocaOleo.veiculo_id == Veiculo.id)
            .join(Cliente, Veiculo.cliente_id == Cliente.id)
            .where(
                (TrocaOleo.proxima_troca_data <= data_limite) |
                ((Veiculo.quilometragem_atual + km_alerta) >= TrocaOleo.proxima_troca_km)
            )
        )

        result = await self.db.execute(query)
        rows = result.all()

        alertas = []
        for troca, veiculo, cliente in rows:
            dias_restantes = None
            km_restantes = None
            urgente = False

            if troca.proxima_troca_data:
                dias_restantes = (troca.proxima_troca_data - hoje).days
                if dias_restantes <= 0:
                    urgente = True

            if troca.proxima_troca_km:
                km_restantes = troca.proxima_troca_km - veiculo.quilometragem_atual
                if km_restantes <= 0:
                    urgente = True

            alertas.append(ProximasTrocasResponse(
                veiculo_id=veiculo.id,
                placa=veiculo.placa,
                modelo=veiculo.nome_completo,
                cliente_nome=cliente.nome,
                ultima_troca=troca.data_troca,
                proxima_troca_km=troca.proxima_troca_km,
                proxima_troca_data=troca.proxima_troca_data,
                km_atual=veiculo.quilometragem_atual,
                dias_restantes=dias_restantes,
                km_restantes=km_restantes,
                urgente=urgente
            ))

        # Ordena por urgência (vencidos primeiro)
        alertas.sort(key=lambda x: (not x.urgente, x.dias_restantes or 999))

        return alertas

    async def get_estatisticas(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> dict:
        """Retorna estatísticas de trocas."""
        query = select(TrocaOleo)

        if data_inicio:
            query = query.where(TrocaOleo.data_troca >= data_inicio)
        if data_fim:
            query = query.where(TrocaOleo.data_troca <= data_fim)

        # Total de trocas
        count_query = select(func.count()).select_from(query.subquery())
        total_trocas = await self.db.scalar(count_query) or 0

        # Soma dos valores
        soma_query = select(
            func.sum(TrocaOleo.valor_total),
            func.sum(TrocaOleo.valor_oleo),
            func.sum(TrocaOleo.valor_servico),
            func.sum(TrocaOleo.quantidade_litros)
        ).select_from(query.subquery())

        result = await self.db.execute(soma_query)
        row = result.one()

        return {
            "total_trocas": total_trocas,
            "faturamento_total": float(row[0] or 0),
            "total_oleo": float(row[1] or 0),
            "total_servico": float(row[2] or 0),
            "litros_utilizados": float(row[3] or 0),
            "ticket_medio": float(row[0] or 0) / total_trocas if total_trocas > 0 else 0
        }
