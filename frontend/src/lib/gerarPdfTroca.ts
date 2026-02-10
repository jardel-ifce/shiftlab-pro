import { jsPDF } from "jspdf"
import api from "@/lib/api"
import type { TrocaOleoDetail } from "@/types/troca"
import type { Cliente } from "@/types/cliente"

const R = (v: number | string) =>
  Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fmtDate = (d: string) => {
  const [y, m, day] = d.split("-")
  return `${day}/${m}/${y}`
}

export async function gerarPdfTroca(trocaId: number) {
  // Fetch troca detail + client
  const { data: troca } = await api.get<TrocaOleoDetail>(`/trocas/${trocaId}`)
  const { data: cliente } = await api.get<Cliente>(`/clientes/${troca.veiculo.cliente_id}`)

  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" })
  const W = 210
  const marginL = 15
  const marginR = 195
  const contentW = marginR - marginL
  let y = 15

  function box(x: number, yPos: number, w: number, h: number) {
    doc.setDrawColor(100)
    doc.setLineWidth(0.3)
    doc.rect(x, yPos, w, h)
  }

  // ─── HEADER ───
  box(marginL, y, contentW, 12)
  doc.setFontSize(14)
  doc.setFont("helvetica", "bold")
  doc.text("ORDEM DE SERVIÇO", W / 2, y + 7.5, { align: "center" })
  doc.setFontSize(9)
  doc.setFont("helvetica", "normal")
  doc.text(`Nº ${String(troca.id).padStart(5, "0")}`, marginR - 2, y + 5, { align: "right" })
  doc.text(fmtDate(troca.data_troca), marginR - 2, y + 10, { align: "right" })
  y += 12

  // ─── CLIENTE + VEÍCULO ───
  const halfW = contentW / 2

  // Client box
  box(marginL, y, halfW, 28)
  doc.setFontSize(7)
  doc.setFont("helvetica", "bold")
  doc.text("CLIENTE", marginL + 2, y + 4)
  doc.setFont("helvetica", "normal")
  doc.setFontSize(9)
  doc.text(cliente.nome, marginL + 2, y + 10)
  doc.setFontSize(8)
  doc.text(`CPF/CNPJ: ${cliente.cpf_cnpj}`, marginL + 2, y + 16)
  doc.text(`Tel: ${cliente.telefone}`, marginL + 2, y + 21)
  if (cliente.endereco) {
    doc.setFontSize(7)
    doc.text(`End: ${cliente.endereco}`, marginL + 2, y + 26)
  }

  // Vehicle box
  box(marginL + halfW, y, halfW, 28)
  doc.setFontSize(7)
  doc.setFont("helvetica", "bold")
  doc.text("VEÍCULO", marginL + halfW + 2, y + 4)
  doc.setFont("helvetica", "normal")
  doc.setFontSize(9)
  const v = troca.veiculo
  doc.text(`${v.placa} — ${v.marca} ${v.modelo} (${v.ano})`, marginL + halfW + 2, y + 10)
  doc.setFontSize(8)
  doc.text(`KM: ${troca.quilometragem_troca.toLocaleString("pt-BR")}`, marginL + halfW + 2, y + 16)
  doc.text(`Câmbio: ${v.tipo_cambio}`, marginL + halfW + 2, y + 21)
  if (v.cor) {
    doc.text(`Cor: ${v.cor}`, marginL + halfW + 2, y + 26)
  }
  y += 28

  // ─── TABELA DE PRODUTOS ───
  box(marginL, y, contentW, 7)
  doc.setFillColor(240, 240, 240)
  doc.rect(marginL, y, contentW, 7, "F")
  box(marginL, y, contentW, 7)
  doc.setFontSize(7)
  doc.setFont("helvetica", "bold")
  doc.text("PRODUTOS / SERVIÇOS", marginL + 2, y + 5)
  y += 7

  // Table header
  const cols = [10, 75, 15, 15, 25, 25] // widths: #, desc, unid, qtd, vunit, total
  const colX = [marginL]
  for (let i = 0; i < cols.length; i++) {
    colX.push(colX[i] + cols[i])
  }

  box(marginL, y, contentW, 6)
  doc.setFillColor(245, 245, 245)
  doc.rect(marginL, y, contentW, 6, "F")
  box(marginL, y, contentW, 6)
  doc.setFontSize(7)
  doc.setFont("helvetica", "bold")
  const headers = ["#", "Descrição", "Unid", "Qtd", "V. Unit", "Total"]
  headers.forEach((h, i) => {
    const align = i >= 4 ? "right" : i >= 2 ? "center" : "left"
    const xPos = align === "right" ? colX[i + 1] - 2 : align === "center" ? colX[i] + cols[i] / 2 : colX[i] + 2
    doc.text(h, xPos, y + 4, { align: align as "left" | "center" | "right" })
  })
  y += 6

  // Item rows
  doc.setFont("helvetica", "normal")
  doc.setFontSize(8)

  // Row 1: Oil
  const oleoTotal = Number(troca.valor_oleo)
  const oleoQtd = Number(troca.quantidade_litros)
  const oleoUnit = oleoQtd > 0 ? oleoTotal / oleoQtd : 0
  const rowH = 6
  let rowNum = 1

  box(marginL, y, contentW, rowH)
  doc.text(String(rowNum), colX[0] + 2, y + 4)
  const oleoDesc = `${troca.oleo.nome} (${troca.oleo.marca})${troca.oleo.tipo_oleo_transmissao ? ` - ${troca.oleo.tipo_oleo_transmissao}` : ""}`
  doc.text(oleoDesc, colX[1] + 2, y + 4)
  doc.text("L", colX[2] + cols[2] / 2, y + 4, { align: "center" })
  doc.text(oleoQtd.toFixed(1), colX[3] + cols[3] / 2, y + 4, { align: "center" })
  doc.text(`R$ ${R(oleoUnit)}`, colX[5] - 2, y + 4, { align: "right" })
  doc.text(`R$ ${R(oleoTotal)}`, colX[6] - 2, y + 4, { align: "right" })
  y += rowH

  // Peca rows
  for (const item of troca.itens) {
    rowNum++
    box(marginL, y, contentW, rowH)
    doc.text(String(rowNum), colX[0] + 2, y + 4)
    const pecaNome = item.peca ? `${item.peca.nome}${item.peca.marca ? ` (${item.peca.marca})` : ""}` : `Peça #${item.peca_id}`
    doc.text(pecaNome, colX[1] + 2, y + 4)
    doc.text(item.peca?.unidade || "un", colX[2] + cols[2] / 2, y + 4, { align: "center" })
    doc.text(Number(item.quantidade).toFixed(0), colX[3] + cols[3] / 2, y + 4, { align: "center" })
    doc.text(`R$ ${R(item.valor_unitario)}`, colX[5] - 2, y + 4, { align: "right" })
    doc.text(`R$ ${R(item.valor_total)}`, colX[6] - 2, y + 4, { align: "right" })
    y += rowH
  }

  y += 2

  // ─── TOTAIS ───
  const totaisX = marginL + contentW - 80
  box(marginL, y, contentW, 42)

  doc.setFontSize(8)
  const subtotalProdutos = Number(troca.valor_oleo) + troca.itens.reduce((acc, it) => acc + Number(it.valor_total), 0)
  const maoDeObra = Number(troca.valor_servico)
  const subtotalGeral = subtotalProdutos + maoDeObra
  const descPerc = subtotalGeral * (Number(troca.desconto_percentual) / 100)
  const descVal = Number(troca.desconto_valor)

  let ty = y + 6
  doc.text("Subtotal Produtos:", totaisX, ty)
  doc.text(`R$ ${R(subtotalProdutos)}`, marginR - 2, ty, { align: "right" })

  ty += 6
  doc.text("Mão de Obra:", totaisX, ty)
  doc.text(`R$ ${R(maoDeObra)}`, marginR - 2, ty, { align: "right" })

  if (Number(troca.desconto_percentual) > 0) {
    ty += 6
    doc.text(`Desconto (${Number(troca.desconto_percentual)}%):`, totaisX, ty)
    doc.text(`- R$ ${R(descPerc)}`, marginR - 2, ty, { align: "right" })
  }

  if (descVal > 0) {
    ty += 6
    doc.text("Desconto (R$):", totaisX, ty)
    doc.text(`- R$ ${R(descVal)}`, marginR - 2, ty, { align: "right" })
  }

  if (troca.motivo_desconto) {
    ty += 5
    doc.setFontSize(7)
    doc.text(`Motivo: ${troca.motivo_desconto}`, totaisX, ty)
    doc.setFontSize(8)
  }

  ty += 3
  doc.setLineWidth(0.3)
  doc.line(totaisX, ty, marginR, ty)

  ty += 6
  doc.setFontSize(10)
  doc.setFont("helvetica", "bold")
  doc.text("VALOR TOTAL:", totaisX, ty)
  doc.text(`R$ ${R(troca.valor_total)}`, marginR - 2, ty, { align: "right" })
  y += 42

  // ─── PRÓXIMA TROCA ───
  if (troca.proxima_troca_km || troca.proxima_troca_data) {
    box(marginL, y, contentW, 14)
    doc.setFontSize(7)
    doc.setFont("helvetica", "bold")
    doc.text("PRÓXIMA TROCA", marginL + 2, y + 5)
    doc.setFont("helvetica", "normal")
    doc.setFontSize(8)
    const parts: string[] = []
    if (troca.proxima_troca_km) parts.push(`KM: ${troca.proxima_troca_km.toLocaleString("pt-BR")}`)
    if (troca.proxima_troca_data) parts.push(`Data: ${fmtDate(troca.proxima_troca_data)}`)
    doc.text(parts.join("     |     "), marginL + 2, y + 11)
    y += 14
  }

  // ─── OBSERVAÇÕES ───
  if (troca.observacoes) {
    box(marginL, y, contentW, 18)
    doc.setFontSize(7)
    doc.setFont("helvetica", "bold")
    doc.text("OBSERVAÇÕES", marginL + 2, y + 5)
    doc.setFont("helvetica", "normal")
    doc.setFontSize(8)
    const lines = doc.splitTextToSize(troca.observacoes, contentW - 6)
    doc.text(lines, marginL + 2, y + 11)
    y += 18
  }

  // ─── FOOTER ───
  y += 10
  doc.setFontSize(7)
  doc.setTextColor(150)
  doc.text("ShiftLab Pro — Ordem de Serviço", W / 2, y, { align: "center" })

  // Download
  doc.save(`OS-${String(troca.id).padStart(5, "0")}.pdf`)
}
