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
from src.domain.filtro import FiltroOleo
from src.schemas.troca_oleo import (
    FinanceiroListResponse,
    FinanceiroResumoResponse,
    ItemTrocaFinanceiroResponse,
    ProdutoFinanceiroListResponse,
    ProdutoFinanceiroResponse,
    ProximasTrocasResponse,
    TrocaFinanceiroResponse,
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
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.filtro),
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
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.filtro),
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

        # Valida itens (peças e filtros) e calcula valor total
        items_to_deduct: list[tuple] = []  # (obj, quantidade, tipo)
        valor_pecas = Decimal("0")

        for item_data in data.itens:
            if item_data.peca_id:
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
                items_to_deduct.append((peca, item_data.quantidade, "peca"))
            elif item_data.filtro_id:
                filtro_query = select(FiltroOleo).where(FiltroOleo.id == item_data.filtro_id)
                filtro = await self.db.scalar(filtro_query)
                if not filtro:
                    raise ValueError(f"Filtro ID {item_data.filtro_id} não encontrado")
                if not filtro.ativo:
                    raise ValueError(f"Filtro '{filtro.nome}' está inativo")
                if filtro.estoque < item_data.quantidade:
                    raise ValueError(
                        f"Estoque insuficiente para '{filtro.nome}'. "
                        f"Disponível: {filtro.estoque}, Solicitado: {item_data.quantidade}"
                    )
                items_to_deduct.append((filtro, item_data.quantidade, "filtro"))

            item_total = item_data.quantidade * item_data.valor_unitario
            valor_pecas += item_total

        # Calcula valor total com descontos e taxa
        subtotal = data.valor_oleo + data.valor_servico + valor_pecas
        desconto_perc = subtotal * (data.desconto_percentual / 100)
        subtotal_com_desconto = subtotal - desconto_perc - data.desconto_valor
        taxa_valor = subtotal_com_desconto * (data.taxa_percentual / 100)
        valor_total = subtotal_com_desconto - taxa_valor

        if valor_total < 0:
            valor_total = Decimal("0")

        # Cria a troca (com snapshot do custo do óleo)
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
            taxa_percentual=data.taxa_percentual,
            valor_total=valor_total,
            custo_oleo=oleo.custo_litro * data.quantidade_litros,
            proxima_troca_km=data.proxima_troca_km,
            proxima_troca_data=data.proxima_troca_data,
            observacoes=data.observacoes
        )

        self.db.add(troca)

        # Atualiza quilometragem do veículo
        veiculo.quilometragem_atual = data.quilometragem_troca

        # Baixa estoque do óleo
        oleo.estoque_litros -= data.quantidade_litros

        # Cria itens e baixa estoque (com snapshot do custo)
        for i, item_data in enumerate(data.itens):
            obj, quantidade, tipo = items_to_deduct[i]
            custo = obj.preco_custo if tipo == "peca" else obj.custo_unitario
            item = ItemTroca(
                troca=troca,
                peca_id=item_data.peca_id,
                filtro_id=item_data.filtro_id,
                quantidade=item_data.quantidade,
                valor_unitario=item_data.valor_unitario,
                valor_total=item_data.quantidade * item_data.valor_unitario,
                custo_unitario=custo,
            )
            self.db.add(item)
            obj.estoque -= quantidade

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
                if old_item.peca_id:
                    peca = await self.db.scalar(select(Peca).where(Peca.id == old_item.peca_id))
                    if peca:
                        peca.estoque += old_item.quantidade
                elif old_item.filtro_id:
                    filtro = await self.db.scalar(select(FiltroOleo).where(FiltroOleo.id == old_item.filtro_id))
                    if filtro:
                        filtro.estoque += int(old_item.quantidade)
                await self.db.delete(old_item)

            # Valida e cria novos itens
            for item_dict in new_items_data:
                peca_id = item_dict.get("peca_id")
                filtro_id = item_dict.get("filtro_id")
                qty = Decimal(str(item_dict["quantidade"]))
                unit_price = Decimal(str(item_dict["valor_unitario"]))
                custo = Decimal("0")

                if peca_id:
                    peca = await self.db.scalar(select(Peca).where(Peca.id == peca_id))
                    if not peca:
                        raise ValueError(f"Peça ID {peca_id} não encontrada")
                    if not peca.ativo:
                        raise ValueError(f"Peça '{peca.nome}' está inativa")
                    if peca.estoque < qty:
                        raise ValueError(f"Estoque insuficiente para '{peca.nome}'")
                    custo = peca.preco_custo
                    peca.estoque -= qty
                elif filtro_id:
                    filtro = await self.db.scalar(select(FiltroOleo).where(FiltroOleo.id == filtro_id))
                    if not filtro:
                        raise ValueError(f"Filtro ID {filtro_id} não encontrado")
                    if not filtro.ativo:
                        raise ValueError(f"Filtro '{filtro.nome}' está inativo")
                    if filtro.estoque < qty:
                        raise ValueError(f"Estoque insuficiente para '{filtro.nome}'")
                    custo = filtro.custo_unitario
                    filtro.estoque -= int(qty)

                item_total = qty * unit_price
                valor_pecas += item_total

                item = ItemTroca(
                    troca=troca,
                    peca_id=peca_id,
                    filtro_id=filtro_id,
                    quantidade=qty,
                    valor_unitario=unit_price,
                    valor_total=item_total,
                    custo_unitario=custo,
                )
                self.db.add(item)
        else:
            # Itens não alterados — soma existentes para recálculo do total
            for existing_item in troca.itens:
                valor_pecas += existing_item.valor_total

        # Recalcula valor total se necessário
        campos_valor = ["valor_oleo", "valor_servico", "desconto_percentual", "desconto_valor", "taxa_percentual"]
        if any(campo in update_data for campo in campos_valor) or new_items_data is not None:
            valor_oleo = update_data.get("valor_oleo", troca.valor_oleo)
            valor_servico = update_data.get("valor_servico", troca.valor_servico)
            desc_perc = update_data.get("desconto_percentual", troca.desconto_percentual)
            desc_valor = update_data.get("desconto_valor", troca.desconto_valor)
            taxa_perc = update_data.get("taxa_percentual", troca.taxa_percentual)

            subtotal = valor_oleo + valor_servico + valor_pecas
            desconto_perc = subtotal * (desc_perc / 100)
            subtotal_com_desconto = subtotal - desconto_perc - desc_valor
            taxa_valor = subtotal_com_desconto * (taxa_perc / 100)
            valor_total = subtotal_com_desconto - taxa_valor

            if valor_total < 0:
                valor_total = Decimal("0")

            update_data["valor_total"] = valor_total

        # Recalcular custo_oleo se óleo ou quantidade mudou
        if "oleo_id" in update_data or "quantidade_litros" in update_data:
            oleo_id_final = update_data.get("oleo_id", troca.oleo_id)
            qtd_final = update_data.get("quantidade_litros", troca.quantidade_litros)
            oleo_q = select(Oleo).where(Oleo.id == oleo_id_final)
            oleo_obj = await self.db.scalar(oleo_q)
            if oleo_obj:
                update_data["custo_oleo"] = oleo_obj.custo_litro * qtd_final

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

        # Devolve estoque das peças e filtros
        for item in troca.itens:
            if item.peca_id:
                peca = await self.db.scalar(select(Peca).where(Peca.id == item.peca_id))
                if peca:
                    peca.estoque += item.quantidade
            elif item.filtro_id:
                filtro = await self.db.scalar(select(FiltroOleo).where(FiltroOleo.id == item.filtro_id))
                if filtro:
                    filtro.estoque += int(item.quantidade)

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

    async def get_financeiro(
        self,
        skip: int = 0,
        limit: int = 20,
        cliente_id: int | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        imposto_percentual: float = 0.0,
        despesas_total: float = 0.0,
    ) -> FinanceiroListResponse:
        """Retorna dados financeiros com lucro por troca."""
        # Base query com filtros
        base = select(TrocaOleo)

        if cliente_id:
            base = base.join(Veiculo).where(Veiculo.cliente_id == cliente_id)
        if data_inicio:
            base = base.where(TrocaOleo.data_troca >= data_inicio)
        if data_fim:
            base = base.where(TrocaOleo.data_troca <= data_fim)

        # Total count
        count_q = select(func.count()).select_from(base.subquery())
        total = await self.db.scalar(count_q) or 0

        # Agregação para resumo (custo_pecas precisa ser calculado via itens)
        agg_q = select(
            func.count(TrocaOleo.id),
            func.sum(TrocaOleo.valor_total),
            func.sum(TrocaOleo.custo_oleo),
        ).select_from(base.subquery())
        agg_result = await self.db.execute(agg_q)
        agg_row = agg_result.one()

        total_trocas = agg_row[0] or 0
        faturamento_total = float(agg_row[1] or 0)
        custo_oleo_total = float(agg_row[2] or 0)

        # Custo de peças total (via join com itens)
        custo_pecas_q = (
            select(func.sum(ItemTroca.custo_unitario * ItemTroca.quantidade))
            .join(TrocaOleo, ItemTroca.troca_id == TrocaOleo.id)
        )
        if cliente_id:
            custo_pecas_q = custo_pecas_q.join(
                Veiculo, TrocaOleo.veiculo_id == Veiculo.id
            ).where(Veiculo.cliente_id == cliente_id)
        if data_inicio:
            custo_pecas_q = custo_pecas_q.where(TrocaOleo.data_troca >= data_inicio)
        if data_fim:
            custo_pecas_q = custo_pecas_q.where(TrocaOleo.data_troca <= data_fim)

        custo_pecas_total = float(await self.db.scalar(custo_pecas_q) or 0)
        custo_total_geral = custo_oleo_total + custo_pecas_total
        lucro_bruto_total = faturamento_total - custo_total_geral
        margem_media = (
            (lucro_bruto_total / faturamento_total) * 100
            if faturamento_total > 0
            else 0
        )
        ticket_medio = faturamento_total / total_trocas if total_trocas > 0 else 0

        imposto_valor = faturamento_total * (imposto_percentual / 100)
        lucro_liquido = lucro_bruto_total - imposto_valor - despesas_total

        resumo = FinanceiroResumoResponse(
            total_trocas=total_trocas,
            faturamento_total=faturamento_total,
            custo_total=custo_total_geral,
            lucro_bruto_total=lucro_bruto_total,
            margem_media=round(margem_media, 1),
            ticket_medio=round(ticket_medio, 2),
            imposto_percentual=imposto_percentual,
            imposto_valor=round(imposto_valor, 2),
            despesas_total=round(despesas_total, 2),
            lucro_liquido=round(lucro_liquido, 2),
        )

        # Query paginada com relacionamentos
        detail_q = (
            base.options(
                selectinload(TrocaOleo.veiculo).selectinload(Veiculo.cliente),
                selectinload(TrocaOleo.oleo),
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.peca),
                selectinload(TrocaOleo.itens).selectinload(ItemTroca.filtro),
            )
            .offset(skip)
            .limit(limit)
            .order_by(TrocaOleo.data_troca.desc())
        )
        result = await self.db.execute(detail_q)
        trocas = result.scalars().all()

        items = []
        for t in trocas:
            cliente_nome = (
                t.veiculo.cliente.nome
                if t.veiculo and t.veiculo.cliente
                else None
            )
            veiculo_info = (
                f"{t.veiculo.placa} - {t.veiculo.marca} {t.veiculo.modelo}"
                if t.veiculo
                else None
            )
            oleo_nome = (
                f"{t.oleo.marca} {t.oleo.nome}" if t.oleo else None
            )

            itens_fin = []
            for item in t.itens:
                nome = None
                if item.peca:
                    nome = item.peca.nome
                elif item.filtro:
                    nome = item.filtro.nome
                itens_fin.append(ItemTrocaFinanceiroResponse(
                    id=item.id,
                    peca_nome=nome,
                    quantidade=item.quantidade,
                    valor_unitario=item.valor_unitario,
                    valor_total=item.valor_total,
                    custo_unitario=item.custo_unitario,
                    lucro_item=item.lucro_item,
                ))

            items.append(TrocaFinanceiroResponse(
                id=t.id,
                data_troca=t.data_troca,
                cliente_nome=cliente_nome,
                veiculo_info=veiculo_info,
                oleo_nome=oleo_nome,
                valor_oleo=t.valor_oleo,
                valor_servico=t.valor_servico,
                valor_total=t.valor_total,
                desconto_percentual=t.desconto_percentual,
                desconto_valor=t.desconto_valor,
                taxa_percentual=t.taxa_percentual,
                custo_oleo=t.custo_oleo,
                custo_pecas=t.custo_pecas,
                custo_total=t.custo_total,
                lucro_bruto=t.lucro_bruto,
                margem_lucro=t.margem_lucro,
                itens=itens_fin,
            ))

        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return FinanceiroListResponse(
            items=items,
            resumo=resumo,
            total=total,
            page=page,
            pages=pages,
        )

    async def get_financeiro_produtos(
        self,
        tipo: str | None = None,
    ) -> ProdutoFinanceiroListResponse:
        """Retorna dados financeiros unificados de todos os produtos."""
        items: list[ProdutoFinanceiroResponse] = []

        # Óleos
        if not tipo or tipo == "oleo":
            q = select(Oleo).where(Oleo.ativo.is_(True)).order_by(Oleo.nome)
            result = await self.db.execute(q)
            for o in result.scalars().all():
                custo = float(o.custo_litro)
                venda = float(o.preco_litro)
                lucro = venda - custo
                margem = ((lucro / custo) * 100) if custo > 0 else 0
                items.append(ProdutoFinanceiroResponse(
                    tipo="oleo",
                    id=o.id,
                    nome=o.nome,
                    marca=o.marca,
                    custo=custo,
                    preco_venda=venda,
                    lucro_unitario=round(lucro, 2),
                    margem_lucro=round(margem, 1),
                    estoque=float(o.estoque_litros),
                ))

        # Filtros
        if not tipo or tipo == "filtro":
            q = select(FiltroOleo).where(FiltroOleo.ativo.is_(True)).order_by(FiltroOleo.nome)
            result = await self.db.execute(q)
            for f in result.scalars().all():
                custo = float(f.custo_unitario)
                venda = float(f.preco_unitario)
                lucro = venda - custo
                margem = ((lucro / custo) * 100) if custo > 0 else 0
                items.append(ProdutoFinanceiroResponse(
                    tipo="filtro",
                    id=f.id,
                    nome=f.nome,
                    marca=f.marca,
                    custo=custo,
                    preco_venda=venda,
                    lucro_unitario=round(lucro, 2),
                    margem_lucro=round(margem, 1),
                    estoque=float(f.estoque),
                ))

        # Peças
        if not tipo or tipo == "peca":
            q = select(Peca).where(Peca.ativo.is_(True)).order_by(Peca.nome)
            result = await self.db.execute(q)
            for p in result.scalars().all():
                custo = float(p.preco_custo)
                venda = float(p.preco_venda)
                lucro = venda - custo
                margem = ((lucro / custo) * 100) if custo > 0 else 0
                items.append(ProdutoFinanceiroResponse(
                    tipo="peca",
                    id=p.id,
                    nome=p.nome,
                    marca=p.marca,
                    custo=custo,
                    preco_venda=venda,
                    lucro_unitario=round(lucro, 2),
                    margem_lucro=round(margem, 1),
                    estoque=float(p.estoque),
                ))

        return ProdutoFinanceiroListResponse(items=items)
