<template>
  <MainLayout>
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1>Derby Director Dashboard</h1>
        <div class="event-info" v-if="eventInfo">
          <h2>{{ eventInfo.event_name }}</h2>
          <div class="event-metadata">
            <div class="event-detail">
              <i class="pi pi-calendar"></i>
              <span>{{ formatDate(eventInfo.event_date) }}</span>
            </div>
            <div class="event-detail">
              <i class="pi pi-map-marker"></i>
              <span>{{ eventInfo.location }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-stats grid">
        <div class="col-12 md:col-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-users"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_racers }}</div>
              <div class="stat-label">Total Racers</div>
            </div>
          </div>
        </div>
        <div class="col-12 md:col-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-flag-fill"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_races }}</div>
              <div class="stat-label">Total Races</div>
            </div>
          </div>
        </div>
        <div class="col-12 md:col-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.checked_in_racers }}</div>
              <div class="stat-label">Checked In</div>
            </div>
          </div>
        </div>
        <div class="col-12 md:col-3">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="pi pi-clock"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.completed_races }}</div>
              <div class="stat-label">Completed Races</div>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-content grid">
        <div class="col-12 md:col-6">
          <Card>
            <template #header>
              <div class="card-header">
                <h2>Recent Activity</h2>
              </div>
            </template>
            <template #content>
              <Timeline :value="recentActivity" class="activity-timeline">
                <template #content="slotProps">
                  <div class="activity-item">
                    <div class="activity-text">{{ slotProps.item.description }}</div>
                    <div class="activity-time">{{ formatTimeAgo(slotProps.item.timestamp) }}</div>
                  </div>
                </template>
              </Timeline>
            </template>
          </Card>
        </div>

        <div class="col-12 md:col-6">
          <Card>
            <template #header>
              <div class="card-header">
                <h2>Current Races</h2>
              </div>
            </template>
            <template #content>
              <div v-if="loadingRaces" class="center-content">
                <ProgressSpinner />
              </div>
              <div v-else-if="!currentRaces.length" class="empty-section">
                <i class="pi pi-flag"></i>
                <p>No active races at the moment</p>
                <Button 
                  label="Create New Race" 
                  icon="pi pi-plus" 
                  @click="router.push('/races')" 
                />
              </div>
              <DataTable v-else :value="currentRaces" class="p-datatable-sm" :rows="5">
                <Column field="name" header="Race Name">
                  <template #body="{ data }">
                    <router-link :to="`/races/${data.id}`">{{ data.name }}</router-link>
                  </template>
                </Column>
                <Column field="status" header="Status">
                  <template #body="{ data }">
                    <Tag :value="formatStatus(data.status)" :severity="getStatusSeverity(data.status)" />
                  </template>
                </Column>
                <Column field="progress" header="Progress">
                  <template #body="{ data }">
                    <ProgressBar 
                      :value="getCompletionPercentage(data)" 
                      :style="{ height: '8px' }" 
                    />
                    <small>{{ data.completed_heats }} / {{ data.total_heats }}</small>
                  </template>
                </Column>
              </DataTable>
            </template>
          </Card>
        </div>

        <div class="col-12 md:col-8">
          <Card>
            <template #header>
              <div class="card-header">
                <h2>Check-in Status</h2>
              </div>
            </template>
            <template #content>
              <div v-if="loadingRacers" class="center-content">
                <ProgressSpinner />
              </div>
              <div v-else>
                <div class="status-chart">
                  <Chart type="pie" :data="checkinChartData" :options="chartOptions" />
                </div>
                <div class="status-legend">
                  <div class="status-item">
                    <div class="status-color" style="background-color: #FF9800;"></div>
                    <div class="status-label">Registered</div>
                    <div class="status-count">{{ stats.registered_racers }}</div>
                  </div>
                  <div class="status-item">
                    <div class="status-color" style="background-color: #2196F3;"></div>
                    <div class="status-label">Checked In</div>
                    <div class="status-count">{{ stats.checked_in_racers }}</div>
                  </div>
                  <div class="status-item">
                    <div class="status-color" style="background-color: #4CAF50;"></div>
                    <div class="status-label">Passed Inspection</div>
                    <div class="status-count">{{ stats.inspected_racers }}</div>
                  </div>
                </div>
              </div>
            </template>
          </Card>
        </div>

        <div class="col-12 md:col-4">
          <Card>
            <template #header>
              <div class="card-header">
                <h2>Quick Actions</h2>
              </div>
            </template>
            <template #content>
              <div class="quick-actions">
                <Button 
                  label="Register Racer" 
                  icon="pi pi-user-plus" 
                  class="p-button-lg w-full mb-3"
                  @click="router.push('/racers')"
                />
                <Button 
                  label="Start New Race" 
                  icon="pi pi-flag" 
                  class="p-button-lg w-full mb-3"
                  @click="router.push('/races')"
                />
                <Button 
                  label="View Results" 
                  icon="pi pi-chart-bar" 
                  class="p-button-lg w-full mb-3"
                  @click="router.push('/reports')"
                />
                <Button 
                  label="Generate Certificates" 
                  icon="pi pi-file" 
                  class="p-button-lg w-full"
                  @click="router.push('/reports')"
                />
              </div>
            </template>
          </Card>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Timeline from 'primevue/timeline'
import ProgressSpinner from 'primevue/progressspinner'
import ProgressBar from 'primevue/progressbar'
import Tag from 'primevue/tag'
import Chart from 'primevue/chart'
import racerService from '../services/racer.service'
import raceService from '../services/race.service'

// Define types for the dashboard data
interface EventInfo {
  event_name: string;
  event_date: Date;
  location: string;
}

