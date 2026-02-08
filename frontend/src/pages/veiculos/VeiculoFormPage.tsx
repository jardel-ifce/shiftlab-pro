import { useEffect, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft, Loader2, CheckCircle2, X } from "lucide-react"
import { useVeiculo, useCreateVeiculo, useUpdateVeiculo } from "@/hooks/useVeiculos"
import { useBuscaCliente } from "@/hooks/useClientes"
import { formatCpfCnpj } from "@/lib/masks"
import { TIPOS_CAMBIO } from "@/types/veiculo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface FormData {
  placa: string
  marca: string
  modelo: string
  ano: number
  tipo_cambio: string
  quilometragem_atual: number
  cor: string
  observacoes: string
}

export function VeiculoFormPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const [searchInput, setSearchInput] = useState("")
  const { cliente, sugestoes, buscando, erro, buscarSugestoes, selecionar, carregarPorId, limpar } = useBuscaCliente()

  const { data: veiculo, isLoading: loadingVeiculo } = useVeiculo(isEditing ? Number(id) : undefined)
  const createMutation = useCreateVeiculo()
  const updateMutation = useUpdateVeiculo()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  // Pre-select client from query param (e.g. /veiculos/novo?cliente=5)
  useEffect(() => {
    if (isEditing || cliente) return
    const clienteParam = searchParams.get("cliente")
    if (clienteParam) {
      carregarPorId(Number(clienteParam))
    }
  }, [isEditing, cliente, searchParams, carregarPorId])

  // When editing, load the client from the vehicle's cliente_id
  useEffect(() => {
    if (veiculo) {
      carregarPorId(veiculo.cliente_id)
      reset({
        placa: veiculo.placa,
        marca: veiculo.marca,
        modelo: veiculo.modelo,
        ano: veiculo.ano,
        tipo_cambio: veiculo.tipo_cambio,
        quilometragem_atual: veiculo.quilometragem_atual,
        cor: veiculo.cor || "",
        observacoes: veiculo.observacoes || "",
      })
    }
  }, [veiculo, reset, carregarPorId])

  function handleSearchChange(value: string) {
    setSearchInput(value)
    buscarSugestoes(value)
  }

  function handleLimparCliente() {
    setSearchInput("")
    limpar()
  }

  async function onSubmit(formData: FormData) {
    if (!cliente) {
      toast.error("Busque e selecione um cliente.")
      return
    }

    try {
      if (isEditing) {
        await updateMutation.mutateAsync({
          id: Number(id),
          payload: {
            marca: formData.marca,
            modelo: formData.modelo,
            ano: Number(formData.ano),
            tipo_cambio: formData.tipo_cambio,
            quilometragem_atual: Number(formData.quilometragem_atual),
            cor: formData.cor || null,
            observacoes: formData.observacoes || null,
            cliente_id: cliente.id,
          },
        })
        toast.success("Veículo atualizado com sucesso!")
      } else {
        await createMutation.mutateAsync({
          placa: formData.placa.toUpperCase().replace(/[^A-Z0-9]/g, ""),
          marca: formData.marca,
          modelo: formData.modelo,
          ano: Number(formData.ano),
          tipo_cambio: formData.tipo_cambio,
          quilometragem_atual: Number(formData.quilometragem_atual) || 0,
          cor: formData.cor || null,
          observacoes: formData.observacoes || null,
          cliente_id: cliente.id,
        })
        toast.success("Veículo cadastrado com sucesso!")
      }
      navigate("/veiculos")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar veículo.")
    }
  }

  if (isEditing && loadingVeiculo) {
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
  const currentYear = new Date().getFullYear()

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/veiculos")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Veículo" : "Novo Veículo"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? "Atualize os dados do veículo." : "Preencha os dados do veículo."}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Dados do Veículo</CardTitle></CardHeader>
        <CardContent>
          {/* Client autocomplete search */}
          <div className="mb-6 space-y-2">
            <Label>Cliente *</Label>
            {cliente ? (
              <div className="flex items-center gap-3 rounded-md border border-green-200 bg-green-50 p-3 dark:border-green-800 dark:bg-green-950">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium">{cliente.nome}</p>
                  <p className="text-xs text-muted-foreground">
                    CPF/CNPJ: {formatCpfCnpj(cliente.cpf_cnpj)}
                  </p>
                </div>
                {!isEditing && (
                  <Button type="button" variant="ghost" size="icon" onClick={handleLimparCliente}>
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ) : (
              <div className="relative">
                <Input
                  placeholder="Digite CPF, CNPJ ou nome do cliente..."
                  value={searchInput}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  autoComplete="off"
                />
                {buscando && (
                  <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
                )}
                {sugestoes.length > 0 && (
                  <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover shadow-md">
                    {sugestoes.map((c) => (
                      <button
                        key={c.id}
                        type="button"
                        className="flex w-full items-center gap-3 px-3 py-2 text-left text-sm hover:bg-accent"
                        onClick={() => {
                          selecionar(c)
                          setSearchInput("")
                        }}
                      >
                        <div>
                          <p className="font-medium">{c.nome}</p>
                          <p className="text-xs text-muted-foreground">{formatCpfCnpj(c.cpf_cnpj)}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {erro && <p className="text-xs text-destructive">{erro}</p>}
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="placa">Placa *</Label>
                <Input
                  id="placa"
                  placeholder="ABC1D23"
                  maxLength={10}
                  disabled={isEditing}
                  {...register("placa", {
                    required: "Placa é obrigatória",
                    pattern: { value: /^[A-Za-z]{3}\d[A-Za-z0-9]\d{2}$/, message: "Formato: ABC1234 ou ABC1D23" },
                  })}
                />
                {errors.placa && <p className="text-xs text-destructive">{errors.placa.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input id="marca" placeholder="Toyota, Honda..." {...register("marca", { required: "Marca é obrigatória", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.marca && <p className="text-xs text-destructive">{errors.marca.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Input id="modelo" placeholder="Corolla, Civic..." {...register("modelo", { required: "Modelo é obrigatório" })} />
                {errors.modelo && <p className="text-xs text-destructive">{errors.modelo.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="ano">Ano *</Label>
                <Input id="ano" type="number" min={1900} max={currentYear + 1} {...register("ano", { required: "Ano é obrigatório", min: { value: 1900, message: "Ano inválido" }, max: { value: currentYear + 1, message: "Ano inválido" } })} />
                {errors.ano && <p className="text-xs text-destructive">{errors.ano.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_cambio">Tipo de Câmbio *</Label>
                <select
                  id="tipo_cambio"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  {...register("tipo_cambio", { required: "Selecione o tipo de câmbio" })}
                >
                  {TIPOS_CAMBIO.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="quilometragem_atual">Quilometragem</Label>
                <Input id="quilometragem_atual" type="number" min={0} placeholder="0" {...register("quilometragem_atual")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cor">Cor</Label>
                <Input id="cor" placeholder="Branco, Preto..." {...register("cor")} />
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
              <Button type="submit" disabled={isPending || !cliente}>
                {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/veiculos")}>Cancelar</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
