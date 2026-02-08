import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Search, Pencil, Trash2, ChevronLeft, ChevronRight, Wrench } from "lucide-react"
import { toast } from "sonner"
import { useVeiculos, useDeleteVeiculo } from "@/hooks/useVeiculos"
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
import type { Veiculo } from "@/types/veiculo"

export function VeiculosPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [deleteTarget, setDeleteTarget] = useState<Veiculo | null>(null)

  const { data, isLoading } = useVeiculos(page, search || undefined)
  const deleteMutation = useDeleteVeiculo()

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Veículo desativado com sucesso!")
      setDeleteTarget(null)
    } catch {
      toast.error("Erro ao desativar veículo.")
    }
  }

  function formatPlaca(placa: string) {
    if (placa.length === 7) return `${placa.slice(0, 3)}-${placa.slice(3)}`
    return placa
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Veículos</h1>
          <p className="text-muted-foreground">
            Gerencie os veículos cadastrados no sistema.
          </p>
        </div>
        <Link to="/veiculos/novo" className={buttonVariants()}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Veículo
        </Link>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por placa, marca ou modelo..."
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
              <TableHead>Placa</TableHead>
              <TableHead>Marca / Modelo</TableHead>
              <TableHead>Ano</TableHead>
              <TableHead>Câmbio</TableHead>
              <TableHead>KM</TableHead>
              <TableHead className="w-[130px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 6 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                  {search ? "Nenhum veículo encontrado." : "Nenhum veículo cadastrado."}
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((v) => (
                <TableRow key={v.id}>
                  <TableCell className="font-mono font-medium">{formatPlaca(v.placa)}</TableCell>
                  <TableCell>{v.marca} {v.modelo}</TableCell>
                  <TableCell>{v.ano}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{v.tipo_cambio}</Badge>
                  </TableCell>
                  <TableCell>{v.quilometragem_atual.toLocaleString("pt-BR")} km</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Link
                        to={`/trocas/nova?veiculo=${v.id}`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                        title="Nova troca"
                      >
                        <Wrench className="h-4 w-4" />
                      </Link>
                      <Link
                        to={`/veiculos/${v.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(v)}>
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
          <p className="text-sm text-muted-foreground">
            {data.total} veículo{data.total !== 1 ? "s" : ""} encontrado{data.total !== 1 ? "s" : ""}
          </p>
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
            <DialogTitle>Desativar veículo</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja desativar o veículo <strong>{deleteTarget && formatPlaca(deleteTarget.placa)}</strong>?
              O histórico de trocas será preservado.
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
