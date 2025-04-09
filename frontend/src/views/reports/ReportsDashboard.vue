<template>
  <MainLayout>
    <div class="reports-container">
      <div class="reports-header">
        <h1>Reports & Results</h1>
      </div>

      <div class="reports-tabs">
        <TabView>
          <TabPanel header="Overall Standings" value="Overall Standings">
            <div class="tab-content">
              <div v-if="loadingStandings" class="center-content">
                <ProgressSpinner />
              </div>
              <div v-else-if="!standings.length" class="center-content">
                <div class="empty-message">
                  <i class="pi pi-chart-bar"></i>
                  <h3>No Standings Available</h3>
                  <p>Complete some races to see standings here.</p>
                </div>
              </div>
              <div v-else class="standings-container">
                <div class="filter-container">
                  <div class="filter-section">
                    <label for="rankFilter">Filter by Rank:</label>
                    <Dropdown 
                      id="rankFilter" 
                      v-model="selectedRank" 
                      :options="rankOptions" 
                      optionLabel="name" 
                      optionValue="value"
                      placeholder="All Ranks" 
                      @change="filterStandings"
                    />
                  </div>
                  <div class="action-section">
                    <Button 
                      icon="pi pi-print" 
                      label="Print Standings" 
                      @click="printStandings"
                    />
                  </div>
                </div>

                <DataTable 
                  :value="filteredStandings" 
                  responsive-layout="stack"
                  class="p-datatable-sm"
                >
                  <Column field="position" header="Position" :sortable="true">
                    <template #body="{ data }">
                      <div class="position-cell">
                        <span class="position-badge" :class="getPositionClass(data.position)">
                          {{ data.position }}
                        </span>
                      </div>
                    </template>
                  </Column>
                  <Column field="car_number" header="Car #" :sortable="true" />
                  <Column field="racer_name" header="Racer" :sortable="true">
                    <template #body="{ data }">
                      {{ data.first_name }} {{ data.last_name }}
                    </template>
                  </Column>
                  <Column field="rank" header="Rank" :sortable="true">
                    <template #body="{ data }">
                      <Chip :label="data.rank" />
                    </template>
                  </Column>
                  <Column field="total_points" header="Points" :sortable="true" />
                  <Column field="fastest_time" header="Fastest Time" :sortable="true">
                    <template #body="{ data }">
                      {{ data.fastest_time ? data.fastest_time.toFixed(3) + 's' : '-' }}
                    </template>
                  </Column>
                  <Column field="avg_time" header="Avg Time" :sortable="true">
                    <template #body="{ data }">
                      {{ data.avg_time ? data.avg_time.toFixed(3) + 's' : '-' }}
                    </template>
                  </Column>
                  <Column field="races_completed" header="Races" :sortable="true" />
                  <Column header="Actions">
                    <template #body="{ data }">
                      <div class="action-buttons">
                        <Button 
                          icon="pi pi-user" 
                          class="p-button-rounded p-button-text p-button-sm"
                          @click="viewRacerDetail(data.racer_id)"
                          tooltip="Racer Details"
                        />
                        <Button 
                          icon="pi pi-file" 
                          class="p-button-rounded p-button-text p-button-sm"
                          @click="openCertificateDialog(data)"
                          tooltip="Generate Certificate"
                        />
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </TabPanel>
          <TabPanel header="Race Results" value="Race Results">
            <div class="tab-content">
              <div v-if="loadingRaces" class="center-content">
                <ProgressSpinner />
              </div>
              <div v-else-if="!races.length" class="center-content">
                <div class="empty-message">
                  <i class="pi pi-flag"></i>
                  <h3>No Race Results Available</h3>
                  <p>Complete races to see results here.</p>
                </div>
              </div>
              <div v-else class="race-results-container">
                <div class="race-selection">
                  <h3>Select a Race:</h3>
                  <Dropdown 
                    v-model="selectedRace" 
                    :options="races" 
                    optionLabel="name" 
                    placeholder="Select Race"
                    class="w-full" 
                    @change="loadRaceReport"
                  />
                </div>

                <div v-if="loadingRaceReport" class="center-content">
                  <ProgressSpinner />
                </div>
                <div v-else-if="selectedRace && raceReport">
                  <div class="race-report-header">
                    <h2>{{ raceReport.name }} Results</h2>
                    <div class="race-metadata">
                      <Tag :value="formatRaceType(raceReport.race_type)" severity="info" />
                      <Tag :value="formatStatus(raceReport.status)" :severity="getStatusSeverity(raceReport.status)" />
                      <span v-if="raceReport.completed_at" class="completed-date">
                        Completed: {{ formatDate(raceReport.completed_at) }}
                      </span>
                    </div>
                    <div class="race-report-actions">
                      <Button 
                        icon="pi pi-print" 
                        label="Print Results" 
                        @click="printRaceResults"
                      />
                      <Button 
                        icon="pi pi-file" 
                        label="Certificates" 
                        @click="openBatchCertificatesDialog"
                      />
                    </div>
                  </div>

                  <DataTable 
                    :value="raceReport.results" 
                    responsive-layout="stack"
                    class="p-datatable-sm"
                  >
                    <Column field="position" header="Position" :sortable="true">
                      <template #body="{ data }">
                        <span class="position-badge" :class="getPositionClass(data.position)">
                          {{ data.position }}
                        </span>
                      </template>
                    </Column>
                    <Column field="car_number" header="Car #" :sortable="true" />
                    <Column field="racer_name" header="Racer" :sortable="true">
                      <template #body="{ data }">
                        {{ data.first_name }} {{ data.last_name }}
                      </template>
                    </Column>
                    <Column field="total_points" header="Points" :sortable="true" />
                    <Column field="fastest_time" header="Fastest Time" :sortable="true">
                      <template #body="{ data }">
                        {{ data.fastest_time ? data.fastest_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                    <Column field="avg_time" header="Avg Time" :sortable="true">
                      <template #body="{ data }">
                        {{ data.avg_time ? data.avg_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                    <Column header="Actions">
                      <template #body="{ data }">
                        <Button 
                          icon="pi pi-file" 
                          class="p-button-rounded p-button-text p-button-sm"
                          @click="generateCertificate({ 
                            race_id: raceReport.race_id, 
                            racer_id: data.racer_id, 
                            award_type: data.position === 1 ? 'winner' : 'participant'
                          })"
                          tooltip="Certificate"
                        />
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
            </div>
          </TabPanel>
        </TabView>
      </div>
    </div>

    <!-- Certificate Generation Dialog -->
    <Dialog 
      v-model:visible="certificateDialog" 
      header="Generate Certificate" 
      :modal="true" 
      class="p-fluid"
      :style="{width: '450px'}"
    >
      <div v-if="selectedRacer" class="certificate-form">
        <div class="racer-info-section">
          <h3>{{ selectedRacer.first_name }} {{ selectedRacer.last_name }}</h3>
          <p>Car #{{ selectedRacer.car_number }} | {{ selectedRacer.rank }}</p>
        </div>
        
        <div class="field">
          <label for="awardType">Certificate Type</label>
          <Dropdown 
            id="awardType" 
            v-model="certificateParams.award_type" 
            :options="certificateTypes" 
            optionLabel="name" 
            optionValue="value"
            placeholder="Select Certificate Type" 
            required 
          />
        </div>
        
        <div class="field" v-if="certificateParams.award_type === 'custom'">
          <label for="title">Certificate Title</label>
          <InputText 
            id="title" 
            v-model="certificateParams.title" 
            placeholder="Enter certificate title" 
            required 
          />
        </div>
        
        <div class="field" v-if="certificateParams.award_type === 'custom'">
          <label for="description">Description</label>
          <Textarea 
            id="description" 
            v-model="certificateParams.description" 
            rows="3" 
            placeholder="Enter certificate description" 
          />
        </div>
        
        <div class="field">
          <label for="raceId">Race (Optional)</label>
          <Dropdown 
            id="raceId" 
            v-model="certificateParams.race_id" 
            :options="races" 
            optionLabel="name" 
            optionValue="race_id"
            placeholder="Select Race" 
          />
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="certificateDialog = false" />
        <Button label="Generate" icon="pi pi-file" class="p-button-primary" @click="generateSelectedCertificate" :loading="generatingCertificate" />
      </template>
    </Dialog>

    <!-- Batch Certificates Dialog -->
    <Dialog 
      v-model:visible="batchCertificatesDialog" 
      header="Generate Certificates" 
      :modal="true" 
      class="p-fluid"
      :style="{width: '450px'}"
    >
      <div v-if="raceReport" class="batch-certificates-form">
        <h3>{{ raceReport.name }}</h3>
        
        <div class="field-checkbox">
          <Checkbox 
            id="winnerCertificates" 
            v-model="batchCertificates.winners" 
            :binary="true" 
          />
          <label for="winnerCertificates">Winner Certificates (Top 3)</label>
        </div>
        
        <div class="field-checkbox">
          <Checkbox 
            id="participantCertificates" 
            v-model="batchCertificates.participants" 
            :binary="true" 
          />
          <label for="participantCertificates">Participation Certificates (All)</label>
        </div>
        
        <div class="field-checkbox">
          <Checkbox 
            id="speedCertificates" 
            v-model="batchCertificates.fastest" 
            :binary="true" 
          />
          <label for="speedCertificates">Fastest Time Certificates</label>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="batchCertificatesDialog = false" />
        <Button label="Generate All" icon="pi pi-file" class="p-button-primary" @click="generateBatchCertificates" :loading="generatingCertificate" />
      </template>
    </Dialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import MainLayout from '../../layouts/MainLayout.vue'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import Dialog from 'primevue/dialog'
import reportService from '../../services/report.service'
import type { RacerResult } from '../../services/report.service'
import type { RaceReport } from '../../services/report.service'
import type { AwardCertificateParams } from '../../services/report.service'

// Initialize services
const router = useRouter()
const toast = useToast()

// Standings state
const standings = ref<RacerResult[]>([])
const filteredStandings = ref<RacerResult[]>([])
const loadingStandings = ref(true)
const selectedRank = ref(null)

// Races state
const races = ref<any[]>([])
const loadingRaces = ref(true)
const selectedRace = ref<any>(null)
const raceReport = ref<RaceReport | null>(null)
const loadingRaceReport = ref(false)

// Certificate dialog
const certificateDialog = ref(false)
const selectedRacer = ref<RacerResult | null>(null)
const certificateParams = ref<AwardCertificateParams>({
  award_type: 'participant',
  title: '',
  description: ''
})
const generatingCertificate = ref(false)

// Batch certificates dialog
const batchCertificatesDialog = ref(false)
const batchCertificates = ref({
  winners: true,
  participants: true,
  fastest: false
})

// Options
const rankOptions = [
  { name: 'All Ranks', value: null },
  { name: 'Lion', value: 'Lion' },
  { name: 'Tiger', value: 'Tiger' },
  { name: 'Wolf', value: 'Wolf' },
  { name: 'Bear', value: 'Bear' },
  { name: 'Webelos', value: 'Webelos' },
  { name: 'Arrow of Light', value: 'Arrow of Light' }
]

const certificateTypes = [
  { name: 'Race Winner', value: 'winner' },
  { name: 'Participation', value: 'participant' },
  { name: 'Speed Award', value: 'speed' },
  { name: 'Design Award', value: 'design' },
  { name: 'Custom Award', value: 'custom' }
]

// Load data on component mount
onMounted(async () => {
  await Promise.all([
    loadStandings(),
    loadRaces()
  ])
})

async function loadStandings() {
  try {
    loadingStandings.value = true
    const response = await reportService.getOverallStandings()
    standings.value = response
    filteredStandings.value = [...response]
  } catch (error) {
    console.error('Error loading standings', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to load standings', 
      life: 3000 
    })
  } finally {
    loadingStandings.value = false
  }
}

async function loadRaces() {
  try {
    loadingRaces.value = true
    const response = await reportService.getAllResults()
    races.value = response
  } catch (error) {
    console.error('Error loading races', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to load races', 
      life: 3000 
    })
  } finally {
    loadingRaces.value = false
  }
}

