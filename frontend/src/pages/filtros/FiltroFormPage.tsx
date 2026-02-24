import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft, ImagePlus, Loader2, Trash2 } from "lucide-react"
import {
  useFiltro,
  useCreateFiltro,
  useUpdateFiltro,
  useUploadFotoFiltro,
  useDeleteFotoFiltro,
} from "@/hooks/useFiltros"
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

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"
const BASE_URL = API_URL.replace(/\/api\/v1\/?$/, "")

interface FormData {
  codigo_produto: string
  nome: string
  marca: string
  codigo_oem: string
  observacoes: string
}

export function FiltroFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: filtro, isLoading } = useFiltro(isEditing ? Number(id) : undefined)
  const createMutation = useCreateFiltro()
  const updateMutation = useUpdateFiltro()
  const uploadFotoMutation = useUploadFotoFiltro()
  const deleteFotoMutation = useDeleteFotoFiltro()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  const [fotoFile, setFotoFile] = useState<File | null>(null)
  const [fotoPreview, setFotoPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [precoUnitario, setPrecoUnitario] = useState("")
  const [estoqueAtual, setEstoqueAtual] = useState("")
  const [estoqueMinimo, setEstoqueMinimo] = useState("2")

  useEffect(() => {
    if (filtro) {
      reset({
        codigo_produto: filtro.codigo_produto || "",
        nome: filtro.nome,
        marca: filtro.marca,
        codigo_oem: filtro.codigo_oem || "",
        observacoes: filtro.observacoes || "",
      })
      setPrecoUnitario(numberToMoeda(filtro.preco_unitario))
      setEstoqueAtual(String(filtro.estoque))
      setEstoqueMinimo(String(filtro.estoque_minimo))
    }
  }, [filtro, reset])

  useEffect(() => {
    return () => {
      if (fotoPreview) URL.revokeObjectURL(fotoPreview)
    }
  }, [fotoPreview])

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      toast.error("Formato inválido. Use JPG ou PNG.")
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Arquivo muito grande. Máximo: 10MB.")
      return
    }
    if (fotoPreview) URL.revokeObjectURL(fotoPreview)
    setFotoFile(file)
    setFotoPreview(URL.createObjectURL(file))
  }

  function handleRemovePreview() {
    if (fotoPreview) URL.revokeObjectURL(fotoPreview)
    setFotoFile(null)
    setFotoPreview(null)
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  async function handleDeleteFoto() {
    if (!isEditing || !filtro?.foto_url) return
    try {
      await deleteFotoMutation.mutateAsync(Number(id))
      toast.success("Foto removida!")
    } catch {
      toast.error("Erro ao remover foto.")
    }
  }

  async function onSubmit(formData: FormData) {
    const precoValue = parseMoeda(precoUnitario)
    if (!precoValue) {
      toast.error("Informe o preço de venda unitário.")
      return
    }

    try {
      const payload = {
        codigo_produto: formData.codigo_produto || null,
        nome: formData.nome,
        marca: formData.marca,
        codigo_oem: formData.codigo_oem || null,
        preco_unitario: precoValue,
        estoque_minimo: Number(estoqueMinimo) || 2,
        observacoes: formData.observacoes || null,
      }

      let filtroId: number

      if (isEditing) {
        const editPayload = { ...payload, estoque: Number(estoqueAtual) || 0 }
        await updateMutation.mutateAsync({ id: Number(id), payload: editPayload })
        filtroId = Number(id)
        toast.success("Filtro atualizado com sucesso!")
      } else {
        const created = await createMutation.mutateAsync(payload)
        filtroId = created.id
        toast.success("Filtro cadastrado com sucesso!")
      }

      if (fotoFile) {
        try {
          await uploadFotoMutation.mutateAsync({ id: filtroId, file: fotoFile })
        } catch {
          toast.error("Filtro salvo, mas erro ao enviar foto.")
        }
      }

      navigate("/filtros")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar filtro.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card><CardContent className="space-y-4 pt-6">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
        </CardContent></Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending || uploadFotoMutation.isPending
  const fotoAtual = filtro?.foto_url ? `${BASE_URL}${filtro.foto_url}` : null

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/filtros")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? "Editar Filtro" : "Novo Filtro"}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? "Atualize os dados do filtro." : "Cadastre um novo filtro de óleo."}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Identificação do Produto</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {/* Foto */}
            <div className="space-y-3">
              <Label>Foto do Produto</Label>
              <div className="flex items-start gap-4">
                <div className="relative flex h-32 w-32 shrink-0 items-center justify-center overflow-hidden rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/50">
                  {fotoPreview ? (
                    <>
                      <img src={fotoPreview} alt="Preview" className="h-full w-full object-cover" />
                      <button
                        type="button"
                        onClick={handleRemovePreview}
                        className="absolute -right-1 -top-1 rounded-full bg-destructive p-1 text-destructive-foreground shadow-sm hover:bg-destructive/90"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </>
                  ) : fotoAtual && !fotoFile ? (
                    <>
                      <img src={fotoAtual} alt="Foto atual" className="h-full w-full object-cover" />
                      <button
                        type="button"
                        onClick={handleDeleteFoto}
                        disabled={deleteFotoMutation.isPending}
                        className="absolute -right-1 -top-1 rounded-full bg-destructive p-1 text-destructive-foreground shadow-sm hover:bg-destructive/90"
                      >
                        {deleteFotoMutation.isPending ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Trash2 className="h-3 w-3" />
                        )}
                      </button>
                    </>
                  ) : (
                    <ImagePlus className="h-8 w-8 text-muted-foreground/50" />
                  )}
                </div>
                <div className="space-y-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <ImagePlus className="mr-2 h-4 w-4" />
                    Escolher Imagem
                  </Button>
                  <p className="text-xs text-muted-foreground">JPG ou PNG, máx. 10MB</p>
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="codigo_produto">Código do Produto</Label>
                <Input id="codigo_produto" placeholder="6209, 6210..." {...register("codigo_produto")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="nome">Modelo do Filtro *</Label>
                <Input id="nome" placeholder="WFC960, WFC995..." {...register("nome", { required: "Nome é obrigatório", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.nome && <p className="text-xs text-destructive">{errors.nome.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input id="marca" placeholder="Wega, Mann, Fram..." {...register("marca", { required: "Marca é obrigatória", minLength: { value: 2, message: "Mínimo 2 caracteres" } })} />
                {errors.marca && <p className="text-xs text-destructive">{errors.marca.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="codigo_oem">Código OEM / Referência</Label>
                <Input id="codigo_oem" placeholder="OC.1604202, QC.160420..." {...register("codigo_oem")} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Preço e Controle</CardTitle></CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="preco_unitario">Preço Venda (R$) *</Label>
                <Input
                  id="preco_unitario"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={precoUnitario}
                  onChange={(e) => setPrecoUnitario(formatMoeda(e.target.value))}
                />
              </div>

              {isEditing && (
                <div className="space-y-2">
                  <Label htmlFor="estoque_atual">Estoque Atual (un.)</Label>
                  <Input
                    id="estoque_atual"
                    type="number"
                    inputMode="numeric"
                    min="0"
                    placeholder="0"
                    value={estoqueAtual}
                    onChange={(e) => setEstoqueAtual(e.target.value.replace(/\D/g, ""))}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="estoque_minimo">Estoque Mínimo (un.)</Label>
                <Input
                  id="estoque_minimo"
                  type="number"
                  inputMode="numeric"
                  min="0"
                  placeholder="2"
                  value={estoqueMinimo}
                  onChange={(e) => setEstoqueMinimo(e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Observações</CardTitle></CardHeader>
          <CardContent>
            <textarea
              id="observacoes"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Observações sobre o filtro..."
              {...register("observacoes")}
            />
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={isPending}>
            {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate("/filtros")}>Cancelar</Button>
        </div>
      </form>
    </div>
  )
}
