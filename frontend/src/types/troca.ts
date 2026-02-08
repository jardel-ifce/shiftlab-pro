import type { Veiculo } from "./veiculo"
import type { Oleo } from "./oleo"

export interface ItemTroca {
  id: number
  peca_id: number
  quantidade: string
  valor_unitario: string
  valor_total: string
  peca?: {
    id: number
    nome: string
    marca: string | null
    unidade: string
    preco_venda: string
    estoque: string
  }
  created_at: string
}

export interface ItemTrocaCreate {
  peca_id: number
  quantidade: number
  valor_unitario: number
}

export interface TrocaOleo {
  id: number
  data_troca: string
  quilometragem_troca: number
  quantidade_litros: string
  valor_oleo: string
  valor_servico: string
  desconto_percentual: string
  desconto_valor: string
  motivo_desconto: string | null
  proxima_troca_km: number | null
  proxima_troca_data: string | null
  observacoes: string | null
  veiculo_id: number
  oleo_id: number
  user_id: number | null
  valor_total: string
  itens: ItemTroca[]
  created_at: string
  updated_at: string
}

export interface TrocaOleoDetail extends TrocaOleo {
  veiculo: Veiculo
  oleo: Oleo
  valor_sugerido_oleo: string
  economia_cliente: string
}

export interface TrocaOleoCreate {
  data_troca: string
  quilometragem_troca: number
  quantidade_litros: number
  veiculo_id: number
  oleo_id: number
  valor_oleo?: number
  valor_servico?: number
  desconto_percentual?: number
  desconto_valor?: number
  motivo_desconto?: string | null
  proxima_troca_km?: number | null
  proxima_troca_data?: string | null
  observacoes?: string | null
  itens?: ItemTrocaCreate[]
}

export interface TrocaOleoUpdate {
  data_troca?: string
  quilometragem_troca?: number
  quantidade_litros?: number
  oleo_id?: number
  valor_oleo?: number
  valor_servico?: number
  desconto_percentual?: number
  desconto_valor?: number
  motivo_desconto?: string | null
  proxima_troca_km?: number | null
  proxima_troca_data?: string | null
  observacoes?: string | null
  itens?: ItemTrocaCreate[]
}

export interface TrocaOleoListResponse {
  items: TrocaOleo[]
  total: number
  page: number
  pages: number
}

export interface ProximaTroca {
  veiculo_id: number
  placa: string
  modelo: string
  cliente_nome: string
  ultima_troca: string
  proxima_troca_km: number | null
  proxima_troca_data: string | null
  km_atual: number
  dias_restantes: number | null
  km_restantes: number | null
  urgente: boolean
}
