export interface Cliente {
  id: number
  nome: string
  telefone: string
  email: string | null
  cpf_cnpj: string
  endereco: string | null
  observacoes: string | null
  created_at: string
  updated_at: string
}

export interface ClienteCreate {
  nome: string
  telefone: string
  email?: string | null
  cpf_cnpj: string
  endereco?: string | null
  observacoes?: string | null
}

export interface ClienteUpdate {
  nome?: string
  telefone?: string
  email?: string | null
  endereco?: string | null
  observacoes?: string | null
}

export interface ClienteListResponse {
  items: Cliente[]
  total: number
  page: number
  pages: number
}
