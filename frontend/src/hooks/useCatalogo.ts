import { useQuery } from "@tanstack/react-query"
import api from "@/lib/api"
import type {
  MontadoraListResponse,
  ModeloReferenciaListResponse,
  FipeMarca,
  FipeModelo,
  FipeAno,
} from "@/types/catalogo"

const CATALOGO_KEY = "catalogo"
const FIPE_KEY = "fipe"

// =============================================================================
// CATÁLOGO LOCAL
// =============================================================================

export function useMontadoras() {
  return useQuery<MontadoraListResponse>({
    queryKey: [CATALOGO_KEY, "montadoras"],
    queryFn: async () => {
      const { data } = await api.get<MontadoraListResponse>("/catalogo/montadoras")
      return data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useModelosByMontadora(montadoraId: number | undefined) {
  return useQuery<ModeloReferenciaListResponse>({
    queryKey: [CATALOGO_KEY, "modelos", montadoraId],
    queryFn: async () => {
      const { data } = await api.get<ModeloReferenciaListResponse>(
        "/catalogo/modelos",
        { params: { montadora_id: montadoraId } }
      )
      return data
    },
    enabled: !!montadoraId,
    staleTime: 5 * 60 * 1000,
  })
}

// =============================================================================
// FIPE (Tabela FIPE via proxy backend)
// =============================================================================

export function useFipeMarcas(enabled: boolean = true) {
  return useQuery<FipeMarca[]>({
    queryKey: [FIPE_KEY, "marcas"],
    queryFn: async () => {
      const { data } = await api.get<FipeMarca[]>("/catalogo/fipe/marcas")
      return data
    },
    enabled,
    staleTime: 24 * 60 * 60 * 1000, // 24h
  })
}

export function useFipeModelos(marcaCode: string | undefined, enabled: boolean = true) {
  return useQuery<FipeModelo[]>({
    queryKey: [FIPE_KEY, "modelos", marcaCode],
    queryFn: async () => {
      const { data } = await api.get<FipeModelo[]>("/catalogo/fipe/modelos", {
        params: { marca_code: marcaCode },
      })
      return data
    },
    enabled: enabled && !!marcaCode,
    staleTime: 24 * 60 * 60 * 1000,
  })
}

export function useFipeAnos(
  marcaCode: string | undefined,
  modeloCode: string | undefined,
  enabled: boolean = true
) {
  return useQuery<FipeAno[]>({
    queryKey: [FIPE_KEY, "anos", marcaCode, modeloCode],
    queryFn: async () => {
      const { data } = await api.get<FipeAno[]>("/catalogo/fipe/anos", {
        params: { marca_code: marcaCode, modelo_code: modeloCode },
      })
      return data
    },
    enabled: enabled && !!marcaCode && !!modeloCode,
    staleTime: 24 * 60 * 60 * 1000,
  })
}