async function loadRaceReport() {
  if (!selectedRace.value) return
  
  try {
    loadingRaceReport.value = true
    const response = await reportService.getRaceReport(selectedRace.value.race_id)
    raceReport.value = response
  } catch (error) {
    console.error('Error loading race report', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to load race report', 
      life: 3000 
    })
  } finally {
    loadingRaceReport.value = false
  }
}

async function filterStandings() {
  if (selectedRank.value) {
    try {
      loadingStandings.value = true
      const response = await reportService.getRankStandings(selectedRank.value)
      filteredStandings.value = response
    } catch (error) {
      console.error('Error loading filtered standings', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load filtered standings', 
        life: 3000 
      })
    } finally {
      loadingStandings.value = false
    }
  } else {
    filteredStandings.value = [...standings.value]
  }
}

// Formatting functions
function formatRaceType(type: string) {
  switch (type) {
    case 'round_robin':
      return 'Round Robin'
    case 'elimination':
      return 'Elimination'
    case 'custom':
      return 'Custom'
    default:
      return type
  }
}

function formatStatus(status: string) {
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

function getStatusSeverity(status: string) {
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

function getPositionClass(position: number) {
  switch (position) {
    case 1:
      return 'position-first'
    case 2:
      return 'position-second'
    case 3:
      return 'position-third'
    default:
      return 'position-other'
  }
}

function formatDate(dateString: string | undefined) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

// Actions
function viewRacerDetail(racerId: number) {
  router.push(`/racers/${racerId}`)
}

function openCertificateDialog(racer: RacerResult) {
  selectedRacer.value = racer
  
  // Initialize certificate params
  certificateParams.value = {
    racer_id: racer.racer_id,
    award_type: racer.position <= 3 ? 'winner' : 'participant',
    race_id: undefined,
    title: '',
    description: ''
  }
  
  certificateDialog.value = true
}

function openBatchCertificatesDialog() {
  if (!raceReport.value) return
  
  batchCertificates.value = {
    winners: true,
    participants: true,
    fastest: false
  }
  
  batchCertificatesDialog.value = true
}

async function generateSelectedCertificate() {
  if (!selectedRacer.value) return
  
  generatingCertificate.value = true
  
  try {
    const blob = await reportService.generateCertificate({
      ...certificateParams.value,
      racer_id: selectedRacer.value.racer_id
    })
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `certificate_${selectedRacer.value.first_name}_${selectedRacer.value.last_name}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Certificate generated', 
      life: 3000 
    })
    
    certificateDialog.value = false
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to generate certificate', 
      life: 3000 
    })
  } finally {
    generatingCertificate.value = false
  }
}

async function generateBatchCertificates() {
  if (!raceReport.value) return
  
  generatingCertificate.value = true
  
  try {
    const raceId = raceReport.value.race_id
    const results = raceReport.value.results
    
    // Generate certificates based on selection
    if (batchCertificates.value.winners) {
      // Generate for top 3
      const winners = results.filter(r => r.position <= 3)
      for (const winner of winners) {
        await reportService.generateCertificate({
          race_id: raceId,
          racer_id: winner.racer_id,
          award_type: 'winner'
        })
      }
    }
    
    if (batchCertificates.value.participants) {
      // Generate for all participants
      for (const racer of results) {
        await reportService.generateCertificate({
          race_id: raceId,
          racer_id: racer.racer_id,
          award_type: 'participant'
        })
      }
    }
    
    if (batchCertificates.value.fastest) {
      // Find racer with fastest time
      const fastestRacer = results.reduce((fastest, current) => {
        if (!fastest || (current.fastest_time && (!fastest.fastest_time || current.fastest_time < fastest.fastest_time))) {
          return current
        }
        return fastest
      }, null as RacerResult | null)
      
      if (fastestRacer) {
        await reportService.generateCertificate({
          race_id: raceId,
          racer_id: fastestRacer.racer_id,
          award_type: 'speed'
        })
      }
    }
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Certificates generated', 
      life: 3000 
    })
    
    batchCertificatesDialog.value = false
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to generate certificates', 
      life: 3000 
    })
  } finally {
    generatingCertificate.value = false
  }
}

function printStandings() {
  window.print()
}

function printRaceResults() {
  window.print()
}

async function generateCertificate(params: AwardCertificateParams) {
  try {
    const blob = await reportService.generateCertificate(params)
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `certificate.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Certificate generated', 
      life: 3000 
    })
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to generate certificate', 
      life: 3000 
    })
  }
}
</script>

<style scoped>
.reports-container {
  max-width: 1200px;
  margin: 0 auto;
}

.reports-header {
  margin-bottom: 1.5rem;
}

.tab-content {
  min-height: 400px;
  padding: 1rem 0;
}

.center-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.empty-message {
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-message i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.race-selection {
  margin-bottom: 2rem;
}

.race-report-header {
  margin-bottom: 1rem;
}

.race-metadata {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin: 0.5rem 0 1rem;
}

.completed-date {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
}

.race-report-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.position-cell {
  display: flex;
  align-items: center;
}

.position-badge {
  display: inline-block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  border-radius: 50%;
  font-weight: bold;
}

.position-first {
  background-color: gold;
  color: #333;
}

.position-second {
  background-color: silver;
  color: #333;
}

.position-third {
  background-color: #cd7f32;
  color: white;
}

.position-other {
  background-color: #e9ecef;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.racer-info-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.racer-info-section h3 {
  margin: 0 0 0.5rem 0;
}

.racer-info-section p {
  margin: 0;
  color: var(--text-color-secondary);
}
</style>