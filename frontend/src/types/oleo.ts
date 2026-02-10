export interface Oleo {
  id: number
  nome: string
  marca: string
  tipo: string
  viscosidade: string | null
  especificacao: string | null
  custo_litro: string
  preco_litro: string
  estoque_litros: string
  estoque_minimo: string
  observacoes: string | null
  foto_url: string | null
  ativo: boolean
  estoque_baixo: boolean
  margem_lucro: string
  lucro_por_litro: string
  created_at: string
  updated_at: string
}

export interface OleoCreate {
  nome: string
  marca: string
  tipo?: string
  viscosidade?: string | null
  especificacao?: string | null
  custo_litro?: number
  preco_litro?: number
  estoque_litros?: number
  estoque_minimo?: number
  observacoes?: string | null
}

export interface OleoUpdate {
  nome?: string
  marca?: string
  tipo?: string
  viscosidade?: string | null
  especificacao?: string | null
  custo_litro?: number
  preco_litro?: number
  estoque_litros?: number
  estoque_minimo?: number
  ativo?: boolean
  observacoes?: string | null
}

export interface OleoListResponse {
  items: Oleo[]
  total: number
  page: number
  pages: number
}

export const TIPOS_OLEO = [
  { value: "atf", label: "ATF" },
  { value: "cvt", label: "CVT" },
  { value: "manual", label: "Manual" },
  { value: "dct", label: "Dupla Embreagem (DCT)" },
  { value: "universal", label: "Universal" },
] as const
