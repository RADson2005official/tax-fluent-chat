import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
    id: number
    email: string
    full_name: string
}

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))

    const isAuthenticated = computed(() => !!token.value)

    async function login(email: string, password: string) {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)

        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            body: formData,
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Login failed')
        }

        const data = await response.json()

        token.value = data.access_token
        user.value = {
            id: data.user_id,
            email: data.email,
            full_name: data.full_name
        }

        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(user.value))
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    async function register(email: string, password: string, fullName: string) {
        const response = await fetch('http://localhost:8000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
            }),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Registration failed')
        }
    }

    const mode = ref<string>('novice')

    function setMode(newMode: string) {
        mode.value = newMode
    }

    return {
        token,
        user,
        mode,
        isAuthenticated,
        login,
        register,
        logout,
        setMode
    }
})
