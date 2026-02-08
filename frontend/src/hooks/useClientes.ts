import { useCallback, useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import type { Cliente, ClienteCreate, ClienteListResponse, ClienteUpdate } from "@/types/cliente"

const CLIENTES_KEY = "clientes"

export function useClientes(page: number = 1, search?: string) {
  const skip = (page - 1) * 20
  return useQuery<ClienteListResponse>({
    queryKey: [CLIENTES_KEY, page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { skip, limit: 20 }
      if (search) params.search = search
      const { data } = await api.get<ClienteListResponse>("/clientes", { params })
      return data
    },
  })
}

export function useCliente(id: number | undefined) {
  return useQuery<Cliente>({
    queryKey: [CLIENTES_KEY, id],
    queryFn: async () => {
      const { data } = await api.get<Cliente>(`/clientes/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useAllClientes() {
  return useQuery<ClienteListResponse>({
    queryKey: [CLIENTES_KEY, "all"],
    queryFn: async () => {
      const { data } = await api.get<ClienteListResponse>("/clientes", { params: { limit: 100 } })
      return data
    },
  })
}

export function useBuscaCliente() {
  const [cliente, setCliente] = useState<Cliente | null>(null)
  const [sugestoes, setSugestoes] = useState<Cliente[]>([])
  const [buscando, setBuscando] = useState(false)
  const [erro, setErro] = useState("")
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  function buscarSugestoes(termo: string) {
    if (timerRef.current) clearTimeout(timerRef.current)

    if (termo.trim().length < 3) {
      setSugestoes([])
      return
    }

    timerRef.current = setTimeout(async () => {
      setBuscando(true)
      try {
        const { data } = await api.get<ClienteListResponse>("/clientes", {
          params: { search: termo, limit: 8 },
        })
        setSugestoes(data.items)
      } catch {
        setSugestoes([])
      } finally {
        setBuscando(false)
      }
    }, 300)
  }

  function selecionar(c: Cliente) {
    setCliente(c)
    setSugestoes([])
    setErro("")
  }

  const carregarPorId = useCallback(async (id: number) => {
    setBuscando(true)
    setErro("")
    try {
      const { data } = await api.get<Cliente>(`/clientes/${id}`)
      setCliente(data)
    } catch {
      setErro("Erro ao carregar cliente")
    } finally {
      setBuscando(false)
    }
  }, [])

  function limpar() {
    setCliente(null)
    setSugestoes([])
    setErro("")
  }

  return { cliente, sugestoes, buscando, erro, buscarSugestoes, selecionar, carregarPorId, limpar }
}

export function useCreateCliente() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ClienteCreate) => {
      const { data } = await api.post<Cliente>("/clientes", payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTES_KEY] })
    },
  })
}

export function useUpdateCliente() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: ClienteUpdate }) => {
      const { data } = await api.patch<Cliente>(`/clientes/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTES_KEY] })
    },
  })
}

export function useDeleteCliente() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/clientes/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CLIENTES_KEY] })
    },
  })
}
