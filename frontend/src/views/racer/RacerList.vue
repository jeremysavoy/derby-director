<template>
  <MainLayout>
    <div class="racer-list-container">
      <div class="header-with-actions">
        <h1>Racers</h1>
        <div class="action-buttons">
          <Button 
            label="Add Racer" 
            icon="pi pi-plus" 
            @click="openNewRacerDialog" 
            v-if="hasPermission('racers:create')"
          />
        </div>
      </div>

      <div class="card">
        <DataTable 
          :value="racers" 
          :loading="loading" 
          responsive-layout="stack"
          :paginator="true" 
          :rows="10"
          stripedRows
          class="p-datatable-sm"
          :filters="filters"
          filterDisplay="menu"
        >
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3 class="m-0">Registered Racers</h3>
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Search..." />
              </span>
            </div>
          </template>

          <Column field="car_number" header="Car #" sortable />
          <Column field="first_name" header="First Name" sortable />
          <Column field="last_name" header="Last Name" sortable />
          <Column field="rank" header="Rank" sortable>
            <template #body="{ data }">
              <Chip :label="data.rank" />
            </template>
          </Column>
          <Column field="weight" header="Weight" sortable>
            <template #body="{ data }">
              {{ data.weight ? `${data.weight.toFixed(2)} oz` : 'Not weighed' }}
            </template>
          </Column>
          <Column field="checkin_status" header="Status" sortable>
            <template #body="{ data }">
              <Tag 
                :value="formatStatus(data.checkin_status)" 
                :severity="getStatusSeverity(data.checkin_status)" 
              />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-sm" 
                  @click="editRacer(data)" 
                  v-if="hasPermission('racers:update')"
                  tooltip="Edit"
                  tooltipOptions="top"
                />
                <Button 
                  icon="pi pi-camera" 
                  class="p-button-rounded p-button-text p-button-sm" 
                  @click="openPhotoDialog(data)" 
                  v-if="hasPermission('racers:update')"
                  tooltip="Photo"
                  tooltipOptions="top"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-rounded p-button-text p-button-danger p-button-sm" 
                  @click="confirmDeleteRacer(data)" 
                  v-if="hasPermission('racers:delete')"
                  tooltip="Delete"
                  tooltipOptions="top"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Racer Form Dialog -->
    <Dialog 
      v-model:visible="racerDialog" 
      :header="editMode ? 'Edit Racer' : 'Add Racer'" 
      :modal="true" 
      class="p-fluid"
      :style="{width: '450px'}"
    >
      <div class="field">
        <label for="firstName">First Name</label>
        <InputText 
          id="firstName" 
          v-model="racer.first_name" 
          required 
          autofocus 
          :class="{'p-invalid': submitted && !racer.first_name}" 
        />
        <small class="p-error" v-if="submitted && !racer.first_name">First Name is required.</small>
      </div>
      
      <div class="field">
        <label for="lastName">Last Name</label>
        <InputText 
          id="lastName" 
          v-model="racer.last_name" 
          required 
          :class="{'p-invalid': submitted && !racer.last_name}" 
        />
        <small class="p-error" v-if="submitted && !racer.last_name">Last Name is required.</small>
      </div>
      
      <div class="field">
        <label for="carNumber">Car Number</label>
        <InputText 
          id="carNumber" 
          v-model="racer.car_number" 
          required 
          :class="{'p-invalid': submitted && !racer.car_number}" 
        />
        <small class="p-error" v-if="submitted && !racer.car_number">Car Number is required.</small>
      </div>
      
      <div class="field">
        <label for="rank">Rank</label>
        <Dropdown 
          id="rank" 
          v-model="racer.rank" 
          :options="rankOptions" 
          optionLabel="name" 
          optionValue="value"
          placeholder="Select a Rank" 
          required 
          :class="{'p-invalid': submitted && !racer.rank}" 
        />
        <small class="p-error" v-if="submitted && !racer.rank">Rank is required.</small>
      </div>
      
      <div class="field">
        <label for="den">Den (Optional)</label>
        <Dropdown 
          id="den" 
          v-model="racer.den" 
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
          v-model="racer.weight" 
          mode="decimal" 
          :minFractionDigits="2" 
          :maxFractionDigits="2"
          placeholder="Enter weight" 
        />
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" class="p-button-primary" @click="saveRacer" :loading="saving" />
      </template>
    </Dialog>

    <!-- Photo Upload Dialog -->
    <Dialog 
      v-model:visible="photoDialog" 
      header="Racer Photo" 
      :modal="true" 
      class="p-fluid"
      :style="{width: '450px'}"
    >
      <div class="photo-upload-container">
        <div v-if="selectedRacer && selectedRacer.photo_url" class="current-photo">
          <h3>Current Photo</h3>
          <img :src="selectedRacer.photo_url" alt="Racer photo" />
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

    <!-- Delete Confirmation -->
    <ConfirmDialog></ConfirmDialog>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import MainLayout from '../../layouts/MainLayout.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import FileUpload from 'primevue/fileupload'
import racerService from '../../services/racer.service'
import type { Racer } from '../../services/racer.service'
import type { RacerCreateDto } from '../../services/racer.service'
import { useAuthStore } from '../../stores/auth'

// Initialize services
const confirm = useConfirm()
const toast = useToast()
const authStore = useAuthStore()

