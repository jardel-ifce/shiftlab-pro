export interface FotoFiltro {
  id: number
  filtro_id: number
  url: string
  ordem: number
  created_at: string
}

export interface Filtro {
  id: number
  codigo_produto: string | null
  nome: string
  marca: string
  codigo_oem: string | null
  custo_unitario: string
  preco_unitario: string
  estoque: number
  estoque_minimo: number
  observacoes: string | null
  foto_url: string | null
  fotos: FotoFiltro[]
  ativo: boolean
  estoque_baixo: boolean
  margem_lucro: string
  lucro_unitario: string
  created_at: string
  updated_at: string
}

export interface FiltroCreate {
  codigo_produto?: string | null
  nome: string
  marca: string
  codigo_oem?: string | null
  custo_unitario?: number
  preco_unitario?: number
  estoque?: number
  estoque_minimo?: number
  observacoes?: string | null
}

export interface FiltroUpdate {
  codigo_produto?: string | null
  nome?: string
  marca?: string
  codigo_oem?: string | null
  custo_unitario?: number
  preco_unitario?: number
  estoque?: number
  estoque_minimo?: number
  ativo?: boolean
  observacoes?: string | null
}

export interface FiltroListResponse {
  items: Filtro[]
  total: number
  page: number
  pages: number
}
