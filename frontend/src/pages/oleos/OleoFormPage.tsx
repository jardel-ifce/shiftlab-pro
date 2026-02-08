import { useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import { useOleo, useCreateOleo, useUpdateOleo } from "@/hooks/useOleos"
import { TIPOS_OLEO } from "@/types/oleo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface FormData {
  nome: string
  marca: string
  tipo: string
  viscosidade: string
  especificacao: string
  custo_litro: string
  preco_litro: string
  estoque_litros: string
  estoque_minimo: string
  observacoes: string
}

export function OleoFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: oleo, isLoading } = useOleo(isEditing ? Number(id) : undefined)
  const createMutation = useCreateOleo()
  const updateMutation = useUpdateOleo()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  useEffect(() => {
    if (oleo) {
      reset({
        nome: oleo.nome,
        marca: oleo.marca,
        tipo: oleo.tipo,
        viscosidade: oleo.viscosidade || "",
        especificacao: oleo.especificacao || "",
        custo_litro: oleo.custo_litro,
        preco_litro: oleo.preco_litro,
        estoque_litros: oleo.estoque_litros,
        estoque_minimo: oleo.estoque_minimo,
        observacoes: oleo.observacoes || "",
      })
    }
  }, [oleo, reset])

  async function onSubmit(formData: FormData) {
    try {
      const payload = {
        nome: formData.nome,
        marca: formData.marca,
        tipo: formData.tipo,
        viscosidade: formData.viscosidade || null,
        especificacao: formData.especificacao || null,
        custo_litro: Number(formData.custo_litro) || 0,
        preco_litro: Number(formData.preco_litro) || 0,
        estoque_litros: Number(formData.estoque_litros) || 0,
        estoque_minimo: Number(formData.estoque_minimo) || 5,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: Number(id), payload })
        toast.success("Óleo atualizado com sucesso!")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Óleo cadastrado com sucesso!")
      }
      navigate("/oleos")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar óleo.")
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
        <Button variant="ghost" size="icon" onClick={() => navigate("/oleos")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Óleo" : "Novo Óleo"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? "Atualize os dados do produto." : "Cadastre um novo óleo no sistema."}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Dados do Produto</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input id="nome" placeholder="Dexron VI, Multi ATF..." {...register("nome", { required: "Nome é obrigatório", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.nome && <p className="text-xs text-destructive">{errors.nome.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input id="marca" placeholder="ZF, Mobil, Shell..." {...register("marca", { required: "Marca é obrigatória", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.marca && <p className="text-xs text-destructive">{errors.marca.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo *</Label>
                <select
                  id="tipo"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  {...register("tipo", { required: "Selecione o tipo" })}
                >
                  {TIPOS_OLEO.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="viscosidade">Viscosidade</Label>
                <Input id="viscosidade" placeholder="75W-90, ATF+4..." {...register("viscosidade")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="especificacao">Especificação</Label>
                <Input id="especificacao" placeholder="Dexron VI, Mercon V..." {...register("especificacao")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="custo_litro">Custo/Litro (R$)</Label>
                <Input id="custo_litro" type="number" step="0.01" min="0" placeholder="0.00" {...register("custo_litro")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="preco_litro">Preço Venda/Litro (R$) *</Label>
                <Input id="preco_litro" type="number" step="0.01" min="0" placeholder="0.00" {...register("preco_litro", { required: "Informe o preço" })} />
                {errors.preco_litro && <p className="text-xs text-destructive">{errors.preco_litro.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="estoque_litros">Estoque Atual (L)</Label>
                <Input id="estoque_litros" type="number" step="0.1" min="0" placeholder="0" {...register("estoque_litros")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estoque_minimo">Estoque Mínimo (L)</Label>
                <Input id="estoque_minimo" type="number" step="0.1" min="0" placeholder="5" {...register("estoque_minimo")} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <textarea
                id="observacoes"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Observações..."
                {...register("observacoes")}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/oleos")}>Cancelar</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
