import { useState } from "react"
import { Link } from "react-router-dom"
import { Plus, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { useEntradasEstoque, useDeleteEntradaEstoque } from "@/hooks/useEntradasEstoque"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
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

export function EntradasPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useEntradasEstoque(page)
  const deleteMutation = useDeleteEntradaEstoque()

  async function handleDelete(id: number) {
    if (!confirm("Excluir esta entrada? O estoque será revertido.")) return
    try {
      await deleteMutation.mutateAsync(id)
      toast.success("Entrada excluída e estoque revertido!")
    } catch {
      toast.error("Erro ao excluir entrada.")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Entradas de Estoque</h1>
          <p className="text-muted-foreground">Histórico de compras de produtos</p>
        </div>
        <Button asChild>
          <Link to="/entradas/nova" className="inline-flex items-center">
            <Plus className="mr-2 h-4 w-4" /> Nova Entrada
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Compras Registradas</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !data?.items.length ? (
            <p className="py-8 text-center text-muted-foreground">
              Nenhuma entrada registrada.
            </p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Produto</TableHead>
                    <TableHead className="text-right">Qtd</TableHead>
                    <TableHead className="text-right">Custo Un.</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                    <TableHead>Fornecedor</TableHead>
                    <TableHead>NF</TableHead>
                    <TableHead className="w-[60px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((e) => (
                    <TableRow key={e.id}>
                      <TableCell>
                        {new Date(e.data_compra + "T00:00:00").toLocaleDateString("pt-BR")}
                      </TableCell>
                      <TableCell>
                        <Badge variant={TIPO_COLORS[e.tipo_produto] || "outline"}>
                          {TIPO_LABELS[e.tipo_produto] || e.tipo_produto}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">{e.produto_nome}</div>
                        <div className="text-xs text-muted-foreground">{e.produto_marca}</div>
                      </TableCell>
                      <TableCell className="text-right">
                        {Number(e.quantidade_litros).toFixed(e.tipo_produto === "oleo" ? 2 : 0)}
                      </TableCell>
                      <TableCell className="text-right">
                        R$ {Number(e.custo_unitario).toFixed(2)}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        R$ {Number(e.custo_total).toFixed(2)}
                      </TableCell>
                      <TableCell>{e.fornecedor || "-"}</TableCell>
                      <TableCell>{e.nota_fiscal || "-"}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(e.id)}
                          disabled={deleteMutation.isPending}
                          title="Excluir"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {data.pages > 1 && (
                <div className="mt-4 flex items-center justify-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Anterior
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {data.page} / {data.pages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= data.pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Próxima
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
