export interface Servico {
  id: number
  nome: string
  descricao: string | null
  preco: string
  ativo: boolean
  observacoes: string | null
  created_at: string
  updated_at: string
}

export interface ServicoCreate {
  nome: string
  descricao?: string | null
  preco?: number
  observacoes?: string | null
}

export interface ServicoUpdate {
  nome?: string
  descricao?: string | null
  preco?: number
  ativo?: boolean
  observacoes?: string | null
}

export interface ServicoListResponse {
  items: Servico[]
  total: number
  page: number
  pages: number
}
