import { useEffect } from "react"
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

interface FormData {
  nome: string
  marca: string
  unidade: string
  preco_custo: string
  preco_venda: string
  estoque: string
  estoque_minimo: string
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

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  useEffect(() => {
    if (peca) {
      reset({
        nome: peca.nome,
        marca: peca.marca || "",
        unidade: peca.unidade,
        preco_custo: peca.preco_custo,
        preco_venda: peca.preco_venda,
        estoque: peca.estoque,
        estoque_minimo: peca.estoque_minimo,
        comentarios: peca.comentarios || "",
        observacoes: peca.observacoes || "",
      })
    }
  }, [peca, reset])

  async function onSubmit(formData: FormData) {
    try {
      const payload = {
        nome: formData.nome,
        marca: formData.marca || null,
        unidade: formData.unidade || "unidade",
        preco_custo: Number(formData.preco_custo) || 0,
        preco_venda: Number(formData.preco_venda) || 0,
        estoque: Number(formData.estoque) || 0,
        estoque_minimo: Number(formData.estoque_minimo) || 5,
        comentarios: formData.comentarios || null,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: Number(id), payload })
        toast.success("Peça atualizada com sucesso!")
      } else {
        await createMutation.mutateAsync(payload)
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
                <Input id="unidade" placeholder="unidade, litro, pacote..." defaultValue="unidade" {...register("unidade")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="preco_custo">Preço de Custo (R$)</Label>
                <Input id="preco_custo" type="number" step="0.01" min="0" placeholder="0.00" {...register("preco_custo")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="preco_venda">Preço de Venda (R$) *</Label>
                <Input id="preco_venda" type="number" step="0.01" min="0" placeholder="0.00" {...register("preco_venda", { required: "Informe o preço de venda" })} />
                {errors.preco_venda && <p className="text-xs text-destructive">{errors.preco_venda.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="estoque">Estoque Atual</Label>
                <Input id="estoque" type="number" step="0.1" min="0" placeholder="0" {...register("estoque")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estoque_minimo">Estoque Mínimo</Label>
                <Input id="estoque_minimo" type="number" step="0.1" min="0" placeholder="5" {...register("estoque_minimo")} />
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
