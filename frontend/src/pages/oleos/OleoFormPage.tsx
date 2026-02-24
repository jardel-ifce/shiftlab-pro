import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { ArrowLeft, ImagePlus, Loader2, Trash2 } from "lucide-react"
import {
  useOleo,
  useCreateOleo,
  useUpdateOleo,
  useUploadFotoOleo,
  useDeleteFotoOleo,
} from "@/hooks/useOleos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  formatMoeda,
  formatDecimal,
  parseMoeda,
  parseDecimal,
  numberToMoeda,
  numberToDecimal,
} from "@/lib/masks"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001"
const BASE_URL = API_URL.replace(/\/api\/v1\/?$/, "")

interface FormData {
  codigo_produto: string
  nome: string
  marca: string
  volume_liquido: string
  tipo_oleo_transmissao: string
  codigo_oem: string
  observacoes: string
}

export function OleoFormPage() {
  const { id } = useParams()
  const isEditing = !!id
  const navigate = useNavigate()

  const { data: oleo, isLoading } = useOleo(isEditing ? Number(id) : undefined)
  const createMutation = useCreateOleo()
  const updateMutation = useUpdateOleo()
  const uploadFotoMutation = useUploadFotoOleo()
  const deleteFotoMutation = useDeleteFotoOleo()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  // Foto state
  const [fotoFile, setFotoFile] = useState<File | null>(null)
  const [fotoPreview, setFotoPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Masked fields state
  const [precoLitro, setPrecoLitro] = useState("")
  const [estoqueLitros, setEstoqueLitros] = useState("")
  const [estoqueMinimo, setEstoqueMinimo] = useState("")

  useEffect(() => {
    if (oleo) {
      reset({
        codigo_produto: oleo.codigo_produto || "",
        nome: oleo.nome,
        marca: oleo.marca,
        volume_liquido: oleo.volume_liquido || "",
        tipo_oleo_transmissao: oleo.tipo_oleo_transmissao || "",
        codigo_oem: oleo.codigo_oem || "",
        observacoes: oleo.observacoes || "",
      })
      setPrecoLitro(numberToMoeda(oleo.preco_litro))
      setEstoqueLitros(numberToDecimal(oleo.estoque_litros))
      setEstoqueMinimo(numberToDecimal(oleo.estoque_minimo))
    }
  }, [oleo, reset])

  // Cleanup preview URL on unmount
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
    if (!isEditing || !oleo?.foto_url) return
    try {
      await deleteFotoMutation.mutateAsync(Number(id))
      toast.success("Foto removida!")
    } catch {
      toast.error("Erro ao remover foto.")
    }
  }

  async function onSubmit(formData: FormData) {
    const precoValue = parseMoeda(precoLitro)
    if (!precoValue) {
      toast.error("Informe o preço de venda por litro.")
      return
    }

    try {
      const payload = {
        codigo_produto: formData.codigo_produto || null,
        nome: formData.nome,
        marca: formData.marca,
        volume_liquido: formData.volume_liquido || null,
        tipo_oleo_transmissao: formData.tipo_oleo_transmissao || null,
        codigo_oem: formData.codigo_oem || null,
        preco_litro: precoValue,
        estoque_minimo: parseDecimal(estoqueMinimo) || 5,
        observacoes: formData.observacoes || null,
      }

      let oleoId: number

      if (isEditing) {
        const editPayload = { ...payload, estoque_litros: parseDecimal(estoqueLitros) || 0 }
        await updateMutation.mutateAsync({ id: Number(id), payload: editPayload })
        oleoId = Number(id)
        toast.success("Óleo atualizado com sucesso!")
      } else {
        const created = await createMutation.mutateAsync(payload)
        oleoId = created.id
        toast.success("Óleo cadastrado com sucesso!")
      }

      // Upload foto se selecionada
      if (fotoFile) {
        try {
          await uploadFotoMutation.mutateAsync({ id: oleoId, file: fotoFile })
        } catch {
          toast.error("Óleo salvo, mas erro ao enviar foto.")
        }
      }

      navigate("/oleos")
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(detail || "Erro ao salvar óleo.")
    }
  }

  if (isEditing && isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card><CardContent className="space-y-4 pt-6">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
        </CardContent></Card>
      </div>
    )
  }

  const isPending = createMutation.isPending || updateMutation.isPending || uploadFotoMutation.isPending
  const fotoAtual = oleo?.foto_url ? `${BASE_URL}${oleo.foto_url}` : null

  return (
    <div className="mx-auto max-w-3xl space-y-6">
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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Card 1: Identificação do Produto */}
        <Card>
          <CardHeader><CardTitle>Identificação do Produto</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {/* Seção de Foto */}
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
                <Input id="codigo_produto" placeholder="5508, 1760..." {...register("codigo_produto")} />
              </div>

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
                <Label htmlFor="tipo_oleo_transmissao">Tipo de Óleo de Transmissão</Label>
                <Input id="tipo_oleo_transmissao" placeholder="ATF Dexron VI, CVT NS-3..." {...register("tipo_oleo_transmissao")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="volume_liquido">Volume Líquido</Label>
                <Input id="volume_liquido" placeholder="1 L..." {...register("volume_liquido")} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="codigo_oem">Código OEM</Label>
                <Input id="codigo_oem" placeholder="GM, Toyota..." {...register("codigo_oem")} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Card 2: Preço e Controle */}
        <Card>
          <CardHeader><CardTitle>Preço e Controle</CardTitle></CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="preco_litro">Preço Venda/Litro (R$) *</Label>
                <Input
                  id="preco_litro"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={precoLitro}
                  onChange={(e) => setPrecoLitro(formatMoeda(e.target.value))}
                />
              </div>

              {isEditing && (
                <div className="space-y-2">
                  <Label htmlFor="estoque_litros">Estoque Atual (L)</Label>
                  <Input
                    id="estoque_litros"
                    type="text"
                    inputMode="decimal"
                    placeholder="0,00"
                    value={estoqueLitros}
                    onChange={(e) => setEstoqueLitros(formatDecimal(e.target.value))}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="estoque_minimo">Estoque Mínimo (L)</Label>
                <Input
                  id="estoque_minimo"
                  type="text"
                  inputMode="decimal"
                  placeholder="5,0"
                  value={estoqueMinimo}
                  onChange={(e) => setEstoqueMinimo(formatDecimal(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Card 4: Observações */}
        <Card>
          <CardHeader><CardTitle>Observações</CardTitle></CardHeader>
          <CardContent>
            <textarea
              id="observacoes"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Observações sobre o produto..."
              {...register("observacoes")}
            />
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={isPending}>
            {isPending ? "Salvando..." : isEditing ? "Atualizar" : "Cadastrar"}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate("/oleos")}>Cancelar</Button>
        </div>
      </form>
    </div>
  )
}
