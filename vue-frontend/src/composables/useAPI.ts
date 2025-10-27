import axios from 'axios'
import type {
  UserLogin,
  UserRegister,
  Token,
  TaxInput,
  TaxResult,
  ExplanationRequest,
  ExplanationResponse
} from '@/types/api'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  async login(credentials: UserLogin): Promise<Token> {
    const response = await api.post<Token>('/auth/login', credentials)
    return response.data
  },

  async register(userData: UserRegister): Promise<Token> {
    const response = await api.post<Token>('/auth/register', userData)
    return response.data
  }
}

export const taxAPI = {
  async calculate(input: TaxInput): Promise<TaxResult> {
    const response = await api.post<TaxResult>('/tax/calculate', input)
    return response.data
  },

  async getBrackets(filingStatus: string) {
    const response = await api.get(`/tax/brackets/${filingStatus}`)
    return response.data
  }
}

export const explainAPI = {
  async getExplanation(request: ExplanationRequest): Promise<ExplanationResponse> {
    const response = await api.post<ExplanationResponse>('/explain', request)
    return response.data
  },

  async getTopics() {
    const response = await api.get('/explain/topics')
    return response.data
  }
}

export default api
