import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Veiculo, VeiculoCreate, VeiculoListResponse, VeiculoUpdate } from "@/types/veiculo"

const KEY = "veiculos"

export function useVeiculos(page: number = 1, search?: string, clienteId?: number) {
  const skip = (page - 1) * 20
  return useQuery<VeiculoListResponse>({
    queryKey: [KEY, page, search, clienteId],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (search) params.search = search
      if (clienteId) params.cliente_id = clienteId
      const { data } = await api.get<VeiculoListResponse>("/veiculos", { params })
      return data
    },
  })
}

export function useVeiculo(id: number | undefined) {
  return useQuery<Veiculo>({
    queryKey: [KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Veiculo>(`/veiculos/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useAllVeiculos() {
  return useQuery<VeiculoListResponse>({
    queryKey: [KEY, "all"],
    queryFn: async () => {
      const { data } = await api.get<VeiculoListResponse>("/veiculos", { params: { limit: 100 } })
      return data
    },
  })
}

export function useCreateVeiculo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: VeiculoCreate) => {
      const { data } = await api.post<Veiculo>("/veiculos", payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useUpdateVeiculo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: VeiculoUpdate }) => {
      const { data } = await api.patch<Veiculo>(`/veiculos/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}

export function useDeleteVeiculo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/veiculos/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  })
}
