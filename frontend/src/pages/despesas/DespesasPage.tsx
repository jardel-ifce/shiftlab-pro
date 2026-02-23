import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Pencil, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
import { toast } from "sonner"
import { useDespesas, useDeleteDespesa } from "@/hooks/useDespesas"
import { Button, buttonVariants } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"

const CATEGORIAS: Record<string, string> = {
  manutencao: "Manutenção",
  aluguel: "Aluguel",
  energia: "Energia",
  conserto: "Conserto",
  material: "Material",
  outros: "Outros",
}

function formatDate(iso: string): string {
  if (!iso) return "-"
  const [year, month, day] = iso.split("T")[0].split("-")
  return `${day}/${month}/${year}`
}

function formatCurrency(value: string | number): string {
  return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
}

export function DespesasPage() {
  const [page, setPage] = useState(1)

  const { data, isLoading } = useDespesas(page)
  const deleteMutation = useDeleteDespesa()

  async function handleDelete(id: number, descricao: string) {
    const confirmed = window.confirm(
      `Tem certeza que deseja excluir a despesa "${descricao}"?`
    )
    if (!confirmed) return

    try {
      await deleteMutation.mutateAsync(id)
      toast.success("Despesa excluída com sucesso!")
    } catch {
      toast.error("Erro ao excluir despesa.")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Despesas</h1>
          <p className="text-muted-foreground">
            Despesas operacionais da oficina
          </p>
        </div>
        <Link to="/despesas/nova">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Nova Despesa
          </Button>
        </Link>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead className="text-right">Valor</TableHead>
              <TableHead className="w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 5 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                  Nenhuma despesa cadastrada.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((despesa) => (
                <TableRow key={despesa.id}>
                  <TableCell className="text-sm">
                    {formatDate(despesa.data)}
                  </TableCell>
                  <TableCell className="font-medium">
                    {despesa.descricao}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {CATEGORIAS[despesa.categoria] || despesa.categoria}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right text-red-600">
                    {formatCurrency(despesa.valor)}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Link
                        to={`/despesas/${despesa.id}/editar`}
                        className={buttonVariants({ variant: "ghost", size: "icon" })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Link>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(despesa.id, despesa.descricao)}
                        disabled={deleteMutation.isPending}
                      >
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
            {data.total} despesa{data.total !== 1 ? "s" : ""}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="mr-1 h-4 w-4" /> Anterior
            </Button>
            <span className="text-sm text-muted-foreground">
              Página {data.page} de {data.pages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= data.pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Próxima <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
