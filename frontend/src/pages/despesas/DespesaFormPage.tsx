import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import {
  useDespesa,
  useCreateDespesa,
  useUpdateDespesa,
} from "@/hooks/useDespesas"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  formatMoeda,
  parseMoeda,
  numberToMoeda,
} from "@/lib/masks"

const CATEGORIAS = [
  { value: "manutencao", label: "Manutenção" },
  { value: "aluguel", label: "Aluguel" },
  { value: "energia", label: "Energia" },
  { value: "conserto", label: "Conserto" },
  { value: "material", label: "Material" },
  { value: "outros", label: "Outros" },
]

interface FormData {
  data: string
  descricao: string
  categoria: string
  observacoes: string
}

export function DespesaFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: despesa, isLoading } = useDespesa(isEditing ? Number(id) : undefined)
  const createMutation = useCreateDespesa()
  const updateMutation = useUpdateDespesa()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>()

  const [valor, setValor] = useState("")

  useEffect(() => {
    if (despesa) {
      reset({
        data: despesa.data ? despesa.data.split("T")[0] : "",
        descricao: despesa.descricao,
        categoria: despesa.categoria,
        observacoes: despesa.observacoes || "",
      })
      setValor(numberToMoeda(despesa.valor))
    }
  }, [despesa, reset])

  async function onSubmit(formData: FormData) {
    const valorNumerico = parseMoeda(valor)
    if (!valorNumerico) {
      toast.error("Informe o valor da despesa.")
      return
    }

    try {
      const payload = {
        data: formData.data,
        descricao: formData.descricao,
        valor: valorNumerico,
        categoria: formData.categoria,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: Number(id), payload })
        toast.success("Despesa atualizada com sucesso!")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Despesa cadastrada com sucesso!")
      }

      navigate("/despesas")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar despesa.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card>
          <CardContent className="space-y-4 pt-6">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/despesas")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Despesa" : "Nova Despesa"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing
              ? "Atualize os dados da despesa."
              : "Cadastre uma nova despesa operacional."}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Dados da Despesa</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="data">Data *</Label>
                <Input
                  id="data"
                  type="date"
                  {...register("data", { required: "Data é obrigatória" })}
                />
                {errors.data && (
                  <p className="text-xs text-destructive">{errors.data.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="categoria">Categoria *</Label>
                <select
                  id="categoria"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  {...register("categoria", { required: "Categoria é obrigatória" })}
                >
                  <option value="">Selecione...</option>
                  {CATEGORIAS.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
                {errors.categoria && (
                  <p className="text-xs text-destructive">{errors.categoria.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="descricao">Descrição *</Label>
              <Input
                id="descricao"
                placeholder="Descreva a despesa..."
                maxLength={200}
                {...register("descricao", {
                  required: "Descrição é obrigatória",
                  maxLength: { value: 200, message: "Máximo 200 caracteres" },
                })}
              />
              {errors.descricao && (
                <p className="text-xs text-destructive">{errors.descricao.message}</p>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="valor">Valor (R$) *</Label>
                <Input
                  id="valor"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={valor}
                  onChange={(e) => setValor(formatMoeda(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              id="observacoes"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Observações sobre a despesa..."
              {...register("observacoes")}
            />
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={isPending}>
            {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={() => navigate("/despesas")}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
