import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type {
  EntradaEstoque,
  EntradaEstoqueCreate,
  EntradaEstoqueListResponse,
  ProdutoBusca,
} from "@/types/entrada_estoque"

const KEY = "entradas-estoque"

export function useEntradasEstoque(page: number = 1, oleoId?: number) {
  const skip = (page - 1) * 20
  return useQuery<EntradaEstoqueListResponse>({
    queryKey: [KEY, page, oleoId],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (oleoId) params.oleo_id = oleoId
      const { data } = await api.get<EntradaEstoqueListResponse>(
        "/entradas-estoque",
        { params },
      )
      return data
    },
  })
}

export function useCreateEntradaEstoque() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: EntradaEstoqueCreate) => {
      const { data } = await api.post<EntradaEstoque>(
        "/entradas-estoque",
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["oleos"] })
      qc.invalidateQueries({ queryKey: ["filtros"] })
    },
  })
}

export function useDeleteEntradaEstoque() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/entradas-estoque/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
      qc.invalidateQueries({ queryKey: ["oleos"] })
      qc.invalidateQueries({ queryKey: ["filtros"] })
    },
  })
}

export function useBuscarProduto(query: string, tipo?: string) {
  return useQuery<ProdutoBusca[]>({
    queryKey: ["buscar-produto", query, tipo],
    queryFn: async () => {
      const params: Record<string, string> = { q: query }
      if (tipo) params.tipo = tipo
      const { data } = await api.get<ProdutoBusca[]>(
        "/entradas-estoque/buscar-produto",
        { params },
      )
      return data
    },
    enabled: query.length >= 1,
  })
}
