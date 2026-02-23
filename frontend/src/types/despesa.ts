export interface Despesa {
  id: number
  data: string
  descricao: string
  valor: string
  categoria: string
  observacoes: string | null
  created_at: string
  updated_at: string
}

export interface DespesaCreate {
  data: string
  descricao: string
  valor: number
  categoria: string
  observacoes?: string | null
}

export interface DespesaUpdate {
  data?: string
  descricao?: string
  valor?: number
  categoria?: string
  observacoes?: string | null
}

export interface DespesaListResponse {
  items: Despesa[]
  total: number
  page: number
  pages: number
}
