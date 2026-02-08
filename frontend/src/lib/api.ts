import axios from "axios"
import { clearAuth, getToken } from "./auth"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuth()
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

export default api
