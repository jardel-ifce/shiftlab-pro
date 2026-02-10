import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Search, Pencil, Trash2, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react"
import { toast } from "sonner"
import { useOleos, useDeleteOleo } from "@/hooks/useOleos"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card"
import type { Oleo } from "@/types/oleo"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"
const BASE_URL = API_URL.replace(/\/api\/v1\/?$/, "")

export function OleosPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [deleteTarget, setDeleteTarget] = useState<Oleo | null>(null)
  const [fotoPreview, setFotoPreview] = useState<Oleo | null>(null)

  const { data, isLoading } = useOleos(page, search || undefined)
  const deleteMutation = useDeleteOleo()

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Óleo desativado com sucesso!")
      setDeleteTarget(null)
    } catch {
      toast.error("Erro ao desativar óleo.")
    }
  }

  function formatCurrency(value: string) {
    return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Óleos</h1>
          <p className="text-muted-foreground">
            Gerencie os óleos (produtos) em estoque.
          </p>
        </div>
        <Link to="/oleos/novo" className={buttonVariants()}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Óleo
        </Link>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, marca ou tipo..."
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
              <TableHead>Nome</TableHead>
              <TableHead>Marca</TableHead>
              <TableHead>Tipo Óleo</TableHead>
              <TableHead>Formato</TableHead>
              <TableHead>Preço/L</TableHead>
              <TableHead>Estoque (L)</TableHead>
              <TableHead>Margem</TableHead>
              <TableHead className="w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 8 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="h-24 text-center text-muted-foreground">
                  {search ? "Nenhum óleo encontrado." : "Nenhum óleo cadastrado."}
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((oleo) => (
                <TableRow key={oleo.id}>
                  <TableCell className="font-medium">
                    {oleo.foto_url ? (
                      <span className="relative inline-block">
                        <HoverCard>
                          <HoverCardTrigger>
                            <span
                              className="cursor-pointer underline-offset-4 hover:underline"
                              onClick={() => setFotoPreview(oleo)}
                            >
                              {oleo.nome}
                            </span>
                          </HoverCardTrigger>
                          <HoverCardContent side="right" className="w-52 p-2">
                            <img
                              src={`${BASE_URL}${oleo.foto_url}`}
                              alt={oleo.nome}
                              className="h-40 w-full rounded-md object-contain"
                            />
                            <p className="mt-2 text-center text-xs font-medium">
                              {oleo.marca} {oleo.nome}
                            </p>
                          </HoverCardContent>
                        </HoverCard>
                      </span>
                    ) : (
                      oleo.nome
                    )}
                    {oleo.viscosidade && <span className="ml-1 text-muted-foreground text-xs">({oleo.viscosidade})</span>}
                  </TableCell>
                  <TableCell>{oleo.marca}</TableCell>
                  <TableCell>
                    {oleo.tipo_oleo_transmissao ? (
                      <Badge variant="secondary">{oleo.tipo_oleo_transmissao}</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>{oleo.formato_venda || <span className="text-muted-foreground">-</span>}</TableCell>
                  <TableCell>{formatCurrency(oleo.preco_litro)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {Number(oleo.estoque_litros).toFixed(1)}
                      {oleo.estoque_baixo && (
                        <span title="Estoque baixo"><AlertTriangle className="h-4 w-4 text-orange-500" /></span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{Number(oleo.margem_lucro).toFixed(1)}%</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Link
                        to={`/oleos/${oleo.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(oleo)}>
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
          <p className="text-sm text-muted-foreground">{data.total} óleo{data.total !== 1 ? "s" : ""}</p>
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
            <DialogTitle>Desativar óleo</DialogTitle>
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

      {/* Dialog de preview da foto (mobile) */}
      <Dialog open={!!fotoPreview} onOpenChange={() => setFotoPreview(null)}>
        <DialogContent onClose={() => setFotoPreview(null)} className="max-w-sm">
          {fotoPreview?.foto_url && (
            <div className="space-y-3">
              <img
                src={`${BASE_URL}${fotoPreview.foto_url}`}
                alt={fotoPreview.nome}
                className="w-full rounded-md object-contain"
              />
              <div className="text-center">
                <p className="font-semibold">{fotoPreview.marca} {fotoPreview.nome}</p>
                {fotoPreview.viscosidade && (
                  <p className="text-sm text-muted-foreground">{fotoPreview.viscosidade}</p>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
