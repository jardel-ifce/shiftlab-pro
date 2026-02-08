import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Servico, ServicoCreate, ServicoListResponse, ServicoUpdate } from "@/types/servico"

const KEY = "servicos"

export function useServicos(page: number = 1, search?: string) {
  const skip = (page - 1) * 20
  return useQuery<ServicoListResponse>({
    queryKey: [KEY, page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (search) params.search = search
      const { data } = await api.get<ServicoListResponse>("/servicos", { params })
      return data
    },
  })
}

export function useServico(id: number | undefined) {
  return useQuery<Servico>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Servico>(`/servicos/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useAllServicos() {
  return useQuery<ServicoListResponse>({
    queryKey: [KEY, "all"],
    queryFn: async () => {
      const { data } = await api.get<ServicoListResponse>("/servicos", { params: { limit: 100 } })
      return data
    },
  })
}

export function useCreateServico() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ServicoCreate) => {
      const { data } = await api.post<Servico>("/servicos", payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUpdateServico() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: ServicoUpdate }) => {
      const { data } = await api.patch<Servico>(`/servicos/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteServico() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/servicos/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}
