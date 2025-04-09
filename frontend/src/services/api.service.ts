import axios from 'axios'
import type { 
  AxiosInstance, 
  AxiosResponse, 
  InternalAxiosRequestConfig
} from 'axios'
import { useAuthStore } from '../stores/auth'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    // Get the auth store
    const authStore = useAuthStore()
    
    // Add authorization header if token exists
    if (authStore.token) {
      // Safe way to set headers in Axios 1.x
      config.headers.set('Authorization', `Bearer ${authStore.token}`);
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    
    // If 401 Unauthorized, log out user
    if (error.response && error.response.status === 401) {
      // Check if this is not the login endpoint
      if (error.config.url && !error.config.url.includes('/auth/login')) {
        authStore.logout()
      }
    }
    
    // If 403 Forbidden, handle permission error
    if (error.response && error.response.status === 403) {
      console.error('Permission denied:', error.response.data)
    }
    
    return Promise.reject(error)
  }
)

// Api service with common methods
const apiService = {
  get<T>(url: string, config?: any): Promise<T> {
    return apiClient.get(url, config).then(response => response.data)
  },
  
  post<T>(url: string, data?: any, config?: any): Promise<T> {
    return apiClient.post(url, data, config).then(response => response.data)
  },
  
  put<T>(url: string, data?: any, config?: any): Promise<T> {
    return apiClient.put(url, data, config).then(response => response.data)
  },
  
  patch<T>(url: string, data?: any, config?: any): Promise<T> {
    return apiClient.patch(url, data, config).then(response => response.data)
  },
  
  delete<T>(url: string, config?: any): Promise<T> {
    return apiClient.delete(url, config).then(response => response.data)
  }
}

export { apiClient, apiService }