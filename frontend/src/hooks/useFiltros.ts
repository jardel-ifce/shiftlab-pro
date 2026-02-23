import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Filtro, FiltroCreate, FiltroListResponse, FiltroUpdate } from "@/types/filtro"

const KEY = "filtros"

export function useFiltros(page: number = 1, search?: string) {
  const skip = (page - 1) * 20
  return useQuery<FiltroListResponse>({
    queryKey: [KEY, page, search],
    queryFn: async () => {
      const params: Record<string, string | number | boolean> = { skip, limit: 20 }
      if (search) params.search = search
      const { data } = await api.get<FiltroListResponse>("/filtros", { params })
      return data
    },
  })
}

export function useFiltro(id: number | undefined) {
  return useQuery<Filtro>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Filtro>(`/filtros/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateFiltro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: FiltroCreate) => {
      const { data } = await api.post<Filtro>("/filtros", payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUpdateFiltro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: FiltroUpdate }) => {
      const { data } = await api.patch<Filtro>(`/filtros/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteFiltro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/filtros/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUploadFotoFiltro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, file }: { id: number; file: File }) => {
      const formData = new FormData()
      formData.append("file", file)
      const { data } = await api.post<Filtro>(`/filtros/${id}/foto`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteFotoFiltro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await api.delete<Filtro>(`/filtros/${id}/foto`)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}
