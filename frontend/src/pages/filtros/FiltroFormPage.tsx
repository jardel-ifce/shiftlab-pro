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

const MAX_FOTOS = 5

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

  // Fotos: novas (ainda não enviadas)
  const [newFiles, setNewFiles] = useState<File[]>([])
  const [newPreviews, setNewPreviews] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [precoUnitario, setPrecoUnitario] = useState("")
  const [estoqueAtual, setEstoqueAtual] = useState("")
  const [estoqueMinimo, setEstoqueMinimo] = useState("2")

  const existingFotos = filtro?.fotos ?? []
  const totalFotos = existingFotos.length + newFiles.length
  const canAddMore = totalFotos < MAX_FOTOS

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

  // Cleanup preview URLs on unmount
  useEffect(() => {
    return () => {
      newPreviews.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [newPreviews])

  function handleFilesSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files || [])
    if (!files.length) return

    const remaining = MAX_FOTOS - totalFotos
    if (remaining <= 0) {
      toast.error(`Máximo de ${MAX_FOTOS} fotos por filtro.`)
      return
    }

    const validFiles: File[] = []
    const previews: string[] = []

    for (const file of files.slice(0, remaining)) {
      if (!["image/jpeg", "image/png"].includes(file.type)) {
        toast.error(`"${file.name}": formato inválido. Use JPG ou PNG.`)
        continue
      }
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`"${file.name}": muito grande. Máximo: 10MB.`)
        continue
      }
      validFiles.push(file)
      previews.push(URL.createObjectURL(file))
    }

    if (validFiles.length) {
      setNewFiles((prev) => [...prev, ...validFiles])
      setNewPreviews((prev) => [...prev, ...previews])
    }

    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  function handleRemoveNewFile(index: number) {
    URL.revokeObjectURL(newPreviews[index])
    setNewFiles((prev) => prev.filter((_, i) => i !== index))
    setNewPreviews((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleDeleteExistingFoto(fotoId: number) {
    if (!isEditing) return
    try {
      await deleteFotoMutation.mutateAsync({ filtroId: Number(id), fotoId })
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

      // Upload de novas fotos
      if (newFiles.length > 0) {
        let erros = 0
        for (const file of newFiles) {
          try {
            await uploadFotoMutation.mutateAsync({ id: filtroId, file })
          } catch {
            erros++
          }
        }
        if (erros > 0) {
          toast.error(`Filtro salvo, mas ${erros} foto(s) falharam no envio.`)
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
            {/* Fotos */}
            <div className="space-y-3">
              <Label>Fotos do Produto ({totalFotos}/{MAX_FOTOS})</Label>
              <div className="flex flex-wrap gap-3">
                {/* Fotos existentes (servidor) */}
                {existingFotos.map((foto) => (
                  <div
                    key={foto.id}
                    className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border bg-muted/50"
                  >
                    <img
                      src={`${BASE_URL}${foto.url}`}
                      alt={`Foto ${foto.ordem + 1}`}
                      className="h-full w-full object-cover"
                    />
                    <button
                      type="button"
                      onClick={() => handleDeleteExistingFoto(foto.id)}
                      disabled={deleteFotoMutation.isPending}
                      className="absolute -right-1 -top-1 rounded-full bg-destructive p-1 text-destructive-foreground shadow-sm hover:bg-destructive/90"
                    >
                      {deleteFotoMutation.isPending ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Trash2 className="h-3 w-3" />
                      )}
                    </button>
                  </div>
                ))}

                {/* Previews de novas fotos */}
                {newPreviews.map((preview, i) => (
                  <div
                    key={`new-${i}`}
                    className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-dashed border-primary bg-muted/50"
                  >
                    <img src={preview} alt={`Nova ${i + 1}`} className="h-full w-full object-cover" />
                    <button
                      type="button"
                      onClick={() => handleRemoveNewFile(i)}
                      className="absolute -right-1 -top-1 rounded-full bg-destructive p-1 text-destructive-foreground shadow-sm hover:bg-destructive/90"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}

                {/* Botão adicionar */}
                {canAddMore && (
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex h-24 w-24 shrink-0 items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/50 hover:border-muted-foreground/50 hover:bg-muted transition-colors"
                  >
                    <ImagePlus className="h-6 w-6 text-muted-foreground/50" />
                  </button>
                )}
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png"
                multiple
                onChange={handleFilesSelect}
                className="hidden"
              />
              <p className="text-xs text-muted-foreground">JPG ou PNG, máx. 10MB cada. Até {MAX_FOTOS} fotos.</p>
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
