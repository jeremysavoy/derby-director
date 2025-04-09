import { apiClient } from './api.service'

export interface RacerResult {
  racer_id: number
  first_name: string
  last_name: string
  car_number: string
  rank: string
  den?: string
  total_points: number
  avg_time?: number
  fastest_time?: number
  races_completed: number
  position: number
}

export interface RaceReport {
  race_id: number
  name: string
  race_type: string
  status: string
  created_at: string
  completed_at?: string
  results: RacerResult[]
}

export interface AwardCertificateParams {
  race_id?: number
  racer_id?: number
  award_type: 'winner' | 'participant' | 'speed' | 'design' | 'custom'
  title?: string
  description?: string
}

class ReportService {
  async getAllResults() {
    try {
      const response = await apiClient.get('/reports/results')
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRaceReport(raceId: number) {
    try {
      const response = await apiClient.get(`/reports/races/${raceId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRacerHistory(racerId: number) {
    try {
      const response = await apiClient.get(`/reports/racers/${racerId}`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async generateCertificate(params: AwardCertificateParams) {
    try {
      const response = await apiClient.post('/reports/certificates', params, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getOverallStandings() {
    try {
      const response = await apiClient.get('/reports/standings')
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRankStandings(rank: string) {
    try {
      const response = await apiClient.get(`/reports/standings/${rank}`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default new ReportService()