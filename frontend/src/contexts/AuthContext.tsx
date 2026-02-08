import { createContext, useCallback, useEffect, useState, type ReactNode } from "react"
import api from "@/lib/api"
import { clearAuth, getToken, getStoredUser, setToken, setStoredUser } from "@/lib/auth"
import type { User } from "@/types/auth"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getStoredUser())
  const [isLoading, setIsLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }
    try {
      const { data } = await api.get<User>("/auth/me")
      setUser(data)
      setStoredUser(data)
    } catch {
      clearAuth()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<{ access_token: string }>("/auth/login/json", {
      email,
      password,
    })
    setToken(data.access_token)

    const { data: userData } = await api.get<User>("/auth/me")
    setUser(userData)
    setStoredUser(userData)
  }, [])

  const logout = useCallback(() => {
    clearAuth()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
