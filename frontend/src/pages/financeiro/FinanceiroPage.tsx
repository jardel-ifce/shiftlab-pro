import { useState } from "react"
import { DollarSign, TrendingUp, TrendingDown, Search, X, Receipt, Percent, BadgeDollarSign, Save } from "lucide-react"
import { useFinanceiro, useFinanceiroProdutos } from "@/hooks/useFinanceiro"
import { useImposto, useUpdateImposto } from "@/hooks/useConfiguracoes"
import { useBuscaCliente } from "@/hooks/useClientes"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"

const TIPO_LABELS: Record<string, string> = {
  oleo: "Óleo",
  filtro: "Filtro",
  peca: "Peça",
}

const TIPO_COLORS: Record<string, "default" | "secondary" | "outline"> = {
  oleo: "default",
  filtro: "secondary",
  peca: "outline",
}

function formatBRL(value: number | string) {
  return `R$ ${Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function margemColor(margem: number) {
  if (margem >= 30) return "text-emerald-600"
  if (margem >= 15) return "text-amber-600"
  return "text-red-600"
}

const MESES = [
  { value: 1, label: "Janeiro" },
  { value: 2, label: "Fevereiro" },
  { value: 3, label: "Março" },
  { value: 4, label: "Abril" },
  { value: 5, label: "Maio" },
  { value: 6, label: "Junho" },
  { value: 7, label: "Julho" },
  { value: 8, label: "Agosto" },
  { value: 9, label: "Setembro" },
  { value: 10, label: "Outubro" },
  { value: 11, label: "Novembro" },
  { value: 12, label: "Dezembro" },
]

export function FinanceiroPage() {
  const [tab, setTab] = useState<"trocas" | "produtos">("trocas")

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Financeiro</h1>
        <p className="text-muted-foreground">Controle de lucro por troca e por produto</p>
      </div>

      <div className="flex gap-2">
        <Button
          variant={tab === "trocas" ? "default" : "outline"}
          onClick={() => setTab("trocas")}
        >
          Lucro por Troca
        </Button>
        <Button
          variant={tab === "produtos" ? "default" : "outline"}
          onClick={() => setTab("produtos")}
        >
          Lucro por Produto
        </Button>
      </div>

      {tab === "trocas" ? <TabTrocas /> : <TabProdutos />}
    </div>
  )
}

function TabTrocas() {
  const [page, setPage] = useState(1)

  // Imposto
  const { data: impostoData } = useImposto()
  const updateImposto = useUpdateImposto()
  const [impostoInput, setImpostoInput] = useState<string | null>(null)
  const impostoAtual = impostoInput ?? String(impostoData?.percentual ?? "")

  function salvarImposto() {
    const val = parseFloat(impostoAtual)
    if (!isNaN(val) && val >= 0 && val <= 100) {
      updateImposto.mutate(val, { onSuccess: () => setImpostoInput(null) })
    }
  }

  // Filtro de cliente
  const [searchInput, setSearchInput] = useState("")
  const { cliente: clienteFiltro, sugestoes, buscando, buscarSugestoes, selecionar, limpar: limparCliente } = useBuscaCliente()

  // Filtros de data (ano/mês/dia)
  const [ano, setAno] = useState<string>("")
  const [mes, setMes] = useState<string>("")
  const [dia, setDia] = useState<string>("")

  const currentYear = new Date().getFullYear()
  const anos = Array.from({ length: currentYear - 2023 }, (_, i) => String(currentYear - i))
  const diasNoMes = ano && mes ? new Date(Number(ano), Number(mes), 0).getDate() : 31
  const dias = Array.from({ length: diasNoMes }, (_, i) => String(i + 1))

  // Computar filtros de data a partir dos selects
  const filters: { cliente_id?: number; data_inicio?: string; data_fim?: string } = {}
  if (clienteFiltro) filters.cliente_id = clienteFiltro.id
  if (ano) {
    if (mes) {
      const m = mes.padStart(2, "0")
      if (dia) {
        const d = dia.padStart(2, "0")
        filters.data_inicio = `${ano}-${m}-${d}`
        filters.data_fim = `${ano}-${m}-${d}`
      } else {
        const lastDay = new Date(Number(ano), Number(mes), 0).getDate()
        filters.data_inicio = `${ano}-${m}-01`
        filters.data_fim = `${ano}-${m}-${String(lastDay).padStart(2, "0")}`
      }
    } else {
      filters.data_inicio = `${ano}-01-01`
      filters.data_fim = `${ano}-12-31`
    }
  }

  const { data, isLoading } = useFinanceiro(page, Object.keys(filters).length > 0 ? filters : undefined)

  function limparFiltros() {
    setAno("")
    setMes("")
    setDia("")
    limparCliente()
    setSearchInput("")
    setPage(1)
  }

  const temFiltro = ano || clienteFiltro

  return (
    <>
      {/* Filtros */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Ano</label>
              <select
                value={ano}
                onChange={(e) => { setAno(e.target.value); setMes(""); setDia(""); setPage(1) }}
                className="h-10 w-[100px] rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <option value="">Todos</option>
                {anos.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Mês</label>
              <select
                value={mes}
                onChange={(e) => { setMes(e.target.value); setDia(""); setPage(1) }}
                disabled={!ano}
                className="h-10 w-[140px] rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Todos</option>
                {MESES.map((m) => <option key={m.value} value={String(m.value)}>{m.label}</option>)}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Dia</label>
              <select
                value={dia}
                onChange={(e) => { setDia(e.target.value); setPage(1) }}
                disabled={!mes}
                className="h-10 w-[90px] rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Todos</option>
                {dias.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>

            {temFiltro && (
              <Button variant="ghost" size="sm" onClick={limparFiltros}>Limpar</Button>
            )}

            <div className="ml-auto flex items-end gap-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Imposto %</label>
                <div className="flex gap-1">
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    step={0.1}
                    className="h-10 w-[80px] text-sm"
                    value={impostoAtual}
                    onChange={(e) => setImpostoInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && salvarImposto()}
                  />
                  <Button
                    size="icon"
                    variant="outline"
                    className="h-10 w-10"
                    onClick={salvarImposto}
                    disabled={updateImposto.isPending}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cards de resumo - Linha 1 */}
      {data?.resumo && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Faturamento</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-600">
                  {formatBRL(data.resumo.faturamento_total)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.resumo.total_trocas} trocas | Ticket médio {formatBRL(data.resumo.ticket_medio)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Custo Total</CardTitle>
                <TrendingDown className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatBRL(data.resumo.custo_total)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Custo de óleo + peças
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lucro Bruto</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${data.resumo.lucro_bruto_total >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                  {formatBRL(data.resumo.lucro_bruto_total)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Faturamento - Custos
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Cards de resumo - Linha 2 */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Impostos ({data.resumo.imposto_percentual}%)</CardTitle>
                <Percent className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  -{formatBRL(data.resumo.imposto_valor)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Sobre faturamento bruto
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Despesas</CardTitle>
                <Receipt className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  -{formatBRL(data.resumo.despesas_total)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Despesas operacionais no período
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-primary/20 bg-primary/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lucro Líquido</CardTitle>
                <BadgeDollarSign className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${data.resumo.lucro_liquido >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                  {formatBRL(data.resumo.lucro_liquido)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Bruto - Impostos - Despesas
                </p>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Tabela */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>Lucro por Troca</CardTitle>
          <div className="relative w-64">
            {clienteFiltro ? (
              <div className="flex h-9 items-center gap-2 rounded-md border bg-muted/50 px-3">
                <span className="text-sm truncate">{clienteFiltro.nome}</span>
                <Button type="button" variant="ghost" size="icon" className="ml-auto h-6 w-6 shrink-0" onClick={() => { limparCliente(); setSearchInput("") }}>
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por cliente..."
                  className="h-9 pl-9 text-sm"
                  value={searchInput}
                  onChange={(e) => {
                    setSearchInput(e.target.value)
                    buscarSugestoes(e.target.value)
                  }}
                />
                {sugestoes.length > 0 && (
                  <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
                    <ul className="max-h-48 overflow-auto py-1">
                      {sugestoes.map((c) => (
                        <li
                          key={c.id}
                          className="cursor-pointer px-3 py-2 text-sm hover:bg-accent"
                          onClick={() => {
                            selecionar(c)
                            setSearchInput("")
                            setPage(1)
                          }}
                        >
                          {c.nome}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {buscando && (
                  <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover p-3 text-center text-sm text-muted-foreground shadow-lg">
                    Buscando...
                  </div>
                )}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : !data?.items.length ? (
            <p className="py-8 text-center text-muted-foreground">Nenhuma troca encontrada.</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Veículo</TableHead>
                    <TableHead className="text-right">Faturamento</TableHead>
                    <TableHead className="text-right">Custo</TableHead>
                    <TableHead className="text-right">Lucro</TableHead>
                    <TableHead className="text-right">Margem</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((t) => {
                    const lucro = Number(t.lucro_bruto)
                    const margem = Number(t.margem_lucro)
                    return (
                      <TableRow key={t.id}>
                        <TableCell>
                          {new Date(t.data_troca + "T00:00:00").toLocaleDateString("pt-BR")}
                        </TableCell>
                        <TableCell>{t.cliente_nome || "-"}</TableCell>
                        <TableCell>
                          <div className="text-sm">{t.veiculo_info || "-"}</div>
                          <div className="text-xs text-muted-foreground">{t.oleo_nome}</div>
                        </TableCell>
                        <TableCell className="text-right font-medium text-emerald-600">
                          {formatBRL(t.valor_total)}
                        </TableCell>
                        <TableCell className="text-right text-red-600">
                          {formatBRL(t.custo_total)}
                        </TableCell>
                        <TableCell className={`text-right font-bold ${lucro >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                          {formatBRL(lucro)}
                        </TableCell>
                        <TableCell className={`text-right font-medium ${margemColor(margem)}`}>
                          {margem.toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>

              {data.pages > 1 && (
                <div className="mt-4 flex items-center justify-center gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                    Anterior
                  </Button>
                  <span className="text-sm text-muted-foreground">{data.page} / {data.pages}</span>
                  <Button variant="outline" size="sm" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>
                    Próxima
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </>
  )
}

function TabProdutos() {
  const [tipoFiltro, setTipoFiltro] = useState<string | undefined>(undefined)
  const { data, isLoading } = useFinanceiroProdutos(tipoFiltro)

  return (
    <>
      {/* Filtro por tipo */}
      <div className="flex gap-2">
        {[undefined, "oleo", "filtro", "peca"].map((t) => (
          <Button
            key={t ?? "todos"}
            variant={tipoFiltro === t ? "default" : "outline"}
            size="sm"
            onClick={() => setTipoFiltro(t)}
          >
            {t ? TIPO_LABELS[t] : "Todos"}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lucro por Produto</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : !data?.items.length ? (
            <p className="py-8 text-center text-muted-foreground">Nenhum produto encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Marca</TableHead>
                  <TableHead className="text-right">Custo</TableHead>
                  <TableHead className="text-right">Preço Venda</TableHead>
                  <TableHead className="text-right">Lucro Un.</TableHead>
                  <TableHead className="text-right">Margem</TableHead>
                  <TableHead className="text-right">Estoque</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((p) => (
                  <TableRow key={`${p.tipo}-${p.id}`}>
                    <TableCell>
                      <Badge variant={TIPO_COLORS[p.tipo] || "outline"}>
                        {TIPO_LABELS[p.tipo] || p.tipo}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">{p.nome}</TableCell>
                    <TableCell>{p.marca || "-"}</TableCell>
                    <TableCell className="text-right text-red-600">{formatBRL(p.custo)}</TableCell>
                    <TableCell className="text-right">{formatBRL(p.preco_venda)}</TableCell>
                    <TableCell className={`text-right font-medium ${p.lucro_unitario >= 0 ? "text-emerald-600" : "text-red-600"}`}>
                      {formatBRL(p.lucro_unitario)}
                    </TableCell>
                    <TableCell className={`text-right font-medium ${margemColor(p.margem_lucro)}`}>
                      {p.margem_lucro.toFixed(1)}%
                    </TableCell>
                    <TableCell className="text-right">{p.estoque}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </>
  )
}
