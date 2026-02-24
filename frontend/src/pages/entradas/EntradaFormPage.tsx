import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft, Search, X } from "lucide-react"
import { useCreateEntradaEstoque, useBuscarProduto } from "@/hooks/useEntradasEstoque"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatMoeda,
  formatDecimal,
  parseMoeda,
  parseDecimal,
} from "@/lib/masks"
import type { ProdutoBusca } from "@/types/entrada_estoque"

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

interface FormData {
  fornecedor: string
  nota_fiscal: string
  data_compra: string
  observacoes: string
}

export function EntradaFormPage() {
  const navigate = useNavigate()
  const createMutation = useCreateEntradaEstoque()

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      data_compra: new Date().toISOString().split("T")[0],
    },
  })

  // Produto selecionado
  const [produtoSelecionado, setProdutoSelecionado] = useState<ProdutoBusca | null>(null)

  // Busca
  const [tipoFiltro, setTipoFiltro] = useState<string | undefined>(undefined)
  const [buscaInput, setBuscaInput] = useState("")
  const [buscaDebounced, setBuscaDebounced] = useState("")
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const { data: resultados, isLoading: buscando } = useBuscarProduto(buscaDebounced, tipoFiltro)

  // Debounce da busca
  useEffect(() => {
    const timer = setTimeout(() => setBuscaDebounced(buscaInput), 300)
    return () => clearTimeout(timer)
  }, [buscaInput])

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // Campos de valor
  const [quantidade, setQuantidade] = useState("")
  const [custoUnitario, setCustoUnitario] = useState("")

  const isOleo = produtoSelecionado?.tipo === "oleo"
  const qtdNum = parseDecimal(quantidade)
  const custoNum = parseMoeda(custoUnitario)
  const custoTotal = qtdNum * custoNum

  function selecionarProduto(p: ProdutoBusca) {
    setProdutoSelecionado(p)
    setBuscaInput("")
    setShowDropdown(false)
    setQuantidade("")
  }

  function limparProduto() {
    setProdutoSelecionado(null)
    setBuscaInput("")
    setQuantidade("")
  }

  async function onSubmit(formData: FormData) {
    if (!produtoSelecionado) {
      toast.error("Selecione um produto.")
      return
    }
    if (!qtdNum || qtdNum <= 0) {
      toast.error(isOleo ? "Informe a quantidade em litros." : "Informe a quantidade.")
      return
    }
    if (!custoNum || custoNum <= 0) {
      toast.error(isOleo ? "Informe o custo por litro." : "Informe o custo unitário.")
      return
    }

    try {
      await createMutation.mutateAsync({
        tipo_produto: produtoSelecionado.tipo,
        produto_id: produtoSelecionado.id,
        quantidade_litros: qtdNum,
        custo_unitario: custoNum,
        fornecedor: formData.fornecedor || null,
        nota_fiscal: formData.nota_fiscal || null,
        data_compra: formData.data_compra,
        observacoes: formData.observacoes || null,
      })
      toast.success("Entrada registrada! Estoque atualizado.")
      navigate("/entradas")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao registrar entrada.")
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/entradas")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Nova Entrada</h1>
          <p className="text-muted-foreground">Registre uma compra de produto.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Produto</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {/* Filtro de tipo */}
            <div className="space-y-2">
              <Label>Tipo de Produto</Label>
              <div className="flex gap-2">
                {[undefined, "oleo", "filtro", "peca"].map((t) => (
                  <Button
                    key={t ?? "todos"}
                    type="button"
                    variant={tipoFiltro === t ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTipoFiltro(t)}
                  >
                    {t ? TIPO_LABELS[t] : "Todos"}
                  </Button>
                ))}
              </div>
            </div>

            {/* Produto selecionado ou campo de busca */}
            {produtoSelecionado ? (
              <div className="flex items-center gap-3 rounded-md border bg-muted/50 p-3">
                <Badge variant={TIPO_COLORS[produtoSelecionado.tipo]}>
                  {TIPO_LABELS[produtoSelecionado.tipo]}
                </Badge>
                <div className="flex-1">
                  <p className="font-medium">{produtoSelecionado.label}</p>
                  {produtoSelecionado.codigo_produto && (
                    <p className="text-xs text-muted-foreground">Cód: {produtoSelecionado.codigo_produto}</p>
                  )}
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={limparProduto}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div className="relative" ref={dropdownRef}>
                <Label htmlFor="busca-produto">Buscar Produto *</Label>
                <div className="relative mt-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="busca-produto"
                    placeholder="Digite o código ou nome do produto..."
                    value={buscaInput}
                    onChange={(e) => {
                      setBuscaInput(e.target.value)
                      setShowDropdown(true)
                    }}
                    onFocus={() => buscaInput.length >= 1 && setShowDropdown(true)}
                    className="pl-9"
                    autoComplete="off"
                  />
                </div>

                {showDropdown && buscaDebounced.length >= 1 && (
                  <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
                    {buscando ? (
                      <div className="p-3 text-center text-sm text-muted-foreground">Buscando...</div>
                    ) : !resultados?.length ? (
                      <div className="p-3 text-center text-sm text-muted-foreground">Nenhum produto encontrado.</div>
                    ) : (
                      <ul className="max-h-60 overflow-auto py-1">
                        {resultados.map((p) => (
                          <li
                            key={`${p.tipo}-${p.id}`}
                            className="flex cursor-pointer items-center gap-2 px-3 py-2 hover:bg-accent"
                            onClick={() => selecionarProduto(p)}
                          >
                            <Badge variant={TIPO_COLORS[p.tipo]} className="text-[10px]">
                              {TIPO_LABELS[p.tipo]}
                            </Badge>
                            <span className="text-sm">{p.label}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Dados da Compra</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="quantidade">
                  {isOleo ? "Quantidade (L) *" : "Quantidade (un.) *"}
                </Label>
                <Input
                  id="quantidade"
                  type="text"
                  inputMode={isOleo ? "decimal" : "numeric"}
                  placeholder={isOleo ? "0,00" : "0"}
                  value={quantidade}
                  onChange={(e) => {
                    if (isOleo) {
                      setQuantidade(formatDecimal(e.target.value, 2))
                    } else {
                      const val = e.target.value.replace(/\D/g, "")
                      setQuantidade(val)
                    }
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="custo_unitario">
                  {isOleo ? "Custo/Litro (R$) *" : "Custo Unitário (R$) *"}
                </Label>
                <Input
                  id="custo_unitario"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={custoUnitario}
                  onChange={(e) => setCustoUnitario(formatMoeda(e.target.value))}
                />
              </div>
            </div>

            {custoTotal > 0 && (
              <div className="rounded-md bg-muted p-3 text-sm">
                <strong>Custo Total:</strong> R$ {custoTotal.toFixed(2).replace(".", ",")}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="data_compra">Data da Compra *</Label>
              <Input
                id="data_compra"
                type="date"
                {...register("data_compra", { required: "Informe a data" })}
              />
              {errors.data_compra && <p className="text-xs text-destructive">{errors.data_compra.message}</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Informações do Fornecedor</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="fornecedor">Fornecedor</Label>
                <Input id="fornecedor" placeholder="Nome do fornecedor" {...register("fornecedor")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="nota_fiscal">Nota Fiscal</Label>
                <Input id="nota_fiscal" placeholder="Número da NF" {...register("nota_fiscal")} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <textarea
                id="observacoes"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Observações sobre esta compra..."
                {...register("observacoes")}
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? "Salvando..." : "Registrar Entrada"}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate("/entradas")}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
