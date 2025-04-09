// Auth Types
export interface User {
    id: number
    username: string
    role: string
    permissions: string[]
  }
  
  export interface JwtPayload {
    sub: string
    role: string
    permissions: string[]
    exp: number
  }
  
  export interface AuthResponse {
    token: string
    token_type: string
  }
  
  // Racer Types
  export interface Racer {
    id: number
    first_name: string
    last_name: string
    car_number: string
    rank: string
    weight?: number
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
  
  // Race Types
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
      lane_number: number
      racer_name?: string
      car_number?: string
      finish_position?: number
      finish_time?: number
      dnf: boolean
    }[]
  }
  
  // Report Types
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
  
  // UI Types
  export interface SelectOption {
    name: string
    value: string | number | null
  }
  
  export interface EventInfo {
    event_name: string
    event_date: Date
    location: string
  }
  
  export interface DashboardStats {
    total_racers: number
    registered_racers: number
    checked_in_racers: number
    inspected_racers: number
    total_races: number
    completed_races: number
    active_races: number
  }
  
  export interface ActivityItem {
    description: string
    timestamp: Date
    type?: string
  }