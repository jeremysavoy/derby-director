<template>
    <MainLayout>
      <div class="racer-detail-container" v-if="racer">
        <div class="back-link">
          <Button
            icon="pi pi-arrow-left"
            label="Back to Racers"
            class="p-button-text"
            @click="router.push('/racers')"
          />
        </div>
        
        <div class="racer-header">
          <div class="racer-info">
            <h1>{{ racer.first_name }} {{ racer.last_name }}</h1>
            <div class="racer-metadata">
              <Tag :value="'Car #' + racer.car_number" />
              <Chip :label="racer.rank" />
              <Tag v-if="racer.den" :value="racer.den" severity="info" />
              <Tag :value="formatStatus(racer.checkin_status)" :severity="getStatusSeverity(racer.checkin_status)" />
            </div>
          </div>
          
          <div class="racer-actions">
            <Button
              icon="pi pi-pencil"
              label="Edit Racer"
              @click="editRacer"
            />
            <Button
              icon="pi pi-camera"
              label="Photo"
              class="p-button-outlined"
              @click="openPhotoDialog"
            />
            <Button
              icon="pi pi-file"
              label="Certificate"
              class="p-button-outlined"
              @click="openCertificateDialog"
            />
          </div>
        </div>
        
        <div class="racer-details grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #header>
                <h2 class="card-header">Racer Details</h2>
              </template>
              <template #content>
                <div class="racer-photo" v-if="racer.photo_url">
                  <img :src="racer.photo_url" :alt="racer.first_name + ' ' + racer.last_name" />
                </div>
                <div class="details-list">
                  <div class="detail-item">
                    <div class="detail-label">First Name:</div>
                    <div class="detail-value">{{ racer.first_name }}</div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-label">Last Name:</div>
                    <div class="detail-value">{{ racer.last_name }}</div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-label">Car Number:</div>
                    <div class="detail-value">{{ racer.car_number }}</div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-label">Rank:</div>
                    <div class="detail-value">{{ racer.rank }}</div>
                  </div>
                  <div class="detail-item" v-if="racer.den">
                    <div class="detail-label">Den:</div>
                    <div class="detail-value">{{ racer.den }}</div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-label">Weight:</div>
                    <div class="detail-value">{{ racer.weight ? racer.weight.toFixed(2) + ' oz' : 'Not weighed' }}</div>
                  </div>
                  <div class="detail-item">
                    <div class="detail-label">Status:</div>
                    <div class="detail-value">
                      <Tag :value="formatStatus(racer.checkin_status)" :severity="getStatusSeverity(racer.checkin_status)" />
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-8">
            <Card>
              <template #header>
                <h2 class="card-header">Race History</h2>
              </template>
              <template #content>
                <div v-if="loadingHistory" class="center-content">
                  <ProgressSpinner />
                </div>
                <div v-else-if="!raceHistory.length" class="empty-history">
                  <i class="pi pi-flag-fill"></i>
                  <h3>No Race History</h3>
                  <p>This racer hasn't participated in any races yet.</p>
                </div>
                <div v-else>
                  <DataTable
                    :value="raceHistory"
                    responsive-layout="stack"
                    class="p-datatable-sm"
                  >
                    <Column field="race_name" header="Race" sortable />
                    <Column field="position" header="Position" sortable>
                      <template #body="{ data }">
                        <span class="position-badge" :class="getPositionClass(data.position)">
                          {{ data.position }}
                        </span>
                      </template>
                    </Column>
                    <Column field="fastest_time" header="Fastest Time" sortable>
                      <template #body="{ data }">
                        {{ data.fastest_time ? data.fastest_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                    <Column field="avg_time" header="Avg Time" sortable>
                      <template #body="{ data }">
                        {{ data.avg_time ? data.avg_time.toFixed(3) + 's' : '-' }}
                      </template>
                    </Column>
                    <Column field="race_date" header="Date" sortable>
                      <template #body="{ data }">
                        {{ formatDate(data.race_date) }}
                      </template>
                    </Column>
                    <Column header="Actions">
                      <template #body="{ data }">
                        <Button
                          icon="pi pi-eye"
                          class="p-button-rounded p-button-text p-button-sm"
                          @click="viewRaceResults(data.race_id)"
                          tooltip="View Race"
                        />
                      </template>
                    </Column>
                  </DataTable>
                  
                  <div class="stats-summary">
                    <h3>Performance Summary</h3>
                    <div class="stats-grid">
                      <div class="stat-card">
                        <div class="stat-value">{{ racerStats.totalRaces }}</div>
                        <div class="stat-label">Total Races</div>
                      </div>
                      <div class="stat-card">
                        <div class="stat-value">{{ racerStats.wins }}</div>
                        <div class="stat-label">1st Place Finishes</div>
                      </div>
                      <div class="stat-card">
                        <div class="stat-value">{{ racerStats.podiums }}</div>
                        <div class="stat-label">Podium Finishes</div>
                      </div>
                      <div class="stat-card">
                        <div class="stat-value">{{ racerStats.fastestTime ? racerStats.fastestTime.toFixed(3) + 's' : '-' }}</div>
                        <div class="stat-label">Fastest Time</div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </div>
      <div v-else class="loading-container">
        <ProgressSpinner />
      </div>
      
      <!-- Edit Racer Dialog -->
      <Dialog
        v-model:visible="editDialog"
        header="Edit Racer"
        :modal="true"
        class="p-fluid"
        :style="{width: '450px'}"
      >
        <div class="field">
          <label for="firstName">First Name</label>
          <InputText
            id="firstName"
            v-model="editedRacer.first_name"
            required
            autofocus
            :class="{'p-invalid': submitted && !editedRacer.first_name}"
          />
          <small class="p-error" v-if="submitted && !editedRacer.first_name">First Name is required.</small>
        </div>
        
        <div class="field">
          <label for="lastName">Last Name</label>
          <InputText
            id="lastName"
            v-model="editedRacer.last_name"
            required
            :class="{'p-invalid': submitted && !editedRacer.last_name}"
          />
          <small class="p-error" v-if="submitted && !editedRacer.last_name">Last Name is required.</small>
        </div>
        
        <div class="field">
          <label for="carNumber">Car Number</label>
          <InputText
            id="carNumber"
            v-model="editedRacer.car_number"
            required
            :class="{'p-invalid': submitted && !editedRacer.car_number}"
          />
          <small class="p-error" v-if="submitted && !editedRacer.car_number">Car Number is required.</small>
        </div>
        
        <div class="field">
          <label for="rank">Rank</label>
          <Dropdown
            id="rank"
            v-model="editedRacer.rank"
            :options="rankOptions"
            optionLabel="name"
            optionValue="value"
            placeholder="Select a Rank"
            required
            :class="{'p-invalid': submitted && !editedRacer.rank}"
          />
          <small class="p-error" v-if="submitted && !editedRacer.rank">Rank is required.</small>
        </div>
        
        <div class="field">
          <label for="den">Den (Optional)</label>
          <Dropdown
            id="den"
            v-model="editedRacer.den"
            :options="denOptions"
            optionLabel="name"
            optionValue="value"
            placeholder="Select a Den"
          />
        </div>
        
        <div class="field">
          <label for="weight">Weight (oz)</label>
          <InputNumber
            id="weight"
            v-model="editedRacer.weight"
            mode="decimal"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            placeholder="Enter weight"
          />
        </div>
        
        <div class="field">
          <label for="checkinStatus">Check-in Status</label>
          <Dropdown
            id="checkinStatus"
            v-model="editedRacer.checkin_status"
            :options="statusOptions"
            optionLabel="name"
            optionValue="value"
            placeholder="Select Status"
            required
          />
        </div>
        
        <template #footer>
          <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="editDialog = false" />
          <Button label="Save" icon="pi pi-check" class="p-button-primary" @click="saveRacer" :loading="saving" />
        </template>
      </Dialog>
      
      <!-- Photo Dialog -->
      <Dialog
        v-model:visible="photoDialog"
        header="Racer Photo"
        :modal="true"
        class="p-fluid"
        :style="{width: '450px'}"
      >
        <div class="photo-upload-container">
          <div v-if="racer && racer.photo_url" class="current-photo">
            <h3>Current Photo</h3>
            <img :src="racer.photo_url" alt="Racer photo" />
          </div>
          
          <div class="upload-section">
            <h3>Upload New Photo</h3>
            <FileUpload
              mode="basic"
              name="photo"
              accept="image/*"
              :maxFileSize="1000000"
              :auto="true"
              @select="onPhotoSelect"
              @upload="onPhotoUpload"
              @error="onPhotoError"
              :customUpload="true"
              chooseLabel="Select Photo"
            />
          </div>
        </div>
        
        <template #footer>
          <Button label="Close" icon="pi pi-times" class="p-button-text" @click="photoDialog = false" />
        </template>
      </Dialog>
      
      <!-- Certificate Dialog -->
      <Dialog
        v-model:visible="certificateDialog"
        header="Generate Certificate"
        :modal="true"
        class="p-fluid"
        :style="{width: '450px'}"
      >
        <div class="certificate-form">
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
              :options="racesForDropdown"
              optionLabel="name"
              optionValue="race_id"
              placeholder="Select Race"
            />
          </div>
        </div>
        
        <template #footer>
          <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="certificateDialog = false" />
          <Button label="Generate" icon="pi pi-file" class="p-button-primary" @click="generateCertificate" :loading="generatingCertificate" />
        </template>
      </Dialog>
    </MainLayout>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useToast } from 'primevue/usetoast'
  import MainLayout from '../../layouts/MainLayout.vue'
  import Card from 'primevue/card'
  import DataTable from 'primevue/datatable'
  import Column from 'primevue/column'
  import ProgressSpinner from 'primevue/progressspinner'
  import Tag from 'primevue/tag'
  import Chip from 'primevue/chip'
  import Dialog from 'primevue/dialog'
  import Dropdown from 'primevue/dropdown'
  import InputNumber from 'primevue/inputnumber'
  import InputText from 'primevue/inputtext'
  import Textarea from 'primevue/textarea'
  import FileUpload from 'primevue/fileupload'
  import racerService from '../../services/racer.service'
  import reportService from '../../services/report.service'
  import type { AwardCertificateParams } from '../../services/report.service'
  
  // Initialize services
  const route = useRoute()
  const router = useRouter()
  const toast = useToast()
  
  // Racer data
  const racer = ref<any>(null)
  const raceHistory = ref<any[]>([])
  const loadingHistory = ref(true)
  
  // Edit dialog
  const editDialog = ref(false)
  const editedRacer = ref<any>({})
  const submitted = ref(false)
  const saving = ref(false)
  
  // Photo dialog
  const photoDialog = ref(false)
  
  // Certificate dialog
  const certificateDialog = ref(false)
  const certificateParams = ref<AwardCertificateParams>({
    award_type: 'participant',
    title: '',
    description: ''
  })
  const generatingCertificate = ref(false)
  
  // Options
  const rankOptions = [
    { name: 'Lion', value: 'Lion' },
    { name: 'Tiger', value: 'Tiger' },
    { name: 'Wolf', value: 'Wolf' },
    { name: 'Bear', value: 'Bear' },
    { name: 'Webelos', value: 'Webelos' },
    { name: 'Arrow of Light', value: 'Arrow of Light' }
  ]
  
  const denOptions = [
    { name: 'Den 1', value: 'Den 1' },
    { name: 'Den 2', value: 'Den 2' },
    { name: 'Den 3', value: 'Den 3' },
    { name: 'Den 4', value: 'Den 4' },
    { name: 'Den 5', value: 'Den 5' }
  ]
  
  const statusOptions = [
    { name: 'Registered', value: 'registered' },
    { name: 'Checked In', value: 'checked_in' },
    { name: 'Passed Inspection', value: 'passed_inspection' }
  ]
  
  const certificateTypes = [
    { name: 'Race Winner', value: 'winner' },
    { name: 'Participation', value: 'participant' },
    { name: 'Speed Award', value: 'speed' },
    { name: 'Design Award', value: 'design' },
    { name: 'Custom Award', value: 'custom' }
  ]
  
  // Computed properties
  const racerStats = computed(() => {
    if (!raceHistory.value.length) {
      return {
        totalRaces: 0,
        wins: 0,
        podiums: 0,
        fastestTime: null
      }
    }
    
    const totalRaces = raceHistory.value.length
    const wins = raceHistory.value.filter(race => race.position === 1).length
    const podiums = raceHistory.value.filter(race => race.position <= 3).length
    
    // Find fastest time
    let fastestTime = null
    for (const race of raceHistory.value) {
      if (race.fastest_time) {
        if (fastestTime === null || race.fastest_time < fastestTime) {
          fastestTime = race.fastest_time
        }
      }
    }
    
    return {
      totalRaces,
      wins,
      podiums,
      fastestTime
    }
  })
  
  const racesForDropdown = computed(() => {
    return raceHistory.value.map(race => ({
      name: race.race_name,
      race_id: race.race_id
    }))
  })
  
  // Load racer data on component mount
  onMounted(async () => {
    const racerId = parseInt(route.params.id as string)
    if (isNaN(racerId)) {
      router.push('/racers')
      return
    }
  
    try {
      // Load racer
      const racerData = await racerService.getRacer(racerId)
      racer.value = racerData
      
      // Load race history
      await loadRacerHistory(racerId)
    } catch (error) {
      console.error('Error loading racer data', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load racer data', 
        life: 3000 
      })
      router.push('/racers')
    }
  })
  
  async function loadRacerHistory(racerId: number) {
    try {
      loadingHistory.value = true
      const historyData = await reportService.getRacerHistory(racerId)
      raceHistory.value = historyData
    } catch (error) {
      console.error('Error loading race history', error)
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to load race history', 
        life: 3000 
      })
    } finally {
      loadingHistory.value = false
    }
  }
  
  // Formatting functions
  function formatStatus(status: string) {
    switch (status) {
      case 'registered':
        return 'Registered'
      case 'checked_in':
        return 'Checked In'
      case 'passed_inspection':
        return 'Passed Inspection'
      default:
        return 'Unknown'
    }
  }
  
  function getStatusSeverity(status: string) {
    switch (status) {
      case 'registered':
        return 'warning'
      case 'checked_in':
        return 'info'
      case 'passed_inspection':
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
  
  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString()
  }
  
  // Actions
  function editRacer() {
    if (!racer.value) return
    
    editedRacer.value = { ...racer.value }
    submitted.value = false
    editDialog.value = true
  }
  
  async function saveRacer() {
    submitted.value = true
    
    if (!editedRacer.value.first_name || !editedRacer.value.last_name || !editedRacer.value.car_number || !editedRacer.value.rank) {
      return
    }
    
    saving.value = true
    
    try {
      await racerService.updateRacer(editedRacer.value.id, editedRacer.value)
      
      // Update racer data
      racer.value = { ...editedRacer.value }
      
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Racer updated', 
        life: 3000 
      })
      
      // Close dialog
      editDialog.value = false
    } catch (error: any) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: error.message || 'Failed to update racer', 
        life: 3000 
      })
    } finally {
      saving.value = false
    }
  }
  
  function openPhotoDialog() {
    photoDialog.value = true
  }
  
  function onPhotoSelect(event: any) {
    // Handle photo selection
    console.log('Photo selected', event)
  }
  
  async function onPhotoUpload(event: any) {
    if (!racer.value) return
    
    try {
      const file = event.files[0]
      await racerService.uploadPhoto(racer.value.id, file)
      
      // Refresh racer data to get updated photo URL
      const updatedRacer = await racerService.getRacer(racer.value.id)
      racer.value = updatedRacer
      
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Photo uploaded', 
        life: 3000 
      })
    } catch (error) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: 'Failed to upload photo', 
        life: 3000 
      })
    }
  }
  
  function onPhotoError(event: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: event.message || 'Failed to upload photo', 
      life: 3000 
    })
  }
  
  function openCertificateDialog() {
    certificateParams.value = {
      racer_id: racer.value.id,
      award_type: 'participant',
      title: '',
      description: ''
    }
    
    certificateDialog.value = true
  }
  
  async function generateCertificate() {
    if (!racer.value) return
    
    generatingCertificate.value = true
    
    try {
      const blob = await reportService.generateCertificate({
        ...certificateParams.value,
        racer_id: racer.value.id
      })
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `certificate_${racer.value.first_name}_${racer.value.last_name}.pdf`
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
  
  function viewRaceResults(raceId: number) {
    router.push(`/reports?raceId=${raceId}`)
  }
  </script>
  
  <style scoped>
  .racer-detail-container {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .back-link {
    margin-bottom: 1rem;
  }
  
  .racer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  
  .racer-metadata {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-top: 0.5rem;
  }
  
  .racer-actions {
    display: flex;
    gap: 0.75rem;
  }
  
  .racer-details {
    margin-bottom: 2rem;
  }
  
  .card-header {
    margin: 0;
    padding: 1rem;
    font-size: 1.25rem;
  }
  
  .racer-photo {
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .racer-photo img {
    max-width: 100%;
    max-height: 300px;
    object-fit: contain;
    border-radius: 4px;
  }
  
  .details-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .detail-item {
    display: flex;
  }
  
  .detail-label {
    font-weight: 600;
    min-width: 100px;
  }
  
  .center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }
  
  .empty-history {
    text-align: center;
    padding: 2rem 0;
    color: var(--text-color-secondary);
  }
  
  .empty-history i {
    font-size: 3rem;
    margin-bottom: 1rem;
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
  
  .stats-summary {
    margin-top: 2rem;
  }
  
  .stats-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .stat-card {
    flex: 1;
    min-width: 150px;
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 1rem;
    text-align: center;
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
    margin-top: 0.5rem;
  }
  
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 400px;
  }
  
  .photo-upload-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .current-photo {
    text-align: center;
  }
  
  .current-photo img {
    max-width: 100%;
    max-height: 300px;
    object-fit: contain;
    border-radius: 4px;
  }
  
  .upload-section {
    margin-top: 1rem;
  }
  </style>