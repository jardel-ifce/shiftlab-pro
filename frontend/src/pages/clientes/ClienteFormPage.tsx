import { useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import { useCliente, useCreateCliente, useUpdateCliente } from "@/hooks/useClientes"
import { formatCpfCnpj, formatTelefone, unmask } from "@/lib/masks"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

const clienteSchema = z.object({
  nome: z.string().min(3, "Nome deve ter pelo menos 3 caracteres"),
  telefone: z.string().min(10, "Telefone inválido"),
  email: z.string().email("Email inválido").or(z.literal("")).optional(),
  cpf_cnpj: z.string().min(11, "CPF/CNPJ inválido"),
  endereco: z.string().optional(),
  observacoes: z.string().optional(),
})

type FormData = z.infer<typeof clienteSchema>

export function ClienteFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: cliente, isLoading: isLoadingCliente } = useCliente(
    isEditing ? Number(id) : undefined
  )
  const createMutation = useCreateCliente()
  const updateMutation = useUpdateCliente()

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<FormData>()

  const telefoneValue = watch("telefone")
  const cpfCnpjValue = watch("cpf_cnpj")

  // Populate form when editing
  useEffect(() => {
    if (cliente) {
      reset({
        nome: cliente.nome,
        telefone: formatTelefone(cliente.telefone),
        email: cliente.email || "",
        cpf_cnpj: formatCpfCnpj(cliente.cpf_cnpj),
        endereco: cliente.endereco || "",
        observacoes: cliente.observacoes || "",
      })
    }
  }, [cliente, reset])

  // Apply masks on change
  useEffect(() => {
    if (telefoneValue) {
      const masked = formatTelefone(telefoneValue)
      if (masked !== telefoneValue) setValue("telefone", masked)
    }
  }, [telefoneValue, setValue])

  useEffect(() => {
    if (cpfCnpjValue) {
      const masked = formatCpfCnpj(cpfCnpjValue)
      if (masked !== cpfCnpjValue) setValue("cpf_cnpj", masked)
    }
  }, [cpfCnpjValue, setValue])

  async function onSubmit(formData: FormData) {
    try {
      const payload = {
        nome: formData.nome,
        telefone: unmask(formData.telefone),
        email: formData.email || null,
        cpf_cnpj: unmask(formData.cpf_cnpj),
        endereco: formData.endereco || null,
        observacoes: formData.observacoes || null,
      }

      if (isEditing) {
        // cpf_cnpj is immutable, don't send on update
        const { cpf_cnpj: _cpf, ...updatePayload } = payload
        void _cpf
        await updateMutation.mutateAsync({ id: Number(id), payload: updatePayload })
        toast.success("Cliente atualizado com sucesso!")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Cliente cadastrado com sucesso!")
      }
      navigate("/clientes")
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar cliente.")
    }
  }

  // Validate form
  function onError() {
    const firstError = Object.values(errors)[0]
    if (firstError?.message) {
      toast.error(String(firstError.message))
    }
  }

  if (isEditing && isLoadingCliente) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card>
          <CardContent className="space-y-4 pt-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/clientes")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Cliente" : "Novo Cliente"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing
              ? "Atualize os dados do cliente."
              : "Preencha os dados para cadastrar um novo cliente."}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dados do Cliente</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit, onError)}
            className="space-y-4"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input
                  id="nome"
                  placeholder="Nome completo"
                  {...register("nome", {
                    required: "Nome é obrigatório",
                    minLength: { value: 3, message: "Mínimo 3 caracteres" },
                  })}
                />
                {errors.nome && (
                  <p className="text-xs text-destructive">{errors.nome.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="cpf_cnpj">CPF/CNPJ *</Label>
                <Input
                  id="cpf_cnpj"
                  placeholder="000.000.000-00"
                  maxLength={18}
                  disabled={isEditing}
                  {...register("cpf_cnpj", {
                    required: "CPF/CNPJ é obrigatório",
                    validate: (v) => {
                      const digits = unmask(v)
                      return (
                        digits.length === 11 ||
                        digits.length === 14 ||
                        "CPF deve ter 11 dígitos ou CNPJ 14 dígitos"
                      )
                    },
                  })}
                />
                {errors.cpf_cnpj && (
                  <p className="text-xs text-destructive">{errors.cpf_cnpj.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="telefone">Telefone *</Label>
                <Input
                  id="telefone"
                  placeholder="(00) 00000-0000"
                  maxLength={15}
                  {...register("telefone", {
                    required: "Telefone é obrigatório",
                    validate: (v) =>
                      unmask(v).length >= 10 || "Telefone inválido",
                  })}
                />
                {errors.telefone && (
                  <p className="text-xs text-destructive">{errors.telefone.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="cliente@email.com"
                  {...register("email")}
                />
                {errors.email && (
                  <p className="text-xs text-destructive">{errors.email.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="endereco">Endereço</Label>
              <Input
                id="endereco"
                placeholder="Rua, número, bairro, cidade"
                {...register("endereco")}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <textarea
                id="observacoes"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Observações sobre o cliente..."
                {...register("observacoes")}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={isPending}>
                {isPending
                  ? "Salvando..."
                  : isEditing
                    ? "Atualizar"
                    : "Cadastrar"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/clientes")}
              >
                Cancelar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
