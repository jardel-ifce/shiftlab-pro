export interface User {
  id: number
  email: string
  nome: string
  role: "admin" | "funcionario"
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}
