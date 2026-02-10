import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Oleo, OleoCreate, OleoListResponse, OleoUpdate } from "@/types/oleo"

const KEY = "oleos"

export function useOleos(page: number = 1, search?: string, tipo?: string) {
  const skip = (page - 1) * 20
  return useQuery<OleoListResponse>({
    queryKey: [KEY, page, search, tipo],
    queryFn: async () => {
      const params: Record<string, string | number | boolean> = { skip, limit: 20 }
      if (search) params.search = search
      if (tipo) params.tipo = tipo
      const { data } = await api.get<OleoListResponse>("/oleos", { params })
      return data
    },
  })
}

export function useOleo(id: number | undefined) {
  return useQuery<Oleo>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Oleo>(`/oleos/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useAllOleos() {
  return useQuery<OleoListResponse>({
    queryKey: [KEY, "all"],
    queryFn: async () => {
      const { data } = await api.get<OleoListResponse>("/oleos", { params: { limit: 100 } })
      return data
    },
  })
}

export function useCreateOleo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: OleoCreate) => {
      const { data } = await api.post<Oleo>("/oleos", payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUpdateOleo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: OleoUpdate }) => {
      const { data } = await api.patch<Oleo>(`/oleos/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteOleo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/oleos/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUploadFotoOleo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, file }: { id: number; file: File }) => {
      const formData = new FormData()
      formData.append("file", file)
      const { data } = await api.post<Oleo>(`/oleos/${id}/foto`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteFotoOleo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await api.delete<Oleo>(`/oleos/${id}/foto`)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}
