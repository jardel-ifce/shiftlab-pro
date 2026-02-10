export function formatCpfCnpj(value: string): string {
  const digits = value.replace(/\D/g, "")

  if (digits.length <= 11) {
    // CPF: 000.000.000-00
    return digits
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d{1,2})$/, "$1-$2")
  }
  // CNPJ: 00.000.000/0000-00
  return digits
    .replace(/(\d{2})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1/$2")
    .replace(/(\d{4})(\d{1,2})$/, "$1-$2")
}

export function formatTelefone(value: string): string {
  const digits = value.replace(/\D/g, "")

  if (digits.length <= 10) {
    // (00) 0000-0000
    return digits
      .replace(/(\d{2})(\d)/, "($1) $2")
      .replace(/(\d{4})(\d{1,4})$/, "$1-$2")
  }
  // (00) 00000-0000
  return digits
    .replace(/(\d{2})(\d)/, "($1) $2")
    .replace(/(\d{5})(\d{1,4})$/, "$1-$2")
}

export function unmask(value: string): string {
  return value.replace(/\D/g, "")
}

/**
 * Formata valor como moeda brasileira (sem prefixo R$).
 * Entrada: dígitos puros ou string formatada.
 * Saída: "1.234,56"
 *
 * Funciona em tempo real conforme o usuário digita:
 * - Aceita apenas dígitos
 * - Últimos 2 dígitos são centavos
 * - Exemplo: digitar "5000" exibe "50,00"
 */
export function formatMoeda(value: string): string {
  const digits = value.replace(/\D/g, "")
  if (!digits) return ""

  const cents = parseInt(digits, 10)
  const formatted = (cents / 100).toFixed(2)

  const [intPart, decPart] = formatted.split(".")
  const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".")

  return `${intFormatted},${decPart}`
}

/**
 * Formata valor decimal com vírgula (para campos como estoque).
 * Entrada: dígitos puros ou string formatada.
 * Saída: "10,5"
 *
 * Últimos N dígitos são a parte decimal.
 */
export function formatDecimal(value: string, casas: number = 1): string {
  const digits = value.replace(/\D/g, "")
  if (!digits) return ""

  const divisor = Math.pow(10, casas)
  const num = parseInt(digits, 10) / divisor
  const formatted = num.toFixed(casas)

  const [intPart, decPart] = formatted.split(".")
  const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".")

  return `${intFormatted},${decPart}`
}

/**
 * Converte moeda formatada "1.234,56" para number 1234.56.
 */
export function parseMoeda(value: string): number {
  if (!value) return 0
  return parseFloat(value.replace(/\./g, "").replace(",", ".")) || 0
}

/**
 * Converte decimal formatado "10,5" para number 10.5.
 */
export function parseDecimal(value: string): number {
  if (!value) return 0
  return parseFloat(value.replace(/\./g, "").replace(",", ".")) || 0
}

/**
 * Converte um número (da API, ex: "50.00" ou 50) para formato moeda "50,00".
 * Usado para popular o form no modo edição.
 */
export function numberToMoeda(value: string | number | null | undefined): string {
  if (value == null || value === "") return ""
  const num = typeof value === "string" ? parseFloat(value) : value
  if (isNaN(num)) return ""
  const formatted = num.toFixed(2)
  const [intPart, decPart] = formatted.split(".")
  const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".")
  return `${intFormatted},${decPart}`
}

/**
 * Converte um número (da API) para formato decimal "10,5".
 */
export function numberToDecimal(value: string | number | null | undefined, casas: number = 1): string {
  if (value == null || value === "") return ""
  const num = typeof value === "string" ? parseFloat(value) : value
  if (isNaN(num)) return ""
  const formatted = num.toFixed(casas)
  const [intPart, decPart] = formatted.split(".")
  const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".")
  return `${intFormatted},${decPart}`
}
