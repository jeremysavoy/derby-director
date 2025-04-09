import { apiClient } from './api.service'

export interface Racer {
  id: number
  first_name: string
  last_name: string
  car_number: string
  rank: string
  weight: number
  checkin_status: 'registered' | 'checked_in' | 'passed_inspection'
  created_at: string
  updated_at: string
  photo_url?: string
  den?: string
  group_id?: number
}

export interface RacerCreateDto {
  first_name: string
  last_name: string
  car_number: string
  rank: string
  weight?: number
  den?: string
  group_id?: number
}

class RacerService {
  async getAllRacers() {
    try {
      const response = await apiClient.get('/racers')
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRacer(id: number) {
    try {
      const response = await apiClient.get(`/racers/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async createRacer(racer: RacerCreateDto) {
    try {
      const response = await apiClient.post('/racers', racer)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async updateRacer(id: number, racer: Partial<RacerCreateDto>) {
    try {
      const response = await apiClient.patch(`/racers/${id}`, racer)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async deleteRacer(id: number) {
    try {
      await apiClient.delete(`/racers/${id}`)
      return true
    } catch (error) {
      throw error
    }
  }

  async updateCheckinStatus(id: number, status: Racer['checkin_status']) {
    try {
      const response = await apiClient.patch(`/racers/${id}/checkin`, { status })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async uploadPhoto(id: number, file: File) {
    try {
      const formData = new FormData()
      formData.append('photo', file)
      
      const response = await apiClient.post(`/racers/${id}/photo`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRankOptions() {
    try {
      const response = await apiClient.get('/racers/ranks')
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getDenOptions() {
    try {
      const response = await apiClient.get('/racers/dens')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default new RacerService()