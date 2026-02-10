export interface Montadora {
  id: number
  nome: string
  pais_origem: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface MontadoraListResponse {
  items: Montadora[]
  total: number
}

export interface ModeloReferencia {
  id: number
  montadora_id: number
  nome: string
  descricao: string
  tipo_cambio: string | null
  ano_inicio: number | null
  ano_fim: number | null
  motor: string | null
  observacoes: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface ModeloReferenciaListResponse {
  items: ModeloReferencia[]
  total: number
}

// FIPE types
export interface FipeMarca {
  code: string
  name: string
}

export interface FipeModelo {
  code: string
  name: string
}

export interface FipeAno {
  code: string
  name: string
}
