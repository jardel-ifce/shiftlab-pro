export interface Oleo {
  id: number
  nome: string
  marca: string
  modelo: string | null
  tipo_veiculo: string | null
  viscosidade: string | null
  volume_unidade: string | null
  volume_liquido: string | null
  formato_venda: string | null
  tipo_recipiente: string | null
  tipo_oleo_transmissao: string | null
  desempenho: string | null
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
  modelo?: string | null
  tipo_veiculo?: string | null
  viscosidade?: string | null
  volume_unidade?: string | null
  volume_liquido?: string | null
  formato_venda?: string | null
  tipo_recipiente?: string | null
  tipo_oleo_transmissao?: string | null
  desempenho?: string | null
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
  modelo?: string | null
  tipo_veiculo?: string | null
  viscosidade?: string | null
  volume_unidade?: string | null
  volume_liquido?: string | null
  formato_venda?: string | null
  tipo_recipiente?: string | null
  tipo_oleo_transmissao?: string | null
  desempenho?: string | null
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

export const TIPOS_VEICULO = [
  "Carro",
  "Caminhonete",
  "Carro/Caminhonete",
  "Moto",
  "Caminhão",
  "Van",
] as const

export const FORMATOS_VENDA = [
  "Unidade",
  "Caixa",
  "Galão",
  "Balde",
  "Kit",
] as const

export const TIPOS_RECIPIENTE = [
  "Garrafa plástica",
  "Lata",
  "Balde",
  "Tambor",
  "Galão",
] as const
