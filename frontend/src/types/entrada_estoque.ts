export interface EntradaEstoque {
  id: number
  tipo_produto: string
  produto_id: number
  produto_nome: string
  produto_marca: string
  quantidade_litros: string
  custo_unitario: string
  custo_total: string
  fornecedor: string | null
  nota_fiscal: string | null
  data_compra: string
  observacoes: string | null
  created_at: string
  updated_at: string
}

export interface EntradaEstoqueCreate {
  tipo_produto: string
  produto_id: number
  quantidade_litros: number
  custo_unitario: number
  fornecedor?: string | null
  nota_fiscal?: string | null
  data_compra: string
  observacoes?: string | null
}

export interface EntradaEstoqueListResponse {
  items: EntradaEstoque[]
  total: number
  page: number
  pages: number
}

export interface ProdutoBusca {
  tipo: string
  id: number
  codigo_produto: string | null
  nome: string
  marca: string
  label: string
}