// Racer list state
const racers = ref<Racer[]>([])
const loading = ref(true)
const filters = ref({
  global: { value: null, matchMode: 'contains' }
})

// Form state
const racerDialog = ref(false)
const photoDialog = ref(false)
const editMode = ref(false)
const submitted = ref(false)
const saving = ref(false)
const racer = reactive<RacerCreateDto>({
  first_name: '',
  last_name: '',
  car_number: '',
  rank: '',
  weight: undefined,
  den: undefined,
  group_id: undefined
})
const selectedRacer = ref<Racer | null>(null)

// Options for dropdowns
const rankOptions = ref([
  { name: 'Lion', value: 'Lion' },
  { name: 'Tiger', value: 'Tiger' },
  { name: 'Wolf', value: 'Wolf' },
  { name: 'Bear', value: 'Bear' },
  { name: 'Webelos', value: 'Webelos' },
  { name: 'Arrow of Light', value: 'Arrow of Light' }
])

const denOptions = ref([
  { name: 'Den 1', value: 'Den 1' },
  { name: 'Den 2', value: 'Den 2' },
  { name: 'Den 3', value: 'Den 3' },
  { name: 'Den 4', value: 'Den 4' },
  { name: 'Den 5', value: 'Den 5' }
])

// Load racers on component mount
onMounted(async () => {
  try {
    // Load racers
    const response = await racerService.getAllRacers()
    racers.value = response
    
    // Get rank options from API if available
    try {
      const rankResponse = await racerService.getRankOptions()
      if (rankResponse && rankResponse.length > 0) {
        rankOptions.value = rankResponse.map((rank: string) => ({
          name: rank,
          value: rank
        }))
      }
    } catch (error) {
      console.error('Could not load rank options, using defaults', error)
    }
    
    // Get den options from API if available
    try {
      const denResponse = await racerService.getDenOptions()
      if (denResponse && denResponse.length > 0) {
        denOptions.value = denResponse.map((den: string) => ({
          name: den,
          value: den
        }))
      }
    } catch (error) {
      console.error('Could not load den options, using defaults', error)
    }
  } catch (error) {
    console.error('Error loading racers', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load racers', life: 3000 })
  } finally {
    loading.value = false
  }
})

// Permission check
function hasPermission(permission: string) {
  return authStore.hasPermission(permission)
}

// Status formatting
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

// Dialog management
function openNewRacerDialog() {
  Object.assign(racer, {
    first_name: '',
    last_name: '',
    car_number: '',
    rank: '',
    weight: undefined,
    den: undefined,
    group_id: undefined
  })
  submitted.value = false
  editMode.value = false
  racerDialog.value = true
}

function editRacer(racerData: Racer) {
  editMode.value = true
  Object.assign(racer, {
    first_name: racerData.first_name,
    last_name: racerData.last_name,
    car_number: racerData.car_number,
    rank: racerData.rank,
    weight: racerData.weight,
    den: racerData.den,
    group_id: racerData.group_id
  })
  selectedRacer.value = racerData
  racerDialog.value = true
}

function hideDialog() {
  racerDialog.value = false
  submitted.value = false
}

// Save racer
async function saveRacer() {
  submitted.value = true
  
  if (!racer.first_name || !racer.last_name || !racer.car_number || !racer.rank) {
    return
  }
  
  saving.value = true
  
  try {
    if (editMode.value && selectedRacer.value) {
      // Update existing racer
      await racerService.updateRacer(selectedRacer.value.id, racer)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Racer updated', life: 3000 })
    } else {
      // Create new racer
      await racerService.createRacer(racer)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Racer created', life: 3000 })
    }
    
    // Refresh racer list
    const response = await racerService.getAllRacers()
    racers.value = response
    
    // Close dialog
    racerDialog.value = false
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: error.message || 'Failed to save racer', 
      life: 3000 
    })
  } finally {
    saving.value = false
  }
}

// Delete racer
function confirmDeleteRacer(racerData: Racer) {
  confirm.require({
    message: `Are you sure you want to delete ${racerData.first_name} ${racerData.last_name}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deleteRacer(racerData.id)
  })
}

async function deleteRacer(id: number) {
  try {
    await racerService.deleteRacer(id)
    racers.value = racers.value.filter(r => r.id !== id)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Racer deleted', life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete racer', life: 3000 })
  }
}

// Photo management
function openPhotoDialog(racerData: Racer) {
  selectedRacer.value = racerData
  photoDialog.value = true
}

function onPhotoSelect(event: any) {
  // Handle photo selection
  console.log('Photo selected', event)
}

async function onPhotoUpload(event: any) {
  if (!selectedRacer.value) return
  
  try {
    const file = event.files[0]
    await racerService.uploadPhoto(selectedRacer.value.id, file)
    
    // Refresh racer data to get updated photo URL
    const updatedRacer = await racerService.getRacer(selectedRacer.value.id)
    selectedRacer.value = updatedRacer
    
    // Update in the racers list
    const index = racers.value.findIndex(r => r.id === selectedRacer.value?.id)
    if (index !== -1) {
      racers.value[index] = updatedRacer
    }
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Photo uploaded', life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to upload photo', life: 3000 })
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
</script>

<style scoped>
.racer-list-container {
  max-width: 1200px;
  margin: 0 auto;
}

.header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.photo-upload-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.current-photo img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}
</style>