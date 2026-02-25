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
import { useAllFiltros } from "@/hooks/useFiltros"
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
  taxa_percentual: string
  proxima_troca_km: string
  proxima_troca_data: string
  observacoes: string
}

interface ItemProduto {
  tipo: "peca" | "filtro"
  produto_id: string
  nome: string
  quantidade: string
  valor_unitario: string
}

interface ProdutoBusca {
  tipo: "peca" | "filtro"
  id: number
  nome: string
  marca: string | null
  preco: number
  estoque: number
  unidade: string
}

const FORMAS_PAGAMENTO = [
  "Dinheiro",
  "PIX",
  "Cartão de Débito",
  "Cartão de Crédito",
]

const DRAFT_KEY = "shiftlab_troca_draft"

interface DraftState {
  form: Partial<FormData>
  clienteId: number | null
  itensProdutos: ItemProduto[]
  formasPagamento?: string[]
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

function ItemRowAutocomplete({
  index, item, itemTotal, produtos, onSelect, onClear, onChangeQty, onChangePrice, onRemove, R,
}: {
  index: number
  item: ItemProduto
  itemTotal: number
  produtos: ProdutoBusca[]
  onSelect: (p: ProdutoBusca) => void
  onClear: () => void
  onChangeQty: (v: string) => void
  onChangePrice: (v: string) => void
  onRemove: () => void
  R: (v: number) => string
}) {
  const [busca, setBusca] = useState("")
  const [aberto, setAberto] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const filtrados = useMemo(() => {
    if (!busca) return produtos
    const lower = busca.toLowerCase()
    return produtos.filter(
      (p) => p.nome.toLowerCase().includes(lower) || (p.marca?.toLowerCase().includes(lower))
    )
  }, [busca, produtos])

  // Close dropdown on outside click
  useEffect(() => {
    function handle(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setAberto(false)
    }
    document.addEventListener("mousedown", handle)
    return () => document.removeEventListener("mousedown", handle)
  }, [])

  const selecionado = !!item.produto_id

  return (
    <div className="grid grid-cols-[40px_1fr_60px_70px_90px_90px_40px] items-center gap-1 border-b border-zinc-200 px-2 py-1.5 dark:border-zinc-700">
      <span className="text-center text-xs text-muted-foreground">{index + 2}</span>

      {/* Autocomplete */}
      <div className="relative" ref={ref}>
        {selecionado ? (
          <div className="flex h-8 items-center gap-1 rounded border border-input bg-background px-1">
            <span className={`inline-flex items-center rounded px-1 text-[10px] font-semibold uppercase leading-none ${item.tipo === "filtro" ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"}`}>
              {item.tipo === "filtro" ? "Filtro" : "Peça"}
            </span>
            <span className="flex-1 truncate text-xs">{item.nome}</span>
            <button type="button" className="shrink-0 text-muted-foreground hover:text-foreground" onClick={onClear}>
              <X className="h-3 w-3" />
            </button>
          </div>
        ) : (
          <>
            <Input
              placeholder="Buscar peça ou filtro..."
              className="h-8 text-xs"
              value={busca}
              onChange={(e) => { setBusca(e.target.value); setAberto(true) }}
              onFocus={() => setAberto(true)}
              autoComplete="off"
            />
            {aberto && filtrados.length > 0 && (
              <div className="absolute z-20 mt-1 w-full rounded-md border bg-popover shadow-md">
                <ul className="max-h-48 overflow-auto py-1">
                  {filtrados.map((p) => (
                    <li
                      key={`${p.tipo}-${p.id}`}
                      className="flex cursor-pointer items-center gap-2 px-2 py-1.5 text-xs hover:bg-accent"
                      onClick={() => {
                        onSelect(p)
                        setBusca("")
                        setAberto(false)
                      }}
                    >
                      <span className={`inline-flex items-center rounded px-1 text-[10px] font-semibold uppercase leading-none ${p.tipo === "filtro" ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"}`}>
                        {p.tipo === "filtro" ? "Filtro" : "Peça"}
                      </span>
                      <span className="flex-1 truncate">
                        {p.nome} {p.marca ? `(${p.marca})` : ""}
                      </span>
                      <span className="text-muted-foreground">R$ {p.preco.toFixed(2)}</span>
                      <span className="text-muted-foreground">Est: {p.estoque}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {aberto && busca && filtrados.length === 0 && (
              <div className="absolute z-20 mt-1 w-full rounded-md border bg-popover p-2 text-center text-xs text-muted-foreground shadow-md">
                Nenhum produto encontrado
              </div>
            )}
          </>
        )}
      </div>

      <span className="text-center text-xs text-muted-foreground">un</span>
      <Input
        type="number"
        step="1"
        min="1"
        className="h-8 px-1 text-center text-xs"
        value={item.quantidade}
        onChange={(e) => onChangeQty(e.target.value)}
      />
      <Input
        type="number"
        step="0.01"
        min="0"
        className="h-8 px-1 text-right text-xs"
        value={item.valor_unitario}
        onChange={(e) => onChangePrice(e.target.value)}
      />
      <div className="text-right text-xs font-medium">
        R$ {R(itemTotal)}
      </div>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        onClick={onRemove}
      >
        <Trash2 className="h-3 w-3 text-destructive" />
      </Button>
    </div>
  )
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
  const { data: filtrosData } = useAllFiltros()
  const { data: servicosData } = useAllServicos()
  const createMutation = useCreateTroca()
  const updateMutation = useUpdateTroca()

  const [itensProdutos, setItensProdutos] = useState<ItemProduto[]>([])
  const [formasPagamento, setFormasPagamento] = useState<string[]>([])
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

  const filtrosAtivos = useMemo(() => {
    if (!filtrosData?.items) return []
    return filtrosData.items.filter((f) => f.ativo)
  }, [filtrosData])

  const produtosBusca: ProdutoBusca[] = useMemo(() => {
    const lista: ProdutoBusca[] = []
    for (const p of pecasAtivas) {
      lista.push({
        tipo: "peca",
        id: p.id,
        nome: p.nome,
        marca: p.marca,
        preco: Number(p.preco_venda),
        estoque: Number(p.estoque),
        unidade: p.unidade || "un",
      })
    }
    for (const f of filtrosAtivos) {
      lista.push({
        tipo: "filtro",
        id: f.id,
        nome: f.nome,
        marca: f.marca,
        preco: Number(f.preco_unitario),
        estoque: f.estoque,
        unidade: "un",
      })
    }
    return lista
  }, [pecasAtivas, filtrosAtivos])

  const servicosAtivos = useMemo(() => {
    if (!servicosData?.items) return []
    return servicosData.items.filter((s) => s.ativo)
  }, [servicosData])

  const defaultProximaData = (() => {
    const d = new Date()
    d.setFullYear(d.getFullYear() + 4)
    return d.toISOString().split("T")[0]
  })()

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      data_troca: new Date().toISOString().split("T")[0],
      desconto_percentual: "0",
      desconto_valor: "0",
      taxa_percentual: "0",
      valor_oleo: "0",
      valor_servico: "0",
      quantidade_litros: "",
      proxima_troca_data: defaultProximaData,
    },
  })

  const veiculoIdValue = watch("veiculo_id")
  const oleoIdValue = watch("oleo_id")
  const kmTroca = watch("quilometragem_troca")
  const qtdLitros = watch("quantidade_litros")
  const valorOleo = watch("valor_oleo")
  const valorServico = watch("valor_servico")
  const descontoPerc = watch("desconto_percentual")
  const descontoVal = watch("desconto_valor")
  const taxaPerc = watch("taxa_percentual")

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

  // Auto-fill proxima_troca_km when quilometragem_troca changes (+40.000)
  useEffect(() => {
    if (!isEditing && kmTroca) {
      const km = Number(kmTroca)
      if (km > 0) {
        setValue("proxima_troca_km", String(km + 40000))
      }
    }
  }, [kmTroca, setValue, isEditing])

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
        taxa_percentual: troca.taxa_percentual || "0",
        proxima_troca_km: troca.proxima_troca_km ? String(troca.proxima_troca_km) : "",
        proxima_troca_data: troca.proxima_troca_data || "",
        observacoes: troca.observacoes || "",
      })
      if (troca.forma_pagamento) {
        setFormasPagamento(troca.forma_pagamento.split(",").map((s) => s.trim()))
      }
      if (troca.itens?.length) {
        setItensProdutos(
          troca.itens.map((it) => ({
            tipo: it.filtro_id ? "filtro" as const : "peca" as const,
            produto_id: String(it.filtro_id || it.peca_id),
            nome: it.filtro?.nome || it.peca?.nome || "",
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
      const restored = { ...draft.form } as FormData
      if (!restored.proxima_troca_data) {
        restored.proxima_troca_data = defaultProximaData
      }
      reset(restored)
    }
    if (draft.itensProdutos?.length) {
      setItensProdutos(draft.itensProdutos)
    }
    if (draft.formasPagamento?.length) {
      setFormasPagamento(draft.formasPagamento)
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
      itensProdutos,
      formasPagamento,
    })
  }, [allFormValues, cliente, itensProdutos, formasPagamento, isEditing])

  // Calculations
  const subtotalOleo = Number(valorOleo) || 0
  const subtotalPecas = itensProdutos.reduce((acc, item) => {
    return acc + (Number(item.quantidade) || 0) * (Number(item.valor_unitario) || 0)
  }, 0)
  const subtotalProdutos = subtotalOleo + subtotalPecas
  const maoDeObra = Number(valorServico) || 0
  const subtotalGeral = subtotalProdutos + maoDeObra
  const descPerc = subtotalGeral * ((Number(descontoPerc) || 0) / 100)
  const descVal = Number(descontoVal) || 0
  const subtotalComDesconto = subtotalGeral - descPerc - descVal
  const taxaVal = subtotalComDesconto * ((Number(taxaPerc) || 0) / 100)
  const valorTotal = Math.max(0, subtotalComDesconto - taxaVal)

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
    setItensProdutos((prev) => [...prev, { tipo: "peca", produto_id: "", nome: "", quantidade: "1", valor_unitario: "0" }])
  }

  function removeItem(index: number) {
    setItensProdutos((prev) => prev.filter((_, i) => i !== index))
  }

  function selectProduto(index: number, produto: ProdutoBusca) {
    setItensProdutos((prev) => {
      const updated = [...prev]
      updated[index] = {
        ...updated[index],
        tipo: produto.tipo,
        produto_id: String(produto.id),
        nome: `${produto.nome}${produto.marca ? ` (${produto.marca})` : ""}`,
        valor_unitario: produto.preco.toFixed(2),
      }
      return updated
    })
  }

  function updateItemField(index: number, field: "quantidade" | "valor_unitario", value: string) {
    setItensProdutos((prev) => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: value }
      return updated
    })
  }

  function clearItemProduto(index: number) {
    setItensProdutos((prev) => {
      const updated = [...prev]
      updated[index] = { ...updated[index], tipo: "peca", produto_id: "", nome: "", valor_unitario: "0" }
      return updated
    })
  }

  async function onSubmit(formData: FormData) {
    try {
      const itens: ItemTrocaCreate[] = itensProdutos
        .filter((it) => it.produto_id)
        .map((it) => ({
          peca_id: it.tipo === "peca" ? Number(it.produto_id) : null,
          filtro_id: it.tipo === "filtro" ? Number(it.produto_id) : null,
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
        taxa_percentual: Number(formData.taxa_percentual) || 0,
        proxima_troca_km: formData.proxima_troca_km ? Number(formData.proxima_troca_km) : null,
        proxima_troca_data: formData.proxima_troca_data || null,
        observacoes: formData.observacoes || null,
        forma_pagamento: formasPagamento.length > 0 ? formasPagamento.join(", ") : null,
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
                <div className="min-w-0">
                  <p className="mb-1 text-xs text-muted-foreground">KM Atual *</p>
                  <Input
                    type="number"
                    min={0}
                    placeholder="0"
                    className="h-9 min-w-0 text-sm"
                    {...register("quilometragem_troca", { required: "KM é obrigatório" })}
                  />
                  {errors.quilometragem_troca && <p className="mt-1 text-xs text-destructive">{errors.quilometragem_troca.message}</p>}
                </div>
                <div className="min-w-0">
                  <p className="mb-1 text-xs text-muted-foreground">Data *</p>
                  <Input
                    type="date"
                    max={new Date().toISOString().split("T")[0]}
                    className="h-9 min-w-0 text-sm"
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
                    {o.nome} ({o.marca}){o.tipo_oleo_transmissao ? ` — ${o.tipo_oleo_transmissao}` : ""} — R$ {Number(o.preco_litro).toFixed(2)}/L — Est: {Number(o.estoque_litros).toFixed(1)}L
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

            {/* Additional item rows (peças + filtros) */}
            {itensProdutos.map((item, index) => {
              const itemTotal = (Number(item.quantidade) || 0) * (Number(item.valor_unitario) || 0)
              return (
                <ItemRowAutocomplete
                  key={index}
                  index={index}
                  item={item}
                  itemTotal={itemTotal}
                  produtos={produtosBusca}
                  onSelect={(p) => selectProduto(index, p)}
                  onClear={() => clearItemProduto(index)}
                  onChangeQty={(v) => updateItemField(index, "quantidade", v)}
                  onChangePrice={(v) => updateItemField(index, "valor_unitario", v)}
                  onRemove={() => removeItem(index)}
                  R={R}
                />
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
                {taxaVal > 0 && (
                  <div className="flex justify-between text-xs text-red-500">
                    <span>Taxa ({Number(taxaPerc).toFixed(1)}%):</span>
                    <span>- R$ {R(taxaVal)}</span>
                  </div>
                )}
                <div className="border-t border-zinc-300 pt-2 dark:border-zinc-600">
                  <div className="flex justify-between text-base font-bold">
                    <span>VALOR TOTAL:</span>
                    <span>R$ {R(valorTotal)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ─── FORMA DE PAGAMENTO + TAXA ─── */}
          <div className="border-b-2 border-zinc-300 p-4 dark:border-zinc-600">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Forma de Pagamento
            </p>
            <div className="flex flex-wrap items-center gap-4">
              {FORMAS_PAGAMENTO.map((forma) => (
                <label key={forma} className="flex items-center gap-2 cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-zinc-300 accent-primary"
                    checked={formasPagamento.includes(forma)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormasPagamento((prev) => [...prev, forma])
                      } else {
                        setFormasPagamento((prev) => prev.filter((f) => f !== forma))
                      }
                    }}
                  />
                  {forma}
                </label>
              ))}
              <div className="ml-auto flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Taxa (%):</span>
                <Input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  placeholder="0"
                  className="h-8 w-20 text-right text-sm"
                  {...register("taxa_percentual")}
                />
              </div>
            </div>
          </div>

          {/* ─── PRÓXIMA TROCA ─── */}
          <div className="border-b-2 border-zinc-300 p-4 dark:border-zinc-600">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Próxima Troca
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="min-w-0">
                <p className="mb-1 text-xs text-muted-foreground">KM</p>
                <Input
                  type="number"
                  min="0"
                  placeholder="Ex: 150000"
                  className="h-9 min-w-0 text-sm"
                  {...register("proxima_troca_km")}
                />
              </div>
              <div className="min-w-0">
                <p className="mb-1 text-xs text-muted-foreground">Data</p>
                <Input
                  type="date"
                  className="h-9 min-w-0 text-sm"
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
            <Button type="button" variant="destructive" onClick={() => { clearDraft(); navigate("/trocas") }}>
              Cancelar
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}
