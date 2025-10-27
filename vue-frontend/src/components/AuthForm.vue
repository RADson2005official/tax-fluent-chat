<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">{{ isLogin ? 'Login' : 'Register' }}</h2>
      
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="!isLogin" class="form-field">
          <label for="email" class="field-label">Email</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="Enter your email"
            class="field-input"
            required
          />
        </div>

        <div class="form-field">
          <label for="username" class="field-label">Username</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="Enter your username"
            class="field-input"
            required
          />
        </div>

        <div class="form-field">
          <label for="password" class="field-label">Password</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="Enter your password"
            class="field-input"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'Processing...' : (isLogin ? 'Login' : 'Register') }}
        </button>
      </form>

      <div class="auth-toggle">
        <span>{{ isLogin ? "Don't have an account?" : 'Already have an account?' }}</span>
        <button @click="toggleMode" class="toggle-button">
          {{ isLogin ? 'Register' : 'Login' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const error = ref<string | null>(null)

const formData = reactive({
  email: '',
  username: '',
  password: ''
})

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = null
}

async function handleSubmit() {
  loading.value = true
  error.value = null

  try {
    let result
    if (isLogin.value) {
      result = await authStore.login(formData.username, formData.password)
    } else {
      result = await authStore.register(formData.username, formData.email, formData.password)
    }

    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error || 'Authentication failed'
    }
  } catch (err: any) {
    error.value = err.message || 'An error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 400px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 32px 0;
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 14px;
  font-weight: 500;
  color: #2d3748;
}

.field-input {
  padding: 12px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.error-message {
  padding: 12px;
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  color: #c53030;
  font-size: 14px;
  text-align: center;
}

.submit-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.auth-toggle {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #718096;
}

.toggle-button {
  background: none;
  border: none;
  color: #4299e1;
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
  padding: 0;
  text-decoration: underline;
}

.toggle-button:hover {
  color: #3182ce;
}
</style>
