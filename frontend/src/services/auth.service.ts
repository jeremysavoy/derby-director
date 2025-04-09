import axios from 'axios'
import { apiClient } from './api.service'

class AuthService {
  async login(username: string, password: string) {
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
        username,
        password
      })
      return response.data
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Authentication failed')
      }
      throw new Error('Authentication service unavailable')
    }
  }

  async getUserProfile() {
    try {
      const response = await apiClient.get('/auth/me')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default new AuthService()