export interface Peca {
  id: number
  nome: string
  marca: string | null
  unidade: string
  preco_custo: string
  preco_venda: string
  estoque: string
  estoque_minimo: string
  comentarios: string | null
  observacoes: string | null
  ativo: boolean
  estoque_baixo: boolean
  margem_lucro: string
  created_at: string
  updated_at: string
}

export interface PecaCreate {
  nome: string
  marca?: string | null
  unidade?: string
  preco_custo?: number
  preco_venda?: number
  estoque?: number
  estoque_minimo?: number
  comentarios?: string | null
  observacoes?: string | null
}

export interface PecaUpdate {
  nome?: string
  marca?: string | null
  unidade?: string
  preco_custo?: number
  preco_venda?: number
  estoque?: number
  estoque_minimo?: number
  ativo?: boolean
  comentarios?: string | null
  observacoes?: string | null
}

export interface PecaListResponse {
  items: Peca[]
  total: number
  page: number
  pages: number
}
