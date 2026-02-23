import { useQuery } from "@tanstack/react-query"
import api from "@/lib/api"
import type { FinanceiroListResponse, ProdutoFinanceiroListResponse } from "@/types/financeiro"

const KEY = "financeiro"

export function useFinanceiro(
  page: number = 1,
  filters?: { cliente_id?: number; data_inicio?: string; data_fim?: string },
) {
  const skip = (page - 1) * 20
  return useQuery<FinanceiroListResponse>({
    queryKey: [KEY, page, filters],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (filters?.cliente_id) params.cliente_id = filters.cliente_id
      if (filters?.data_inicio) params.data_inicio = filters.data_inicio
      if (filters?.data_fim) params.data_fim = filters.data_fim
      const { data } = await api.get<FinanceiroListResponse>("/financeiro", { params })
      return data
    },
  })
}

export function useFinanceiroProdutos(tipo?: string) {
  return useQuery<ProdutoFinanceiroListResponse>({
    queryKey: [KEY, "produtos", tipo],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (tipo) params.tipo = tipo
      const { data } = await api.get<ProdutoFinanceiroListResponse>("/financeiro/produtos", { params })
      return data
    },
  })
}
