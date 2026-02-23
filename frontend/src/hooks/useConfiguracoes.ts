import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"

const KEY = "configuracoes"

export interface ImpostoResponse {
  percentual: number
}

export function useImposto() {
  return useQuery<ImpostoResponse>({
    queryKey: [KEY, "imposto"],
    queryFn: async () => {
      const { data } = await api.get<ImpostoResponse>("/configuracoes/imposto")
      return data
    },
  })
}

export function useUpdateImposto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (percentual: number) => {
      const { data } = await api.put<ImpostoResponse>("/configuracoes/imposto", {
        valor: String(percentual),
      })
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["financeiro"] })
    },
  })
}
