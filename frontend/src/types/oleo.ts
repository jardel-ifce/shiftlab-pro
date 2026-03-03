export interface Oleo {
  id: number
  codigo_produto: string | null
  nome: string
  marca: string
  volume_liquido: string | null
  tipo_oleo_transmissao: string | null
  codigo_oem: string | null
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
  volume_liquido?: string | null
  tipo_oleo_transmissao?: string | null
  codigo_oem?: string | null
  custo_litro?: number
  preco_litro?: number
  estoque_litros?: number
  estoque_minimo?: number
  observacoes?: string | null
}

export interface OleoUpdate {
  nome?: string
  marca?: string
  volume_liquido?: string | null
  tipo_oleo_transmissao?: string | null
  codigo_oem?: string | null
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

