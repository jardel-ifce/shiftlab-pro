import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Retirada, RetiradaCreate, RetiradaListResponse, RetiradaUpdate } from "@/types/retirada"

const KEY = "retiradas"

export function useRetiradas(
  page: number = 1,
  filters?: { data_inicio?: string; data_fim?: string }
) {
  const skip = (page - 1) * 20
  return useQuery<RetiradaListResponse>({
    queryKey: [KEY, page, filters],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (filters?.data_inicio) params.data_inicio = filters.data_inicio
      if (filters?.data_fim) params.data_fim = filters.data_fim
      const { data } = await api.get<RetiradaListResponse>("/retiradas", { params })
      return data
    },
  })
}

export function useCreateRetirada() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RetiradaCreate) => {
      const { data } = await api.post<Retirada>("/retiradas", payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}

export function useUpdateRetirada() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: RetiradaUpdate }) => {
      const { data } = await api.patch<Retirada>(`/retiradas/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}

export function useDeleteRetirada() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/retiradas/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}
