export interface ItemTrocaFinanceiro {
  id: number
  peca_nome: string | null
  quantidade: string
  valor_unitario: string
  valor_total: string
  custo_unitario: string
  lucro_item: string
}

export interface TrocaFinanceiro {
  id: number
  data_troca: string
  cliente_nome: string | null
  veiculo_info: string | null
  oleo_nome: string | null
  valor_oleo: string
  valor_servico: string
  valor_total: string
  desconto_percentual: string
  desconto_valor: string
  custo_oleo: string
  custo_pecas: string
  custo_total: string
  lucro_bruto: string
  margem_lucro: string
  itens: ItemTrocaFinanceiro[]
}

export interface FinanceiroResumo {
  total_trocas: number
  faturamento_total: number
  custo_total: number
  lucro_bruto_total: number
  margem_media: number
  ticket_medio: number
  imposto_percentual: number
  imposto_valor: number
  despesas_total: number
  lucro_liquido: number
  investimento_total: number
}

export interface FinanceiroListResponse {
  items: TrocaFinanceiro[]
  resumo: FinanceiroResumo
  total: number
  page: number
  pages: number
}

export interface ProdutoFinanceiro {
  tipo: string
  id: number
  nome: string
  marca: string | null
  custo: number
  preco_venda: number
  lucro_unitario: number
  margem_lucro: number
  estoque: number
}

export interface ProdutoFinanceiroListResponse {
  items: ProdutoFinanceiro[]
}
