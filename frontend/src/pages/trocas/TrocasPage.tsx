import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Pencil, Trash2, ChevronLeft, ChevronRight, FileDown, Loader2, CheckCircle2, X, Search } from "lucide-react"
import { toast } from "sonner"
import { useTrocas, useDeleteTroca } from "@/hooks/useTrocas"
import { useAllVeiculos } from "@/hooks/useVeiculos"
import { useAllClientes } from "@/hooks/useClientes"
import { useBuscaCliente } from "@/hooks/useClientes"
import { formatCpfCnpj } from "@/lib/masks"
import { gerarPdfTroca } from "@/lib/gerarPdfTroca"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import type { TrocaOleo } from "@/types/troca"

export function TrocasPage() {
  const [page, setPage] = useState(1)
  const [deleteTarget, setDeleteTarget] = useState<TrocaOleo | null>(null)
  const [pdfLoading, setPdfLoading] = useState<number | null>(null)

  // Filtro de cliente (autocomplete)
  const [searchInput, setSearchInput] = useState("")
  const { cliente: clienteFiltro, sugestoes, buscando, buscarSugestoes, selecionar, limpar: limparCliente } = useBuscaCliente()

  // Filtros de data
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const [filtroInicio, setFiltroInicio] = useState("")
  const [filtroFim, setFiltroFim] = useState("")

  const filters = {
    ...(filtroInicio ? { data_inicio: filtroInicio } : {}),
    ...(filtroFim ? { data_fim: filtroFim } : {}),
    ...(clienteFiltro ? { cliente_id: clienteFiltro.id } : {}),
  }

  const { data, isLoading } = useTrocas(page, Object.keys(filters).length > 0 ? filters : undefined)
  const { data: veiculosData } = useAllVeiculos()
  const { data: clientesData } = useAllClientes()
  const deleteMutation = useDeleteTroca()

  // Map veiculo_id → info + cliente_id
  const veiculoInfoMap = new Map<number, string>()
  const veiculoClienteMap = new Map<number, number>()
  if (veiculosData?.items) {
    for (const v of veiculosData.items) {
      veiculoInfoMap.set(v.id, `${v.placa} — ${v.marca} ${v.modelo}`)
      veiculoClienteMap.set(v.id, v.cliente_id)
    }
  }

  // Map cliente_id → nome
  const clienteNomeMap = new Map<number, string>()
  if (clientesData?.items) {
    for (const c of clientesData.items) {
      clienteNomeMap.set(c.id, c.nome)
    }
  }

  function getClienteNome(veiculoId: number): string {
    const clienteId = veiculoClienteMap.get(veiculoId)
    if (!clienteId) return "—"
    return clienteNomeMap.get(clienteId) || "—"
  }

  function handleFiltrar(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setFiltroInicio(dataInicio)
    setFiltroFim(dataFim)
  }

  function handleLimparFiltros() {
    setDataInicio("")
    setDataFim("")
    setFiltroInicio("")
    setFiltroFim("")
    setSearchInput("")
    limparCliente()
    setPage(1)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Troca removida com sucesso!")
      setDeleteTarget(null)
    } catch {
      toast.error("Erro ao remover troca.")
    }
  }

  async function handlePdf(trocaId: number) {
    setPdfLoading(trocaId)
    try {
      await gerarPdfTroca(trocaId)
    } catch {
      toast.error("Erro ao gerar PDF.")
    } finally {
      setPdfLoading(null)
    }
  }

  function formatDate(dateStr: string) {
    return new Date(dateStr + "T00:00:00").toLocaleDateString("pt-BR")
  }

  function formatCurrency(value: string) {
    return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
  }

  const temFiltro = filtroInicio || filtroFim || clienteFiltro

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trocas de Óleo</h1>
          <p className="text-muted-foreground">
            Registros de trocas de óleo realizadas.
          </p>
        </div>
        <Link to="/trocas/nova" className={buttonVariants()}>
          <Plus className="mr-2 h-4 w-4" />
          Nova Troca
        </Link>
      </div>

      {/* Filtros */}
      <form onSubmit={handleFiltrar} className="flex flex-wrap items-end gap-3">
        {/* Busca por cliente */}
        <div className="relative">
          <p className="mb-1 text-xs text-muted-foreground">Cliente</p>
          {clienteFiltro ? (
            <div className="flex h-9 items-center gap-2 rounded-md border border-green-300 bg-green-50 px-2 text-sm dark:border-green-800 dark:bg-green-950">
              <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
              <span className="max-w-[150px] truncate font-medium">{clienteFiltro.nome}</span>
              <button type="button" onClick={() => { limparCliente(); setSearchInput(""); setPage(1) }} className="ml-1">
                <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
              </button>
            </div>
          ) : (
            <>
              <div className="relative">
                <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Nome ou CPF..."
                  value={searchInput}
                  onChange={(e) => { setSearchInput(e.target.value); buscarSugestoes(e.target.value) }}
                  autoComplete="off"
                  className="h-9 w-48 pl-7 text-sm"
                />
                {buscando && (
                  <Loader2 className="absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 animate-spin text-muted-foreground" />
                )}
              </div>
              {sugestoes.length > 0 && (
                <div className="absolute z-10 mt-1 w-60 rounded-md border bg-popover shadow-md">
                  {sugestoes.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-accent"
                      onClick={() => { selecionar(c); setSearchInput(""); setPage(1) }}
                    >
                      <div>
                        <p className="font-medium">{c.nome}</p>
                        <p className="text-xs text-muted-foreground">{formatCpfCnpj(c.cpf_cnpj)}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        <div>
          <p className="mb-1 text-xs text-muted-foreground">Data Início</p>
          <Input
            type="date"
            value={dataInicio}
            onChange={(e) => setDataInicio(e.target.value)}
            className="h-9 w-40 text-sm"
          />
        </div>
        <div>
          <p className="mb-1 text-xs text-muted-foreground">Data Fim</p>
          <Input
            type="date"
            value={dataFim}
            onChange={(e) => setDataFim(e.target.value)}
            className="h-9 w-40 text-sm"
          />
        </div>
        <Button type="submit" variant="secondary" size="sm" className="h-9">
          Filtrar
        </Button>
        {temFiltro && (
          <Button type="button" variant="ghost" size="sm" className="h-9" onClick={handleLimparFiltros}>
            Limpar
          </Button>
        )}
      </form>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead>Veículo</TableHead>
              <TableHead>KM</TableHead>
              <TableHead>Valor Total</TableHead>
              <TableHead>Próx. Troca</TableHead>
              <TableHead className="w-[130px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  {temFiltro ? "Nenhuma troca encontrada no período." : "Nenhuma troca registrada."}
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((troca) => (
                <TableRow key={troca.id}>
                  <TableCell>{formatDate(troca.data_troca)}</TableCell>
                  <TableCell>{getClienteNome(troca.veiculo_id)}</TableCell>
                  <TableCell className="font-medium">
                    {veiculoInfoMap.get(troca.veiculo_id) || `#${troca.veiculo_id}`}
                  </TableCell>
                  <TableCell>{troca.quilometragem_troca.toLocaleString("pt-BR")}</TableCell>
                  <TableCell className="font-medium">{formatCurrency(troca.valor_total)}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {troca.proxima_troca_km
                      ? `${troca.proxima_troca_km.toLocaleString("pt-BR")} km`
                      : troca.proxima_troca_data
                        ? formatDate(troca.proxima_troca_data)
                        : "-"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Baixar PDF"
                        disabled={pdfLoading === troca.id}
                        onClick={() => handlePdf(troca.id)}
                      >
                        {pdfLoading === troca.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <FileDown className="h-4 w-4" />
                        )}
                      </Button>
                      <Link
                        to={`/trocas/${troca.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(troca)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">{data.total} troca{data.total !== 1 ? "s" : ""}</p>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft className="mr-1 h-4 w-4" /> Anterior
            </Button>
            <span className="text-sm text-muted-foreground">Página {data.page} de {data.pages}</span>
            <Button variant="outline" size="sm" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>
              Próxima <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent onClose={() => setDeleteTarget(null)}>
          <DialogHeader>
            <DialogTitle>Remover troca</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja remover esta troca? O estoque do óleo e das peças será devolvido.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancelar</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? "Removendo..." : "Remover"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
