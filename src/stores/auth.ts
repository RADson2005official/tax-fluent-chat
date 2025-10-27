import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface User {
  email: string
  fullName: string
  token: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  
  const API_URL = 'http://localhost:8000'
  
  async function register(email: string, password: string, fullName: string) {
    try {
      const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, full_name: fullName }),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }
      
      const data = await response.json()
      user.value = { email, fullName, token: data.access_token }
      isAuthenticated.value = true
      
      // Store token in localStorage
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify({ email, fullName }))
      
      return data
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }
  
  async function login(email: string, password: string) {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }
      
      const data = await response.json()
      const storedUser = localStorage.getItem('user')
      const userData = storedUser ? JSON.parse(storedUser) : { email, fullName: email }
      
      user.value = { ...userData, token: data.access_token }
      isAuthenticated.value = true
      
      // Store token in localStorage
      localStorage.setItem('token', data.access_token)
      
      return data
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }
  
  function logout() {
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  function loadFromStorage() {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      const userData = JSON.parse(userStr)
      user.value = { ...userData, token }
      isAuthenticated.value = true
    }
  }
  
  return {
    user,
    isAuthenticated,
    register,
    login,
    logout,
    loadFromStorage,
  }
})
