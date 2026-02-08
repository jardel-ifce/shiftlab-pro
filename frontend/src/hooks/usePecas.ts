import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Peca, PecaCreate, PecaListResponse, PecaUpdate } from "@/types/peca"

const KEY = "pecas"

export function usePecas(page: number = 1, search?: string) {
  const skip = (page - 1) * 20
  return useQuery<PecaListResponse>({
    queryKey: [KEY, page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (search) params.search = search
      const { data } = await api.get<PecaListResponse>("/pecas", { params })
      return data
    },
  })
}

export function usePeca(id: number | undefined) {
  return useQuery<Peca>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Peca>(`/pecas/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useAllPecas() {
  return useQuery<PecaListResponse>({
    queryKey: [KEY, "all"],
    queryFn: async () => {
      const { data } = await api.get<PecaListResponse>("/pecas", { params: { limit: 100 } })
      return data
    },
  })
}

export function useCreatePeca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PecaCreate) => {
      const { data } = await api.post<Peca>("/pecas", payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUpdatePeca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: PecaUpdate }) => {
      const { data } = await api.patch<Peca>(`/pecas/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeletePeca() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/pecas/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}
