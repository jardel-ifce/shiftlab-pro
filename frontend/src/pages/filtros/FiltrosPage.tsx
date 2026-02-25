import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Search, Pencil, Trash2, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react"
import { toast } from "sonner"
import { useFiltros, useDeleteFiltro } from "@/hooks/useFiltros"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card"
import { Carousel } from "@/components/ui/carousel"
import type { Filtro } from "@/types/filtro"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"
const BASE_URL = API_URL.replace(/\/api\/v1\/?$/, "")

export function FiltrosPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [deleteTarget, setDeleteTarget] = useState<Filtro | null>(null)
  const [fotoPreview, setFotoPreview] = useState<Filtro | null>(null)

  const { data, isLoading } = useFiltros(page, search || undefined)
  const deleteMutation = useDeleteFiltro()

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Filtro desativado com sucesso!")
      setDeleteTarget(null)
    } catch {
      toast.error("Erro ao desativar filtro.")
    }
  }

  function formatCurrency(value: string | number) {
    return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Filtros de Óleo</h1>
          <p className="text-muted-foreground">
            Gerencie os filtros de óleo em estoque.
          </p>
        </div>
        <Link to="/filtros/novo" className={buttonVariants()}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Filtro
        </Link>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, marca, código ou OEM..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button type="submit" variant="secondary">Buscar</Button>
        {search && (
          <Button type="button" variant="ghost" onClick={() => { setSearchInput(""); setSearch(""); setPage(1) }}>
            Limpar
          </Button>
        )}
      </form>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Código</TableHead>
              <TableHead>Nome</TableHead>
              <TableHead>Marca</TableHead>
              <TableHead>OEM</TableHead>
              <TableHead className="text-right">Custo</TableHead>
              <TableHead className="text-right">Preço</TableHead>
              <TableHead className="text-right">Lucro</TableHead>
              <TableHead>Estoque</TableHead>
              <TableHead>Margem</TableHead>
              <TableHead className="w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 10 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} className="h-24 text-center text-muted-foreground">
                  {search ? "Nenhum filtro encontrado." : "Nenhum filtro cadastrado."}
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((filtro) => (
                <TableRow key={filtro.id}>
                  <TableCell className="text-muted-foreground text-sm">
                    {filtro.codigo_produto || "-"}
                  </TableCell>
                  <TableCell className="font-medium">
                    {filtro.fotos?.length > 0 ? (
                      <HoverCard>
                        <HoverCardTrigger>
                          <span
                            className="cursor-pointer underline-offset-4 hover:underline"
                            onClick={() => setFotoPreview(filtro)}
                          >
                            {filtro.nome}
                          </span>
                        </HoverCardTrigger>
                        <HoverCardContent side="right" className="w-52 p-2">
                          <Carousel
                            images={filtro.fotos.map((f) => ({ id: f.id, url: `${BASE_URL}${f.url}` }))}
                            alt={filtro.nome}
                            className="h-40"
                          />
                          <p className="mt-2 text-center text-xs font-medium">
                            {filtro.marca} {filtro.nome}
                          </p>
                        </HoverCardContent>
                      </HoverCard>
                    ) : (
                      filtro.nome
                    )}
                  </TableCell>
                  <TableCell>{filtro.marca}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {filtro.codigo_oem || "-"}
                  </TableCell>
                  <TableCell className="text-right text-red-600">{formatCurrency(filtro.custo_unitario)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(filtro.preco_unitario)}</TableCell>
                  <TableCell className="text-right text-emerald-600">{formatCurrency(filtro.lucro_unitario)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {filtro.estoque}
                      {filtro.estoque_baixo && (
                        <span title="Estoque baixo"><AlertTriangle className="h-4 w-4 text-orange-500" /></span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{Number(filtro.margem_lucro).toFixed(1)}%</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Link
                        to={`/filtros/${filtro.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(filtro)}>
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
          <p className="text-sm text-muted-foreground">{data.total} filtro{data.total !== 1 ? "s" : ""}</p>
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
            <DialogTitle>Desativar filtro</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja desativar <strong>{deleteTarget?.nome}</strong>?
              O produto não será excluído, apenas ficará inativo.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancelar</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? "Desativando..." : "Desativar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!fotoPreview} onOpenChange={() => setFotoPreview(null)}>
        <DialogContent onClose={() => setFotoPreview(null)} className="max-w-md">
          {fotoPreview && fotoPreview.fotos?.length > 0 && (
            <div className="space-y-3">
              <Carousel
                images={fotoPreview.fotos.map((f) => ({ id: f.id, url: `${BASE_URL}${f.url}` }))}
                alt={fotoPreview.nome}
              />
              <div className="text-center">
                <p className="font-semibold">{fotoPreview.marca} {fotoPreview.nome}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
