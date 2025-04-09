<template>
    <MainLayout>
      <div class="race-detail-container" v-if="race">
        <div class="race-header">
          <div class="race-info">
            <h1>{{ race.name }}</h1>
            <div class="race-metadata">
              <Tag :value="formatRaceType(race.race_type)" severity="info" />
              <Tag :value="formatStatus(race.status)" :severity="getStatusSeverity(race.status)" />
              <span class="heat-progress">
                Heats: {{ race.completed_heats }}/{{ race.total_heats }}
              </span>
            </div>
          </div>
          <div class="race-actions">
            <Button 
              v-if="race.status === 'pending'"
              label="Start Race" 
              icon="pi pi-play" 
              @click="startRace"
              :disabled="!race.total_heats"
            />
            <Button 
              v-if="race.status === 'in_progress'"
              label="Complete Race" 
              icon="pi pi-check" 
              @click="completeRace"
            />
            <Button 
              v-if="race.status === 'pending' && !race.total_heats"
              label="Generate Heats" 
              icon="pi pi-refresh" 
              @click="generateHeats"
            />
            <Button 
              icon="pi pi-print" 
              label="Print Results" 
              class="p-button-outlined"
              v-if="race.status === 'completed'"
              @click="printResults"
            />
          </div>
        </div>
  
        <div class="race-tabs">
          <TabView>
            <TabPanel header="Heats" value="heats">
              <div class="tab-content">
                <div v-if="loading" class="center-content">
                  <ProgressSpinner />
                </div>
                <div v-else-if="heats.length === 0" class="center-content">
                  <div class="empty-message">
                    <i class="pi pi-flag-fill"></i>
                    <h3>No Heats Available</h3>
                    <p v-if="race.status === 'pending'">Click "Generate Heats" to create heats for this race.</p>
                  </div>
                </div>
                <div v-else class="heats-list">
                  <DataTable 
                    :value="heats" 
                    responsive-layout="stack"
                    class="p-datatable-sm"
                  >
                    <Column field="heat_number" header="Heat #" :sortable="true" />
                    <Column header="Status">
                      <template #body="{ data }">
                        <Tag :value="formatHeatStatus(data.status)" :severity="getHeatStatusSeverity(data.status)" />
                      </template>
                    </Column>
                    <Column header="Racers">
                      <template #body="{ data }">
                        <div class="heat-racers">
                          <div v-for="lane in data.lanes" :key="lane.id" class="heat-lane">
                            <span class="lane-number">Lane {{ lane.lane_number }}:</span>
                            <Chip :label="`#${lane.car_number}: ${lane.racer_name}`" />
                            <span v-if="lane.finish_position" class="position-badge" :class="getPositionClass(lane.finish_position)">
                              {{ getPositionText(lane.finish_position) }}
                            </span>
                            <Tag v-if="lane.dnf" severity="danger" value="DNF" />
                          </div>
                        </div>
                      </template>
                    </Column>
                    <Column header="Actions">
                      <template #body="{ data }">
                        <div class="action-buttons">
                          <Button 
                            v-if="data.status === 'pending' && race.status === 'in_progress'"
                            icon="pi pi-play" 
                            class="p-button-rounded p-button-sm" 
                            @click="startHeat(data)"
                            tooltip="Start Heat"
                          />
                          <Button 
                            v-if="data.status === 'in_progress'"
                            icon="pi pi-check" 
                            class="p-button-rounded p-button-success p-button-sm" 
                            @click="openResultsDialog(data)"
                            tooltip="Record Results"
                          />
                          <Button 
                            v-if="data.status === 'completed'"
                            icon="pi pi-eye" 
                            class="p-button-rounded p-button-info p-button-sm" 
                            @click="viewHeatResults(data)"
                            tooltip="View Results"
                          />
                        </div>
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
            </TabPanel>
            <TabPanel header="Results" value="results">
              <div class="tab-content">
                <div v-if="loadingResults" class="center-content">
                  <ProgressSpinner />
                </div>
                <div v-else-if="!results.length" class="center-content">
                  <div class="empty-message">
                    <i class="pi pi-chart-bar"></i>
                    <h3>No Results Available</h3>
                    <p>Complete some heats to see results here.</p>
                  </div>
                </div>
                <div v-else class="results-container">
                  <div class="results-header">
                    <h2>Race Results</h2>
                  </div>
                  <DataTable 
                    :value="results" 
                    responsive-layout="stack"
                    class="p-datatable-sm"
                  >
                    <Column field="position" header="Position" :sortable="true">
                      <template #body="{ data }">
                        <span>{{ data.dnf ? '-' : data.position }}</span>
                      </template>
                    </Column>>
                    <Column field="car_number" header="Car #" :sortable="true" />
                    <Column field="racer_name" header="Racer" :sortable="true" />
                    <Column field="points" header="Points" :sortable="true" />
                    <Column field="avg_time" header="Avg Time" :sortable="true">
                      <template #body="{ data }">
                        {{ data.avg_time ? data.avg_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                    <Column field="fastest_time" header="Fastest" :sortable="true">
                      <template #body="{ data }">
                        {{ data.fastest_time ? data.fastest_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </div>
      <div v-else class="loading-container">
        <ProgressSpinner />
      </div>
  
      <!-- Heat Results Dialog -->
      <Dialog 
        v-model:visible="resultsDialog" 
        header="Record Heat Results" 
        :modal="true" 
        class="p-fluid"
        :style="{width: '500px'}"
      >
        <div v-if="selectedHeat" class="heat-results-form">
          <div v-for="lane in heatResults.lanes" :key="lane.lane_id" class="lane-result">
            <div class="lane-header">
              <h3>Lane {{ lane.lane_number }}</h3>
              <div class="racer-info">
                {{ lane.racer_name }} (Car #{{ lane.car_number }})
              </div>
            </div>
            
            <div class="field-checkbox">
              <Checkbox 
                :id="'dnf-' + lane.lane_id" 
                v-model="lane.dnf" 
                :binary="true" 
                @change="handleDnfChange(lane)"
              />
              <label :for="'dnf-' + lane.lane_id">Did Not Finish (DNF)</label>
            </div>
            
            <div class="result-fields" v-if="!lane.dnf">
              <div class="field">
                <label :for="'position-' + lane.lane_id">Finish Position</label>
                <Dropdown 
                  :id="'position-' + lane.lane_id" 
                  v-model="lane.finish_position" 
                  :options="positionOptions" 
                  placeholder="Select Position" 
                  :class="{'p-invalid': submitted && !lane.dnf && !lane.finish_position}" 
                />
                <small class="p-error" v-if="submitted && !lane.dnf && !lane.finish_position">Position is required.</small>
              </div>
              
              <div class="field">
                <label :for="'time-' + lane.lane_id">Finish Time (seconds)</label>
                <InputNumber 
                  :id="'time-' + lane.lane_id" 
                  v-model="lane.finish_time" 
                  mode="decimal" 
                  :minFractionDigits="3" 
                  :maxFractionDigits="3"
                  placeholder="Enter time" 
                  :class="{'p-invalid': submitted && !lane.dnf && !lane.finish_time}" 
                />
                <small class="p-error" v-if="submitted && !lane.dnf && !lane.finish_time">Time is required.</small>
              </div>
            </div>
          </div>
        </div>
        
        <template #footer>
          <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideResultsDialog" />
          <Button label="Save Results" icon="pi pi-check" class="p-button-primary" @click="saveHeatResults" :loading="savingResults" />
        </template>
      </Dialog>
  
      <!-- Heat Results View Dialog -->
      <Dialog 
        v-model:visible="viewResultsDialog" 
        header="Heat Results" 
        :modal="true" 
        class="p-fluid"
        :style="{width: '500px'}"
      >
        <div v-if="selectedHeat" class="heat-results-view">
          <DataTable :value="selectedHeatResults" class="p-datatable-sm">
            <Column field="position" header="Position">
              <template #body="{ data }">
                <span>{{ data.dnf ? '-' : data.position }}</span>
              </template>
            </Column>/>
            <Column field="lane" header="Lane" />
            <Column field="racer" header="Racer" />
            <Column field="time" header="Time">
              <template #body="{ data }">
                <span v-if="data.dnf">DNF</span>
                <span v-else>{{ data.time.toFixed(3) }}s</span>
              </template>
            </Column>
          </DataTable>
        </div>
        
        <template #footer>
          <Button label="Close" icon="pi pi-times" class="p-button-text" @click="viewResultsDialog = false" />
        </template>
      </Dialog>
    </MainLayout>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useToast } from 'primevue/usetoast'
  import MainLayout from '../../layouts/MainLayout.vue'
  import TabView from 'primevue/tabview'
  import TabPanel from 'primevue/tabpanel'
  import DataTable from 'primevue/datatable'
  import Column from 'primevue/column'
  import ProgressSpinner from 'primevue/progressspinner'
  import Tag from 'primevue/tag'
  import Chip from 'primevue/chip'
  import Dialog from 'primevue/dialog'
  import Checkbox from 'primevue/checkbox'
  import Dropdown from 'primevue/dropdown'
  import InputNumber from 'primevue/inputnumber'
  import raceService from '../../services/race.service'
  import type { Race, Heat, HeatResultDto } from '../../types'
  
  // Initialize services
  const route = useRoute()
  const router = useRouter()
  const toast = useToast()
  
  // Race data
  const race = ref<Race | null>(null)
  const heats = ref<Heat[]>([])
  const results = ref<any[]>([])
  const loading = ref(true)
  const loadingResults = ref(true)
  
  // Heat results dialog
  const resultsDialog = ref(false)
  const selectedHeat = ref<Heat | null>(null)
  const heatResults = ref<HeatResultDto>({
    heat_id: 0,
    lanes: []
  })
  const submitted = ref(false)
  const savingResults = ref(false)
  
  // View results dialog
  const viewResultsDialog = ref(false)
  const selectedHeatResults = ref<any[]>([])
  
  // Position options for dropdown
  const positionOptions = [1, 2, 3, 4, 5, 6, 7, 8]
  
  // Load race data on component mount
  onMounted(async () => {
    const raceId = parseInt(route.params.id as string)
    if (isNaN(raceId)) {
      router.push('/races')
      return
    }
  
    try {
      // Load race
      const raceData = await raceService.getRace(raceId)
      race.value = raceData
      
      // Load heats
      await loadHeats(raceId)
      
      // Load results if race is in progress or completed
      if (!race.value) return
      else if (race.value.status !== 'pending') {
        await loadResults(raceId)
      }
    } catch (error) {
      console.error('Error loading race data', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load race data', 
        life: 3000 
      })
      router.push('/races')
    } finally {
      loading.value = false
    }
  })
  
  async function loadHeats(raceId: number) {
    try {
      loading.value = true
      const heatsData = await raceService.getHeats(raceId)
      heats.value = heatsData
    } catch (error) {
      console.error('Error loading heats', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load heats', 
        life: 3000 
      })
    } finally {
      loading.value = false
    }
  }
  
  async function loadResults(raceId: number) {
    try {
      loadingResults.value = true
      const resultsData = await raceService.getRaceResults(raceId)
      results.value = resultsData
    } catch (error) {
      console.error('Error loading results', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load results', 
        life: 3000 
      })
    } finally {
      loadingResults.value = false
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
  
  function formatHeatStatus(status: string) {
    switch (status) {
      case 'pending':
        return 'Pending'
      case 'in_progress':
        return 'Running'
      case 'completed':
        return 'Completed'
      default:
        return 'Unknown'
    }
  }
  
  function getHeatStatusSeverity(status: string) {
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
  
  function getPositionText(position: number) {
    switch (position) {
      case 1:
        return '1st'
      case 2:
        return '2nd'
      case 3:
        return '3rd'
      default:
        return `${position}th`
    }
  }
  
  // Race actions
  async function startRace() {
    if (!race.value) return
    
    try {
      const updatedRace = await raceService.startRace(race.value.id)
      race.value = updatedRace
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Race started successfully', 
        life: 3000 
      })
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to start race', 
        life: 3000 
      })
    }
  }
  
  async function completeRace() {
    if (!race.value) return
    
    try {
      const updatedRace = await raceService.completeRace(race.value.id)
      race.value = updatedRace
      if (!race.value) return
      else await loadResults(race.value.id)
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Race completed successfully', 
        life: 3000 
      })
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to complete race', 
        life: 3000 
      })
    }
  }
  
  async function generateHeats() {
    if (!race.value) return
    
    try {
      await raceService.generateHeats(race.value.id)
      // Reload race and heats
      const updatedRace = await raceService.getRace(race.value.id)
      race.value = updatedRace
      if (!race.value) return
      else await loadHeats(race.value.id)
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Heats generated successfully', 
        life: 3000 
      })
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to generate heats', 
        life: 3000 
      })
    }
  }
  
  function printResults() {
    // Implementation for printing results
    window.print()
  }
  
  // Heat actions
  async function startHeat(heat: Heat) {
    try {
      const updatedHeat = await raceService.startHeat(heat.id)
      // Update heat in list
      const index = heats.value.findIndex(h => h.id === heat.id)
      if (index !== -1) {
        heats.value[index] = updatedHeat
      }
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: `Heat ${heat.heat_number} started`, 
        life: 3000 
      })
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to start heat', 
        life: 3000 
      })
    }
  }
  
  function openResultsDialog(heat: Heat) {
    selectedHeat.value = heat
    
    // Initialize heat results form
    heatResults.value = {
      heat_id: heat.id,
      lanes: heat.lanes.map(lane => ({
        lane_id: lane.id,
        lane_number: lane.lane_number,
        racer_name: lane.racer_name,  // Not part of the API but useful for UI
        car_number: lane.car_number,  // Not part of the API but useful for UI
        finish_position: lane.finish_position || undefined,
        finish_time: lane.finish_time || undefined,
        dnf: lane.dnf
      }))
    }
    
    submitted.value = false
    resultsDialog.value = true
  }
  
  function hideResultsDialog() {
    resultsDialog.value = false
    selectedHeat.value = null
  }
  
  function handleDnfChange(lane: any) {
    if (lane.dnf) {
      lane.finish_position = undefined
      lane.finish_time = undefined
    }
  }
  
  async function saveHeatResults() {
    submitted.value = true
    
    // Validate form
    let valid = true
    for (const lane of heatResults.value.lanes) {
      if (!lane.dnf && (!lane.finish_position || !lane.finish_time)) {
        valid = false
        break
      }
    }
    
    if (!valid) return
    
    savingResults.value = true
    
    try {
      // Clean up the data before sending
      const dataToSubmit = {
        heat_id: heatResults.value.heat_id,
        lanes: heatResults.value.lanes.map(lane => ({
          lane_id: lane.lane_id,
          finish_position: lane.finish_position,
          finish_time: lane.finish_time,
          dnf: lane.dnf
        }))
      }
      
      await raceService.submitHeatResults(dataToSubmit)
      
      // Reload heats and results
      if (race.value) {
        await loadHeats(race.value.id)
        await loadResults(race.value.id)
      }
      
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Heat results saved', 
        life: 3000 
      })
      
      resultsDialog.value = false
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to save heat results', 
        life: 3000 
      })
    } finally {
      savingResults.value = false
    }
  }
  
  function viewHeatResults(heat: Heat) {
    selectedHeat.value = heat
    
    // Format heat results for display
    selectedHeatResults.value = heat.lanes
      .filter(lane => !lane.dnf || lane.finish_position)
      .map(lane => ({
        //position: lane.dnf ? '-' : lane.finish_position,
        position: lane.finish_position ?? 999,
        lane: lane.lane_number,
        racer: `${lane.racer_name} (#${lane.car_number})`,
        time: lane.finish_time,
        dnf: lane.dnf
      }))
      .sort((a, b) => {
        if (a.dnf && !b.dnf) return 1
        if (!a.dnf && b.dnf) return -1
        if (a.dnf && b.dnf) return 0
        return a.position - b.position
      })
    
    viewResultsDialog.value = true
  }
  </script>
  
  <style scoped>
  .race-detail-container {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .race-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  
  .race-metadata {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-top: 0.5rem;
  }
  
  .heat-progress {
    font-size: 0.9rem;
    color: var(--text-color-secondary);
  }
  
  .race-actions {
    display: flex;
    gap: 0.75rem;
  }
  
  .race-tabs {
    margin-top: 1rem;
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
  
  .heat-racers {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .heat-lane {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .lane-number {
    font-weight: 500;
    min-width: 70px;
  }
  
  .position-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.8rem;
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
  
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 400px;
  }
  
  .heat-results-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .lane-result {
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1rem;
  }
  
  .lane-header {
    margin-bottom: 1rem;
  }
  
  .lane-header h3 {
    margin: 0;
    font-size: 1.1rem;
  }
  
  .racer-info {
    color: var(--text-color-secondary);
    font-size: 0.9rem;
  }
  
  .result-fields {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .results-header {
    margin-bottom: 1rem;
  }
  </style>