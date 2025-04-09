import { apiClient } from './api.service'

export interface Race {
  id: number
  name: string
  status: 'pending' | 'in_progress' | 'completed'
  race_type: 'round_robin' | 'elimination' | 'custom'
  group_id?: number
  created_at: string
  updated_at: string
  completed_at?: string
  total_heats: number
  completed_heats: number
}

export interface Heat {
  id: number
  race_id: number
  heat_number: number
  status: 'pending' | 'in_progress' | 'completed'
  created_at: string
  updated_at: string
  lanes: HeatLane[]
}

export interface HeatLane {
  id: number
  heat_id: number
  lane_number: number
  racer_id: number
  racer_name: string
  car_number: string
  finish_position?: number
  finish_time?: number
  dnf: boolean
}

export interface RaceCreateDto {
  name: string
  race_type: 'round_robin' | 'elimination' | 'custom'
  group_id?: number
  include_all_racers?: boolean
  selected_racer_ids?: number[]
}

export interface HeatResultDto {
  heat_id: number
  lanes: {
    lane_id: number
    finish_position?: number
    finish_time?: number
    dnf: boolean
  }[]
}

class RaceService {
  async getAllRaces() {
    try {
      const response = await apiClient.get('/races')
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRace(id: number) {
    try {
      const response = await apiClient.get(`/races/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async createRace(race: RaceCreateDto) {
    try {
      const response = await apiClient.post('/races', race)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async updateRace(id: number, race: Partial<RaceCreateDto>) {
    try {
      const response = await apiClient.patch(`/races/${id}`, race)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async deleteRace(id: number) {
    try {
      await apiClient.delete(`/races/${id}`)
      return true
    } catch (error) {
      throw error
    }
  }

  async startRace(id: number) {
    try {
      const response = await apiClient.post(`/races/${id}/start`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async completeRace(id: number) {
    try {
      const response = await apiClient.post(`/races/${id}/complete`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getHeats(raceId: number) {
    try {
      const response = await apiClient.get(`/races/${raceId}/heats`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getHeat(heatId: number) {
    try {
      const response = await apiClient.get(`/heats/${heatId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async startHeat(heatId: number) {
    try {
      const response = await apiClient.post(`/heats/${heatId}/start`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async submitHeatResults(results: HeatResultDto) {
    try {
      const response = await apiClient.post(`/heats/${results.heat_id}/results`, results)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRaceResults(raceId: number) {
    try {
      const response = await apiClient.get(`/races/${raceId}/results`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async generateHeats(raceId: number) {
    try {
      const response = await apiClient.post(`/races/${raceId}/generate-heats`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default new RaceService()