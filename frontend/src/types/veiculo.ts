export interface Veiculo {
  id: number
  placa: string
  marca: string
  modelo: string
  ano: number
  tipo_cambio: string
  quilometragem_atual: number
  cor: string | null
  observacoes: string | null
  cliente_id: number
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface VeiculoCreate {
  placa: string
  marca: string
  modelo: string
  ano: number
  tipo_cambio: string
  quilometragem_atual?: number
  cor?: string | null
  observacoes?: string | null
  cliente_id: number
}

export interface VeiculoUpdate {
  marca?: string
  modelo?: string
  ano?: number
  tipo_cambio?: string
  quilometragem_atual?: number
  cor?: string | null
  observacoes?: string | null
  cliente_id?: number
}

export interface VeiculoListResponse {
  items: Veiculo[]
  total: number
  page: number
  pages: number
}

export const TIPOS_CAMBIO = [
  { value: "manual", label: "Manual" },
  { value: "automatico", label: "Automático" },
  { value: "cvt", label: "CVT" },
  { value: "automatizado", label: "Automatizado" },
  { value: "dupla_embreagem", label: "Dupla Embreagem" },
  { value: "outro", label: "Outro" },
] as const
