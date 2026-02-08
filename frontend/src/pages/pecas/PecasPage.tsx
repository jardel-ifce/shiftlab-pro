import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Search, Pencil, Trash2, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react"
import { toast } from "sonner"
import { usePecas, useDeletePeca } from "@/hooks/usePecas"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import type { Peca } from "@/types/peca"

export function PecasPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [deleteTarget, setDeleteTarget] = useState<Peca | null>(null)

  const { data, isLoading } = usePecas(page, search || undefined)
  const deleteMutation = useDeletePeca()

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Peça desativada com sucesso!")
      setDeleteTarget(null)
    } catch {
      toast.error("Erro ao desativar peça.")
    }
  }

  function formatCurrency(value: string) {
    return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Peças e Itens</h1>
          <p className="text-muted-foreground">
            Gerencie peças, filtros, aditivos e outros itens auxiliares.
          </p>
        </div>
        <Link to="/pecas/novo" className={buttonVariants()}>
          <Plus className="mr-2 h-4 w-4" />
          Nova Peça
        </Link>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome ou marca..."
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
              <TableHead>Unidade</TableHead>
              <TableHead>Custo</TableHead>
              <TableHead>Venda</TableHead>
              <TableHead>Estoque</TableHead>
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
                  {search ? "Nenhuma peça encontrada." : "Nenhuma peça cadastrada."}
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((peca) => (
                <TableRow key={peca.id}>
                  <TableCell className="font-medium">{peca.nome}</TableCell>
                  <TableCell>{peca.marca || "—"}</TableCell>
                  <TableCell>{peca.unidade}</TableCell>
                  <TableCell>{formatCurrency(peca.preco_custo)}</TableCell>
                  <TableCell>{formatCurrency(peca.preco_venda)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {Number(peca.estoque).toFixed(1)}
                      {peca.estoque_baixo && (
                        <span title="Estoque baixo"><AlertTriangle className="h-4 w-4 text-orange-500" /></span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{Number(peca.margem_lucro).toFixed(1)}%</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Link
                        to={`/pecas/${peca.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(peca)}>
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
          <p className="text-sm text-muted-foreground">{data.total} peça{data.total !== 1 ? "s" : ""}</p>
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
            <DialogTitle>Desativar peça</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja desativar <strong>{deleteTarget?.nome}</strong>?
              O item não será excluído, apenas ficará inativo.
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
    </div>
  )
}
