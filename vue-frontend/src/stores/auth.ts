import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Token } from '@/types/api'
import { authAPI } from '@/composables/useAPI'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const username = ref<string | null>(localStorage.getItem('username'))
  const isAuthenticated = ref<boolean>(!!token.value)

  async function login(usernameInput: string, password: string) {
    try {
      const response = await authAPI.login({ username: usernameInput, password })
      token.value = response.access_token
      username.value = usernameInput
      isAuthenticated.value = true
      
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('username', usernameInput)
      
      return { success: true }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  async function register(usernameInput: string, email: string, password: string) {
    try {
      const response = await authAPI.register({ username: usernameInput, email, password })
      token.value = response.access_token
      username.value = usernameInput
      isAuthenticated.value = true
      
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('username', usernameInput)
      
      return { success: true }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  function logout() {
    token.value = null
    username.value = null
    isAuthenticated.value = false
    
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }

  return {
    token,
    username,
    isAuthenticated,
    login,
    register,
    logout
  }
})
