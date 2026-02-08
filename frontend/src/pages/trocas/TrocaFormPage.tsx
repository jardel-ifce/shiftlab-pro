import { useEffect, useMemo, useRef, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft, Loader2, CheckCircle2, X, Plus, Trash2 } from "lucide-react"
import { useTroca, useCreateTroca, useUpdateTroca } from "@/hooks/useTrocas"
import { useBuscaCliente } from "@/hooks/useClientes"
import { useAllVeiculos } from "@/hooks/useVeiculos"
import { useAllOleos } from "@/hooks/useOleos"
import { useAllPecas } from "@/hooks/usePecas"
import { useAllServicos } from "@/hooks/useServicos"
import { formatCpfCnpj } from "@/lib/masks"
import type { ItemTrocaCreate } from "@/types/troca"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

interface FormData {
  veiculo_id: string
  oleo_id: string
  data_troca: string
  quilometragem_troca: string
  quantidade_litros: string
  valor_oleo: string
  valor_servico: string
  desconto_percentual: string
  desconto_valor: string
  motivo_desconto: string
  proxima_troca_km: string
  proxima_troca_data: string
  observacoes: string
}

interface ItemPeca {
  peca_id: string
  quantidade: string
  valor_unitario: string
}

const DRAFT_KEY = "shiftlab_troca_draft"

interface DraftState {
  form: Partial<FormData>
  clienteId: number | null
  itensPecas: ItemPeca[]
}

function saveDraft(state: DraftState) {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(state))
}