interface DashboardStats {
  total_racers: number;
  registered_racers: number;
  checked_in_racers: number;
  inspected_racers: number;
  total_races: number;
  completed_races: number;
  active_races: number;
}

interface Activity {
  description: string;
  timestamp: Date;
}

interface Racer {
  id: number;
  first_name: string;
  last_name: string;
  car_number: string;
  rank: string;
  checkin_status: 'registered' | 'checked_in' | 'passed_inspection';
  [key: string]: any;
}

interface Race {
  id: number;
  name: string;
  status: 'pending' | 'in_progress' | 'completed';
  total_heats: number;
  completed_heats: number;
  [key: string]: any;
}

// Initialize services
const router = useRouter()

// Dashboard data
const eventInfo = ref<EventInfo>({
  event_name: 'Pinewood Derby 2025',
  event_date: new Date('2025-04-15'),
  location: 'Community Center'
})

const stats = ref<DashboardStats>({
  total_racers: 0,
  registered_racers: 0,
  checked_in_racers: 0,
  inspected_racers: 0,
  total_races: 0,
  completed_races: 0,
  active_races: 0
})

const recentActivity = ref<Activity[]>([
  { description: 'Race "Tiger Finals" completed', timestamp: new Date(Date.now() - 1000 * 60 * 30) }, // 30 mins ago
  { description: 'John Smith checked in', timestamp: new Date(Date.now() - 1000 * 60 * 45) }, // 45 mins ago
  { description: 'Heat #3 of "Wolf Prelims" completed', timestamp: new Date(Date.now() - 1000 * 60 * 60) }, // 1 hour ago
  { description: 'New racer Mike Johnson registered', timestamp: new Date(Date.now() - 1000 * 60 * 90) }, // 1.5 hours ago
  { description: 'Race "Bear Finals" completed', timestamp: new Date(Date.now() - 1000 * 60 * 120) } // 2 hours ago
])

const currentRaces = ref<Race[]>([])
const loadingRaces = ref(true)

const racers = ref<Racer[]>([])
const loadingRacers = ref(true)

// Chart data
const checkinChartData = computed(() => {
  return {
    labels: ['Registered', 'Checked In', 'Passed Inspection'],
    datasets: [
      {
        data: [
          stats.value.registered_racers, 
          stats.value.checked_in_racers, 
          stats.value.inspected_racers
        ],
        backgroundColor: ['#FF9800', '#2196F3', '#4CAF50'],
        hoverBackgroundColor: ['#F57C00', '#1976D2', '#388E3C']
      }
    ]
  }
})

const chartOptions = {
  plugins: {
    legend: {
      display: false
    }
  },
  responsive: true,
  maintainAspectRatio: false
}

// Load dashboard data
onMounted(async () => {
  try {
    // Load racers data
    const racersData = await racerService.getAllRacers()
    racers.value = racersData
    
    // Calculate stats
    stats.value.total_racers = racersData.length
    stats.value.registered_racers = racersData.filter((r: Racer) => r.checkin_status === 'registered').length
    stats.value.checked_in_racers = racersData.filter((r: Racer) => r.checkin_status === 'checked_in').length
    stats.value.inspected_racers = racersData.filter((r: Racer) => r.checkin_status === 'passed_inspection').length
    
    // Load races data
    const racesData = await raceService.getAllRaces()
    currentRaces.value = racesData.filter((r: Race) => r.status !== 'completed').slice(0, 5)
    
    // Calculate race stats
    stats.value.total_races = racesData.length
    stats.value.completed_races = racesData.filter((r: Race) => r.status === 'completed').length
    stats.value.active_races = racesData.filter((r: Race) => r.status === 'in_progress').length
    
    // Load recent activity
    // This would typically come from an API, but we're using mock data for now
  } catch (error) {
    console.error('Error loading dashboard data', error)
  } finally {
    loadingRaces.value = false
    loadingRacers.value = false
  }
})

// Formatting functions
function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatTimeAgo(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.round(diffMs / (1000 * 60))
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`
  
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`
}

function formatStatus(status: string): string {
  switch (status) {
    case 'pending':
      return 'Pending'
    case 'in_progress':
      return 'In Progress'
    case 'completed':
      return 'Completed'
    default:
      return 'Unknown'
  }
}

function getStatusSeverity(status: string): string {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'in_progress':
      return 'info'
    case 'completed':
      return 'success'
    default:
      return 'secondary'
  }
}

function getCompletionPercentage(race: Race): number {
  if (race.total_heats === 0) return 0
  return Math.round((race.completed_heats / race.total_heats) * 100)
}
</script>

<style scoped>
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.event-info {
  margin-top: 1rem;
}

.event-info h2 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
}

.event-metadata {
  display: flex;
  gap: 1.5rem;
}

.event-detail {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color-secondary);
}

.dashboard-stats {
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: rgba(var(--primary-color-rgb), 0.1);
  margin-right: 1rem;
}

.stat-icon i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: bold;
  line-height: 1.2;
}

.stat-label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.card-header {
  padding: 1rem;
}

.card-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.activity-timeline {
  margin-top: 0.5rem;
}

.activity-item {
  margin-bottom: 1rem;
}

.activity-time {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  margin-top: 0.25rem;
}

.center-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-section i {
  font-size: 2rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.status-chart {
  height: 200px;
  margin-bottom: 1.5rem;
}

.status-legend {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.status-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-bottom: 0.5rem;
}

.status-count {
  font-weight: bold;
  font-size: 1.25rem;
  margin-top: 0.25rem;
}

.quick-actions {
  padding: 1rem 0;
}
</style>