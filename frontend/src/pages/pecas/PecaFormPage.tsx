import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import { usePeca, useCreatePeca, useUpdatePeca } from "@/hooks/usePecas"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  formatMoeda,
  formatDecimal,
  parseMoeda,
  parseDecimal,
  numberToMoeda,
  numberToDecimal,
} from "@/lib/masks"

const UNIDADES = [
  { value: "un.", label: "Unidade (un.)" },
  { value: "l", label: "Litro (l)" },
  { value: "kg", label: "Quilograma (kg)" },
]

interface FormData {
  nome: string
  marca: string
  unidade: string
  comentarios: string
  observacoes: string
}

export function PecaFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: peca, isLoading } = usePeca(isEditing ? Number(id) : undefined)
  const createMutation = useCreatePeca()
  const updateMutation = useUpdatePeca()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    defaultValues: { unidade: "un." },
  })

  const [precoVenda, setPrecoVenda] = useState("")
  const [estoque, setEstoque] = useState("")
  const [estoqueMinimo, setEstoqueMinimo] = useState("")

  useEffect(() => {
    if (peca) {
      reset({
        nome: peca.nome,
        marca: peca.marca || "",
        unidade: peca.unidade,
        comentarios: peca.comentarios || "",
        observacoes: peca.observacoes || "",
      })
      setPrecoVenda(numberToMoeda(peca.preco_venda))
      setEstoque(numberToDecimal(peca.estoque))
      setEstoqueMinimo(numberToDecimal(peca.estoque_minimo))
    }
  }, [peca, reset])

  async function onSubmit(formData: FormData) {
    const vendaValue = parseMoeda(precoVenda)
    if (!vendaValue) {
      toast.error("Informe o preço de venda.")
      return
    }

    try {
      const base = {
        nome: formData.nome,
        marca: formData.marca || null,
        unidade: formData.unidade || "un.",
        preco_venda: vendaValue,
        estoque_minimo: parseDecimal(estoqueMinimo) || 5,
        comentarios: formData.comentarios || null,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        const payload = { ...base, estoque: parseDecimal(estoque) || 0 }
        await updateMutation.mutateAsync({ id: Number(id), payload })
        toast.success("Peça atualizada com sucesso!")
      } else {
        await createMutation.mutateAsync(base)
        toast.success("Peça cadastrada com sucesso!")
      }
      navigate("/pecas")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar peça.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card><CardContent className="space-y-4 pt-6">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
        </CardContent></Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/pecas")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Peça" : "Nova Peça"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? "Atualize os dados do item." : "Cadastre uma nova peça ou item auxiliar."}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Dados do Item</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input id="nome" placeholder="Filtro de óleo, Estopa, Aditivo..." {...register("nome", { required: "Nome é obrigatório", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.nome && <p className="text-xs text-destructive">{errors.nome.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="marca">Marca</Label>
                <Input id="marca" placeholder="Tecfil, Wega, Wurth..." {...register("marca")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="unidade">Unidade de Medida</Label>
                <select
                  id="unidade"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  {...register("unidade")}
                >
                  {UNIDADES.map((u) => (
                    <option key={u.value} value={u.value}>{u.label}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="preco_venda">Preço de Venda (R$) *</Label>
                <Input
                  id="preco_venda"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={precoVenda}
                  onChange={(e) => setPrecoVenda(formatMoeda(e.target.value))}
                />
              </div>

              {isEditing && (
                <div className="space-y-2">
                  <Label htmlFor="estoque">Estoque Atual</Label>
                  <Input
                    id="estoque"
                    type="text"
                    inputMode="decimal"
                    placeholder="0"
                    value={estoque}
                    onChange={(e) => setEstoque(formatDecimal(e.target.value, 1))}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="estoque_minimo">Estoque Mínimo</Label>
                <Input
                  id="estoque_minimo"
                  type="text"
                  inputMode="decimal"
                  placeholder="5"
                  value={estoqueMinimo}
                  onChange={(e) => setEstoqueMinimo(formatDecimal(e.target.value, 1))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="comentarios">Comentários</Label>
              <textarea
                id="comentarios"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Comentários sobre o item..."
                {...register("comentarios")}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <textarea
                id="observacoes"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Notas adicionais..."
                {...register("observacoes")}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/pecas")}>Cancelar</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