function loadDraft(): DraftState | null {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function clearDraft() {
  sessionStorage.removeItem(DRAFT_KEY)
}

export function TrocaFormPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const [searchInput, setSearchInput] = useState("")
  const { cliente, sugestoes, buscando, erro, buscarSugestoes, selecionar, carregarPorId, limpar } = useBuscaCliente()

  const { data: troca, isLoading } = useTroca(isEditing ? Number(id) : undefined)
  const { data: veiculosData } = useAllVeiculos()
  const { data: oleosData } = useAllOleos()
  const { data: pecasData } = useAllPecas()
  const { data: servicosData } = useAllServicos()
  const createMutation = useCreateTroca()
  const updateMutation = useUpdateTroca()

  const [itensPecas, setItensPecas] = useState<ItemPeca[]>([])
  const [servicoId, setServicoId] = useState<string>("")
  const restoredRef = useRef(false)
  const submittedRef = useRef(false)

  const veiculosDoCliente = useMemo(() => {
    if (!veiculosData?.items || !cliente) return []
    return veiculosData.items.filter((v) => v.cliente_id === cliente.id && v.ativo)
  }, [veiculosData, cliente])

  const pecasAtivas = useMemo(() => {
    if (!pecasData?.items) return []
    return pecasData.items.filter((p) => p.ativo)
  }, [pecasData])

  const servicosAtivos = useMemo(() => {
    if (!servicosData?.items) return []
    return servicosData.items.filter((s) => s.ativo)
  }, [servicosData])

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      data_troca: new Date().toISOString().split("T")[0],
      desconto_percentual: "0",
      desconto_valor: "0",
      valor_oleo: "0",
      valor_servico: "0",
      quantidade_litros: "",
    },
  })

  const veiculoIdValue = watch("veiculo_id")
  const oleoIdValue = watch("oleo_id")
  const qtdLitros = watch("quantidade_litros")
  const valorOleo = watch("valor_oleo")
  const valorServico = watch("valor_servico")
  const descontoPerc = watch("desconto_percentual")
  const descontoVal = watch("desconto_valor")

  // Auto-fill oil price when oil is selected
  const oleoSelecionado = useMemo(() => {
    if (!oleoIdValue || !oleosData?.items) return null
    return oleosData.items.find((o) => o.id === Number(oleoIdValue)) || null
  }, [oleoIdValue, oleosData])

  useEffect(() => {
    if (oleoSelecionado && !isEditing) {
      const precoTotal = Number(oleoSelecionado.preco_litro) * Number(qtdLitros || 0)
      setValue("valor_oleo", precoTotal.toFixed(2))
    }
  }, [oleoSelecionado, qtdLitros, setValue, isEditing])

  // Auto-fill service price when a service is selected
  useEffect(() => {
    if (!servicoId) return
    const servico = servicosAtivos.find((s) => s.id === Number(servicoId))
    if (servico) {
      setValue("valor_servico", Number(servico.preco).toFixed(2))
    }
  }, [servicoId, servicosAtivos, setValue])

  // When editing, load client and items
  useEffect(() => {
    if (troca && veiculosData?.items) {
      const veiculo = veiculosData.items.find((v) => v.id === troca.veiculo_id)
      if (veiculo) {
        carregarPorId(veiculo.cliente_id)
      }
      reset({
        veiculo_id: String(troca.veiculo_id),
        oleo_id: String(troca.oleo_id),
        data_troca: troca.data_troca,
        quilometragem_troca: String(troca.quilometragem_troca),
        quantidade_litros: troca.quantidade_litros,
        valor_oleo: troca.valor_oleo,
        valor_servico: troca.valor_servico,
        desconto_percentual: troca.desconto_percentual,
        desconto_valor: troca.desconto_valor,
        motivo_desconto: troca.motivo_desconto || "",
        proxima_troca_km: troca.proxima_troca_km ? String(troca.proxima_troca_km) : "",
        proxima_troca_data: troca.proxima_troca_data || "",
        observacoes: troca.observacoes || "",
      })
      if (troca.itens?.length) {
        setItensPecas(
          troca.itens.map((it) => ({
            peca_id: String(it.peca_id),
            quantidade: String(it.quantidade),
            valor_unitario: String(it.valor_unitario),
          }))
        )
      }
    }
  }, [troca, veiculosData, reset, carregarPorId])

  // Restore draft from sessionStorage (only for new trocas)
  useEffect(() => {
    if (isEditing || restoredRef.current) return
    restoredRef.current = true
    const draft = loadDraft()
    if (!draft) return

    if (draft.form) {
      reset({ ...draft.form } as FormData)
    }
    if (draft.itensPecas?.length) {
      setItensPecas(draft.itensPecas)
    }
    if (draft.clienteId) {
      carregarPorId(draft.clienteId)
    }
  }, [isEditing, reset, carregarPorId])

  // Pre-select vehicle from query param (e.g. /trocas/nova?veiculo=5)
  useEffect(() => {
    if (isEditing || cliente) return
    const veiculoParam = searchParams.get("veiculo")
    if (veiculoParam && veiculosData?.items) {
      const veiculo = veiculosData.items.find((v) => v.id === Number(veiculoParam))
      if (veiculo) {
        carregarPorId(veiculo.cliente_id)
        setValue("veiculo_id", veiculoParam)
      }
    }
  }, [isEditing, cliente, searchParams, veiculosData, carregarPorId, setValue])

  // Auto-save draft to sessionStorage (only for new trocas)
  const allFormValues = watch()
  useEffect(() => {
    if (isEditing || !restoredRef.current || submittedRef.current) return
    saveDraft({
      form: allFormValues,
      clienteId: cliente?.id ?? null,
      itensPecas,
    })
  }, [allFormValues, cliente, itensPecas, isEditing])

  // Calculations
  const subtotalOleo = Number(valorOleo) || 0
  const subtotalPecas = itensPecas.reduce((acc, item) => {
    return acc + (Number(item.quantidade) || 0) * (Number(item.valor_unitario) || 0)
  }, 0)
  const subtotalProdutos = subtotalOleo + subtotalPecas
  const maoDeObra = Number(valorServico) || 0
  const subtotalGeral = subtotalProdutos + maoDeObra
  const descPerc = subtotalGeral * ((Number(descontoPerc) || 0) / 100)
  const descVal = Number(descontoVal) || 0
  const valorTotal = Math.max(0, subtotalGeral - descPerc - descVal)

  function handleSearchChange(value: string) {
    setSearchInput(value)
    buscarSugestoes(value)
  }

  function handleLimparCliente() {
    setSearchInput("")
    limpar()
    setValue("veiculo_id", "")
  }

  function addItem() {
    setItensPecas((prev) => [...prev, { peca_id: "", quantidade: "1", valor_unitario: "0" }])
  }

  function removeItem(index: number) {
    setItensPecas((prev) => prev.filter((_, i) => i !== index))
  }

  function updateItem(index: number, field: keyof ItemPeca, value: string) {
    setItensPecas((prev) => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: value }

      // Auto-fill price when selecting a peca
      if (field === "peca_id" && value) {
        const peca = pecasAtivas.find((p) => p.id === Number(value))
        if (peca) {
          updated[index].valor_unitario = peca.preco_venda
        }
      }
      return updated
    })
  }

  async function onSubmit(formData: FormData) {
    try {
      const itens: ItemTrocaCreate[] = itensPecas
        .filter((it) => it.peca_id)
        .map((it) => ({
          peca_id: Number(it.peca_id),
          quantidade: Number(it.quantidade),
          valor_unitario: Number(it.valor_unitario),
        }))

      const base = {
        data_troca: formData.data_troca,
        quilometragem_troca: Number(formData.quilometragem_troca),
        quantidade_litros: Number(formData.quantidade_litros),
        oleo_id: Number(formData.oleo_id),
        valor_oleo: Number(formData.valor_oleo) || 0,
        valor_servico: Number(formData.valor_servico) || 0,
        desconto_percentual: Number(formData.desconto_percentual) || 0,
        desconto_valor: Number(formData.desconto_valor) || 0,
        motivo_desconto: formData.motivo_desconto || null,
        proxima_troca_km: formData.proxima_troca_km ? Number(formData.proxima_troca_km) : null,
        proxima_troca_data: formData.proxima_troca_data || null,
        observacoes: formData.observacoes || null,
        itens,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: Number(id), payload: base })
        toast.success("Troca atualizada com sucesso!")
      } else {
        await createMutation.mutateAsync({
          ...base,
          veiculo_id: Number(formData.veiculo_id),
        })
        toast.success("Troca registrada com sucesso!")
      }
      submittedRef.current = true
      clearDraft()
      navigate("/trocas")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar troca.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-[600px] w-full" />
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending
  const selectClass = "flex h-9 w-full rounded-md border border-input bg-background px-2 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"

  const R = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <div className="mx-auto max-w-4xl">
      {/* Back button */}
      <div className="mb-4 flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={() => navigate("/trocas")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm text-muted-foreground">Voltar para listagem</span>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="border-2 border-zinc-300 dark:border-zinc-600">
          {/* ─── HEADER ─── */}
          <div className="flex items-center justify-between border-b-2 border-zinc-300 bg-zinc-50 px-4 py-3 dark:border-zinc-600 dark:bg-zinc-900">
            <h1 className="text-lg font-bold tracking-wide uppercase">
              {isEditing ? "Editar Ordem de Serviço" : "Ordem de Serviço"}
            </h1>
            <div className="text-right text-sm">
              {isEditing && <p className="font-semibold">Nº {id}</p>}
              <p className="text-muted-foreground">
                {new Date().toLocaleDateString("pt-BR")}
              </p>
            </div>
          </div>

          {/* ─── CLIENTE + VEÍCULO ─── */}
          <div className="grid grid-cols-1 border-b-2 border-zinc-300 dark:border-zinc-600 md:grid-cols-2">
            {/* Cliente */}
            <div className="border-b-2 border-zinc-300 p-4 dark:border-zinc-600 md:border-b-0 md:border-r-2">
              <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Cliente
              </p>
              {cliente ? (
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                  <div className="flex-1 text-sm">
                    <p className="font-semibold">{cliente.nome}</p>
                    <p className="text-muted-foreground">
                      CPF/CNPJ: {formatCpfCnpj(cliente.cpf_cnpj)}
                    </p>
                    {cliente.telefone && (
                      <p className="text-muted-foreground">Tel: {cliente.telefone}</p>
                    )}
                  </div>
                  {!isEditing && (
                    <Button type="button" variant="ghost" size="icon" className="h-6 w-6" onClick={handleLimparCliente}>
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              ) : (
                <div className="relative">
                  <Input
                    placeholder="Digite CPF, CNPJ ou nome..."
                    value={searchInput}
                    onChange={(e) => handleSearchChange(e.target.value)}
                    autoComplete="off"
                    className="h-9 text-sm"
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
                  {erro && <p className="mt-1 text-xs text-destructive">{erro}</p>}
                </div>
              )}
            </div>

            {/* Veículo */}
            <div className="p-4">
              <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Veículo
              </p>
              <select
                className={selectClass}
                disabled={isEditing || !cliente}
                value={veiculoIdValue || ""}
                {...register("veiculo_id", { required: "Selecione o veículo" })}
              >
                <option value="">
                  {!cliente ? "Busque o cliente primeiro..." : "Selecione o veículo..."}
                </option>
                {veiculosDoCliente.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.placa} — {v.marca} {v.modelo} ({v.ano})
                  </option>
                ))}
              </select>
              {errors.veiculo_id && <p className="mt-1 text-xs text-destructive">{errors.veiculo_id.message}</p>}
              {cliente && veiculosDoCliente.length === 0 && (
                <p className="mt-1 text-xs text-orange-500">Nenhum veículo ativo cadastrado.</p>
              )}

              <div className="mt-3 grid grid-cols-2 gap-3">
                <div>
                  <p className="mb-1 text-xs text-muted-foreground">KM Atual *</p>
                  <Input
                    type="number"
                    min={0}
                    placeholder="0"
                    className="h-9 text-sm"
                    {...register("quilometragem_troca", { required: "KM é obrigatório" })}
                  />
                  {errors.quilometragem_troca && <p className="mt-1 text-xs text-destructive">{errors.quilometragem_troca.message}</p>}
                </div>
                <div>
                  <p className="mb-1 text-xs text-muted-foreground">Data *</p>
                  <Input
                    type="date"
                    max={new Date().toISOString().split("T")[0]}
                    className="h-9 text-sm"
                    {...register("data_troca", { required: "Data é obrigatória" })}
                  />
                  {errors.data_troca && <p className="mt-1 text-xs text-destructive">{errors.data_troca.message}</p>}
                </div>
              </div>
            </div>
          </div>

          {/* ─── TABELA DE PRODUTOS / SERVIÇOS ─── */}
          <div className="border-b-2 border-zinc-300 dark:border-zinc-600">
            <div className="flex items-center justify-between bg-zinc-50 px-4 py-2 dark:bg-zinc-900">
              <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Produtos / Serviços
              </p>
              <Button type="button" variant="outline" size="sm" className="h-7 gap-1 text-xs" onClick={addItem}>
                <Plus className="h-3 w-3" /> Item
              </Button>
            </div>

            {/* Table header */}
            <div className="grid grid-cols-[40px_1fr_60px_70px_90px_90px_40px] items-center gap-1 border-b border-zinc-200 bg-zinc-100 px-2 py-1.5 text-xs font-semibold uppercase text-muted-foreground dark:border-zinc-700 dark:bg-zinc-800">
              <span className="text-center">#</span>
              <span>Descrição</span>
              <span className="text-center">Unid</span>
              <span className="text-center">Qtd</span>
              <span className="text-right">V. Unit</span>
              <span className="text-right">Total</span>
              <span></span>
            </div>

            {/* Row: Óleo (mandatory) */}
            <div className="grid grid-cols-[40px_1fr_60px_70px_90px_90px_40px] items-center gap-1 border-b border-zinc-200 px-2 py-1.5 dark:border-zinc-700">
              <span className="text-center text-xs text-muted-foreground">1</span>
              <select
                className="h-8 w-full rounded border border-input bg-background px-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                {...register("oleo_id", { required: "Selecione o óleo" })}
              >
                <option value="">Selecione o óleo...</option>
                {oleosData?.items.filter((o) => o.ativo).map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.nome} ({o.marca}) — R$ {Number(o.preco_litro).toFixed(2)}/L — Est: {Number(o.estoque_litros).toFixed(1)}L
                  </option>
                ))}
              </select>
              <span className="text-center text-xs text-muted-foreground">L</span>
              <Input
                type="number"
                step="0.1"
                min="0.1"
                max="50"
                placeholder="0"
                className="h-8 px-1 text-center text-xs"
                {...register("quantidade_litros", { required: "Obrigatório" })}
              />
              <div className="text-right text-xs text-muted-foreground">
                {oleoSelecionado ? `R$ ${Number(oleoSelecionado.preco_litro).toFixed(2)}/L` : "—"}
              </div>
              <div className="text-right text-xs font-medium">
                R$ {R(subtotalOleo)}
              </div>
              <div>{/* no remove for oil */}</div>
            </div>
            {errors.oleo_id && <p className="px-2 py-1 text-xs text-destructive">{errors.oleo_id.message}</p>}

            {/* Additional peca rows */}
            {itensPecas.map((item, index) => {
              const itemTotal = (Number(item.quantidade) || 0) * (Number(item.valor_unitario) || 0)
              const pecaSelecionada = item.peca_id ? pecasAtivas.find((p) => p.id === Number(item.peca_id)) : null
              return (
                <div
                  key={index}
                  className="grid grid-cols-[40px_1fr_60px_70px_90px_90px_40px] items-center gap-1 border-b border-zinc-200 px-2 py-1.5 dark:border-zinc-700"
                >
                  <span className="text-center text-xs text-muted-foreground">{index + 2}</span>
                  <select
                    className="h-8 w-full rounded border border-input bg-background px-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={item.peca_id}
                    onChange={(e) => updateItem(index, "peca_id", e.target.value)}
                  >
                    <option value="">Selecione a peça...</option>
                    {pecasAtivas.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nome} {p.marca ? `(${p.marca})` : ""} — R$ {Number(p.preco_venda).toFixed(2)} — Est: {Number(p.estoque).toFixed(0)}
                      </option>
                    ))}
                  </select>
                  <span className="text-center text-xs text-muted-foreground">
                    {pecaSelecionada?.unidade || "un"}
                  </span>
                  <Input
                    type="number"
                    step="1"
                    min="1"
                    className="h-8 px-1 text-center text-xs"
                    value={item.quantidade}
                    onChange={(e) => updateItem(index, "quantidade", e.target.value)}
                  />
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    className="h-8 px-1 text-right text-xs"
                    value={item.valor_unitario}
                    onChange={(e) => updateItem(index, "valor_unitario", e.target.value)}
                  />
                  <div className="text-right text-xs font-medium">
                    R$ {R(itemTotal)}
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => removeItem(index)}
                  >
                    <Trash2 className="h-3 w-3 text-destructive" />
                  </Button>
                </div>
              )
            })}

            {/* Valor do óleo (editable) hidden input */}
            <input type="hidden" {...register("valor_oleo")} />
          </div>

          {/* ─── TOTAIS ─── */}
          <div className="border-b-2 border-zinc-300 dark:border-zinc-600">
            <div className="flex justify-end">
              <div className="w-full max-w-sm space-y-1 p-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Subtotal Produtos:</span>
                  <span>R$ {R(subtotalProdutos)}</span>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-muted-foreground">Serviço:</span>
                  <div className="flex items-center gap-1">
                    <select
                      className="h-8 w-32 rounded-md border border-input bg-background px-1 text-xs ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={servicoId}
                      onChange={(e) => setServicoId(e.target.value)}
                    >
                      <option value="">Manual</option>
                      {servicosAtivos.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.nome}
                        </option>
                      ))}
                    </select>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                      className="h-8 w-28 text-right text-sm"
                      {...register("valor_servico")}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-muted-foreground">Desconto (%):</span>
                  <Input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    placeholder="0"
                    className="h-8 w-28 text-right text-sm"
                    {...register("desconto_percentual")}
                  />
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-muted-foreground">Desconto (R$):</span>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    className="h-8 w-28 text-right text-sm"
                    {...register("desconto_valor")}
                  />
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-muted-foreground">Motivo:</span>
                  <Input
                    placeholder="Ex: Cliente fiel"
                    className="h-8 w-28 text-right text-sm"
                    {...register("motivo_desconto")}
                  />
                </div>
                <div className="border-t border-zinc-300 pt-2 dark:border-zinc-600">
                  <div className="flex justify-between text-base font-bold">
                    <span>VALOR TOTAL:</span>
                    <span>R$ {R(valorTotal)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ─── PRÓXIMA TROCA ─── */}
          <div className="border-b-2 border-zinc-300 p-4 dark:border-zinc-600">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Próxima Troca
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="mb-1 text-xs text-muted-foreground">KM</p>
                <Input
                  type="number"
                  min="0"
                  placeholder="Ex: 150000"
                  className="h-9 text-sm"
                  {...register("proxima_troca_km")}
                />
              </div>
              <div>
                <p className="mb-1 text-xs text-muted-foreground">Data</p>
                <Input
                  type="date"
                  className="h-9 text-sm"
                  {...register("proxima_troca_data")}
                />
              </div>
            </div>
          </div>

          {/* ─── OBSERVAÇÕES ─── */}
          <div className="border-b-2 border-zinc-300 p-4 dark:border-zinc-600">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Observações
            </p>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              placeholder="Observações sobre a troca..."
              {...register("observacoes")}
            />
          </div>

          {/* ─── AÇÕES ─── */}
          <div className="flex items-center gap-3 bg-zinc-50 px-4 py-3 dark:bg-zinc-900">
            <Button type="submit" disabled={isPending}>
              {isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Salvando...
                </>
              ) : isEditing ? (
                "Atualizar Troca"
              ) : (
                "Registrar Troca"
              )}
            </Button>
            <Button type="button" variant="outline" onClick={() => { clearDraft(); navigate("/trocas") }}>
              Cancelar
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}
