import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '../services/auth.service'
import jwt_decode from 'jwt-decode'

interface User {
  id: number
  username: string
  role: string
  permissions: string[]
}

interface JwtPayload {
  sub: string
  role: string
  permissions: string[]
  exp: number
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Initialize user from token if it exists
  if (token.value) {
    try {
      const decoded = jwt_decode<JwtPayload>(token.value)
      user.value = {
        id: parseInt(decoded.sub),
        username: decoded.sub,
        role: decoded.role,
        permissions: decoded.permissions
      }
    } catch (err) {
      // Invalid token
      token.value = null
      localStorage.removeItem('token')
    }
  }

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || '')
  const hasPermission = (permission: string) => {
    return user.value?.permissions.includes(permission) || false
  }

  // Actions
  async function login(username: string, password: string) {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.login(username, password)
      token.value = response.access_token
      localStorage.setItem('token', response.token)
      
      // Decode token to get user info
      const decoded = jwt_decode<JwtPayload>(response.token)
      user.value = {
        id: parseInt(decoded.sub),
        username: decoded.sub,
        role: decoded.role,
        permissions: decoded.permissions
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to login'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    userRole,
    hasPermission,
    login,
    logout
  }
})