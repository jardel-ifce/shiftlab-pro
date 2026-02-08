import { useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import { useServico, useCreateServico, useUpdateServico } from "@/hooks/useServicos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface FormData {
  nome: string
  descricao: string
  preco: string
  observacoes: string
}

export function ServicoFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: servico, isLoading } = useServico(isEditing ? Number(id) : undefined)
  const createMutation = useCreateServico()
  const updateMutation = useUpdateServico()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  useEffect(() => {
    if (servico) {
      reset({
        nome: servico.nome,
        descricao: servico.descricao || "",
        preco: servico.preco,
        observacoes: servico.observacoes || "",
      })
    }
  }, [servico, reset])

  async function onSubmit(formData: FormData) {
    try {
      const payload = {
        nome: formData.nome,
        descricao: formData.descricao || null,
        preco: Number(formData.preco) || 0,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: Number(id), payload })
        toast.success("Serviço atualizado com sucesso!")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Serviço cadastrado com sucesso!")
      }
      navigate("/servicos")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar serviço.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card><CardContent className="space-y-4 pt-6">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
        </CardContent></Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/servicos")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Serviço" : "Novo Serviço"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? "Atualize os dados do serviço." : "Cadastre um novo tipo de serviço."}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Dados do Serviço</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input
                  id="nome"
                  placeholder="Ex: Troca Simples, SUV/Pickup..."
                  {...register("nome", {
                    required: "Nome é obrigatório",
                    minLength: { value: 2, message: "Mínimo 2 caracteres" },
                  })}
                />
                {errors.nome && <p className="text-xs text-destructive">{errors.nome.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="preco">Preço (R$) *</Label>
                <Input
                  id="preco"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  {...register("preco", { required: "Informe o preço" })}
                />
                {errors.preco && <p className="text-xs text-destructive">{errors.preco.message}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="descricao">Descrição</Label>
              <textarea
                id="descricao"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Descrição do serviço..."
                {...register("descricao")}
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
              <Button type="button" variant="outline" onClick={() => navigate("/servicos")}>Cancelar</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
