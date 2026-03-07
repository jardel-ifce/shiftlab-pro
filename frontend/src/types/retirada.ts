export interface Retirada {
  id: number
  data: string
  valor: string
  descricao: string
  observacoes: string | null
  created_at: string
  updated_at: string
}

export interface RetiradaCreate {
  data: string
  valor: number
  descricao: string
  observacoes?: string
}

export interface RetiradaUpdate {
  data?: string
  valor?: number
  descricao?: string
  observacoes?: string
}

export interface RetiradaListResponse {
  items: Retirada[]
  total: number
  page: number
  pages: number
}
