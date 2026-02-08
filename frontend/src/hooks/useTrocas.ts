import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type {
  TrocaOleo,
  TrocaOleoCreate,
  TrocaOleoDetail,
  TrocaOleoListResponse,
  TrocaOleoUpdate,
} from "@/types/troca"

const KEY = "trocas"

export function useTrocas(
  page: number = 1,
  filters?: { veiculo_id?: number; cliente_id?: number; data_inicio?: string; data_fim?: string }
) {
  const skip = (page - 1) * 20
  return useQuery<TrocaOleoListResponse>({
    queryKey: [KEY, page, filters],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (filters?.veiculo_id) params.veiculo_id = filters.veiculo_id
      if (filters?.cliente_id) params.cliente_id = filters.cliente_id
      if (filters?.data_inicio) params.data_inicio = filters.data_inicio
      if (filters?.data_fim) params.data_fim = filters.data_fim
      const { data } = await api.get<TrocaOleoListResponse>("/trocas", { params })
      return data
    },
  })
}

export function useTroca(id: number | undefined) {
  return useQuery<TrocaOleoDetail>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<TrocaOleoDetail>(`/trocas/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateTroca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TrocaOleoCreate) => {
      const { data } = await api.post<TrocaOleo>("/trocas", payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["oleos"] })
      qc.invalidateQueries({ queryKey: ["veiculos"] })
      qc.invalidateQueries({ queryKey: ["pecas"] })
    },
  })
}

export function useUpdateTroca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: TrocaOleoUpdate }) => {
      const { data } = await api.patch<TrocaOleo>(`/trocas/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["oleos"] })
      qc.invalidateQueries({ queryKey: ["pecas"] })
    },
  })
}

export function useDeleteTroca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/trocas/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["oleos"] })
      qc.invalidateQueries({ queryKey: ["pecas"] })
    },
  })
}
