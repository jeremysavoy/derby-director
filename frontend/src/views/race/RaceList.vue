<template>
    <MainLayout>
      <div class="race-list-container">
        <div class="header-with-actions">
          <h1>Races</h1>
          <div class="action-buttons">
            <Button 
              label="Create Race" 
              icon="pi pi-plus" 
              @click="openNewRaceDialog" 
              v-if="hasPermission('races:create')"
            />
          </div>
        </div>
  
        <div class="card">
          <DataTable 
            :value="races" 
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
                <h3 class="m-0">Race Events</h3>
                <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText v-model="filters['global'].value" placeholder="Search..." />
                </span>
              </div>
            </template>
  
            <Column field="name" header="Race Name" sortable />
            <Column field="race_type" header="Type" sortable>
              <template #body="{ data }">
                <Chip :label="formatRaceType(data.race_type)" />
              </template>
            </Column>
            <Column field="status" header="Status" sortable>
              <template #body="{ data }">
                <Tag 
                  :value="formatStatus(data.status)" 
                  :severity="getStatusSeverity(data.status)" 
                />
              </template>
            </Column>
            <Column field="total_heats" header="Total Heats" sortable />
            <Column field="completed_heats" header="Completed" sortable>
              <template #body="{ data }">
                <ProgressBar 
                  :value="getCompletionPercentage(data)" 
                  :style="{ height: '8px' }" 
                  :class="{ 'completed': data.status === 'completed' }" 
                />
                <small>{{ data.completed_heats }} / {{ data.total_heats }}</small>
              </template>
            </Column>
            <Column field="created_at" header="Created" sortable>
              <template #body="{ data }">
                {{ formatDate(data.created_at) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="action-buttons">
                  <Button 
                    icon="pi pi-play" 
                    class="p-button-rounded p-button-text p-button-sm" 
                    @click="navigateToRaceDetail(data.id)" 
                    tooltip="Manage Race"
                    tooltipOptions="top"
                  />
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-rounded p-button-text p-button-sm" 
                    @click="editRace(data)" 
                    v-if="hasPermission('races:update') && data.status === 'pending'"
                    tooltip="Edit"
                    tooltipOptions="top"
                  />
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-rounded p-button-text p-button-danger p-button-sm" 
                    @click="confirmDeleteRace(data)" 
                    v-if="hasPermission('races:delete') && data.status === 'pending'"
                    tooltip="Delete"
                    tooltipOptions="top"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
  
      <!-- Race Form Dialog -->
      <Dialog 
        v-model:visible="raceDialog" 
        :header="editMode ? 'Edit Race' : 'Create Race'" 
        :modal="true" 
        class="p-fluid"
        :style="{width: '500px'}"
      >
        <div class="field">
          <label for="name">Race Name</label>
          <InputText 
            id="name" 
            v-model="race.name" 
            required 
            autofocus 
            :class="{'p-invalid': submitted && !race.name}" 
          />
          <small class="p-error" v-if="submitted && !race.name">Race Name is required.</small>
        </div>
        
        <div class="field">
          <label for="raceType">Race Type</label>
          <Dropdown 
            id="raceType" 
            v-model="race.race_type" 
            :options="raceTypes" 
            optionLabel="name" 
            optionValue="value"
            placeholder="Select Race Type" 
            required 
            :class="{'p-invalid': submitted && !race.race_type}" 
          />
          <small class="p-error" v-if="submitted && !race.race_type">Race Type is required.</small>
        </div>
        
        <div class="field">
          <label for="groupId">Group (Optional)</label>
          <Dropdown 
            id="groupId" 
            v-model="race.group_id" 
            :options="groupOptions" 
            optionLabel="name"
            optionValue="id" 
            placeholder="Select a Group" 
          />
        </div>
        
        <div class="field-checkbox">
          <Checkbox 
            id="includeAllRacers" 
            v-model="race.include_all_racers" 
            :binary="true" 
          />
          <label for="includeAllRacers">Include all eligible racers</label>
        </div>
        
        <div class="field" v-if="!race.include_all_racers">
          <label for="selectedRacers">Select Racers</label>
          <MultiSelect 
            id="selectedRacers" 
            v-model="race.selected_racer_ids" 
            :options="racersForSelection" 
            optionLabel="name" 
            optionValue="id"
            placeholder="Select Racers" 
            display="chip" 
          />
        </div>
        
        <template #footer>
          <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
          <Button label="Save" icon="pi pi-check" class="p-button-primary" @click="saveRace" :loading="saving" />
        </template>
      </Dialog>
  
      <!-- Delete Confirmation -->
      <ConfirmDialog></ConfirmDialog>
    </MainLayout>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, reactive, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useConfirm } from 'primevue/useconfirm'
  import { useToast } from 'primevue/usetoast'
  import MainLayout from '../../layouts/MainLayout.vue'
  import DataTable from 'primevue/datatable'
  import Column from 'primevue/column'
  import ProgressBar from 'primevue/progressbar'
  import Dialog from 'primevue/dialog'
  import Dropdown from 'primevue/dropdown'
  import MultiSelect from 'primevue/multiselect'
  import Checkbox from 'primevue/checkbox'
  import Tag from 'primevue/tag'
  import Chip from 'primevue/chip'
  import raceService from '../../services/race.service'
  import type { Race } from '../../services/race.service'
  import type { RaceCreateDto } from '../../services/race.service'
  import racerService from '../../services/racer.service'
  import { useAuthStore } from '../../stores/auth'
  
  // Initialize services
  const router = useRouter()
  const confirm = useConfirm()
  const toast = useToast()
  const authStore = useAuthStore()
  
  // Race list state
  const races = ref<Race[]>([])
  const loading = ref(true)
  const filters = ref({
    global: { value: null, matchMode: 'contains' }
  })
  
  // Form state
  const raceDialog = ref(false)
  const editMode = ref(false)
  const submitted = ref(false)
  const saving = ref(false)
  const race = reactive<RaceCreateDto>({
    name: '',
    race_type: 'round_robin',
    include_all_racers: true,
    selected_racer_ids: []
  })
  const selectedRace = ref<Race | null>(null)
  
  // Options for dropdowns
  const raceTypes = [
    { name: 'Round Robin', value: 'round_robin' },
    { name: 'Elimination', value: 'elimination' },
    { name: 'Custom', value: 'custom' }
  ]
  
  const groupOptions = ref([
    { name: 'All Ranks', id: null },
    { name: 'Lions', id: 1 },
    { name: 'Tigers', id: 2 },
    { name: 'Wolves', id: 3 },
    { name: 'Bears', id: 4 },
    { name: 'Webelos', id: 5 }
  ])
  
  const racersList = ref([])
  const racersForSelection = computed(() => {
    return racersList.value.map((racer: any) => ({
      id: racer.id,
      name: `${racer.car_number}: ${racer.first_name} ${racer.last_name}`
    }))
  })
  
  // Load races on component mount
  onMounted(async () => {
    try {
      // Load races
      const response = await raceService.getAllRaces()
      races.value = response
      
      // Load racers for selection
      const racersResponse = await racerService.getAllRacers()
      racersList.value = racersResponse
    } catch (error) {
      console.error('Error loading races', error)
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load races', life: 3000 })
    } finally {
      loading.value = false
    }
  })
  
  // Permission check
  function hasPermission(permission: string) {
    return authStore.hasPermission(permission)
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
  
  function getCompletionPercentage(race: Race) {
    if (race.total_heats === 0) return 0
    return Math.round((race.completed_heats / race.total_heats) * 100)
  }
  
  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString()
  }
  
  // Dialog management
  function openNewRaceDialog() {
    Object.assign(race, {
      name: '',
      race_type: 'round_robin',
      group_id: undefined,
      include_all_racers: true,
      selected_racer_ids: []
    })
    submitted.value = false
    editMode.value = false
    raceDialog.value = true
  }
  
  function editRace(raceData: Race) {
    editMode.value = true
    Object.assign(race, {
      name: raceData.name,
      race_type: raceData.race_type,
      group_id: raceData.group_id,
      // These fields may not be in the original data, but we need them for the form
      include_all_racers: true, // Default to true when editing
      selected_racer_ids: []
    })
    selectedRace.value = raceData
    raceDialog.value = true
  }
  
  function hideDialog() {
    raceDialog.value = false
    submitted.value = false
  }
  
  // Save race
  async function saveRace() {
    submitted.value = true
    
    if (!race.name || !race.race_type) {
      return
    }
    
    saving.value = true
    
    try {
      if (editMode.value && selectedRace.value) {
        // Update existing race
        await raceService.updateRace(selectedRace.value.id, {
          name: race.name,
          race_type: race.race_type,
          group_id: race.group_id
        })
        toast.add({ severity: 'success', summary: 'Success', detail: 'Race updated', life: 3000 })
      } else {
        // Create new race
        await raceService.createRace(race)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Race created', life: 3000 })
      }
      
      // Refresh race list
      const response = await raceService.getAllRaces()
      races.value = response
      
      // Close dialog
      raceDialog.value = false
    } catch (error: any) {
      toast.add({ 
        severity: 'error', 
        summary: 'Error', 
        detail: error.message || 'Failed to save race', 
        life: 3000 
      })
    } finally {
      saving.value = false
    }
  }
  
  // Delete race
  function confirmDeleteRace(raceData: Race) {
    confirm.require({
      message: `Are you sure you want to delete the race "${raceData.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      acceptClass: 'p-button-danger',
      accept: () => deleteRace(raceData.id)
    })
  }
  
  async function deleteRace(id: number) {
    try {
      await raceService.deleteRace(id)
      races.value = races.value.filter(r => r.id !== id)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Race deleted', life: 3000 })
    } catch (error) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete race', life: 3000 })
    }
  }
  
  // Navigation
  function navigateToRaceDetail(raceId: number) {
    router.push(`/races/${raceId}`)
  }
  </script>
  
  <style scoped>
  .race-list-container {
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
  
  :deep(.completed .p-progressbar-value) {
    background: var(--green-500);
  }
  </style>