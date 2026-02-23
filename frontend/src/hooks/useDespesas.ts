import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Despesa, DespesaCreate, DespesaListResponse, DespesaUpdate } from "@/types/despesa"

const KEY = "despesas"

export function useDespesas(
  page: number = 1,
  filters?: { data_inicio?: string; data_fim?: string; categoria?: string }
) {
  const skip = (page - 1) * 20
  return useQuery<DespesaListResponse>({
    queryKey: [KEY, page, filters],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (filters?.data_inicio) params.data_inicio = filters.data_inicio
      if (filters?.data_fim) params.data_fim = filters.data_fim
      if (filters?.categoria) params.categoria = filters.categoria
      const { data } = await api.get<DespesaListResponse>("/despesas", { params })
      return data
    },
  })
}

export function useDespesa(id: number | undefined) {
  return useQuery<Despesa>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Despesa>(`/despesas/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateDespesa() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: DespesaCreate) => {
      const { data } = await api.post<Despesa>("/despesas", payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}

export function useUpdateDespesa() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: DespesaUpdate }) => {
      const { data } = await api.patch<Despesa>(`/despesas/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}

export function useDeleteDespesa() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/despesas/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}
