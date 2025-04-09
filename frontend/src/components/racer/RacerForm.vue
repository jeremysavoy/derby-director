<template>
  <div class="racer-form">
    <div class="field">
      <label for="firstName">First Name</label>
      <InputText 
        id="firstName" 
        v-model="modelValue.first_name" 
        required 
        :class="{'p-invalid': submitted && !modelValue.first_name}" 
      />
      <small class="p-error" v-if="submitted && !modelValue.first_name">First Name is required.</small>
    </div>
    
    <div class="field">
      <label for="lastName">Last Name</label>
      <InputText 
        id="lastName" 
        v-model="modelValue.last_name" 
        required 
        :class="{'p-invalid': submitted && !modelValue.last_name}" 
      />
      <small class="p-error" v-if="submitted && !modelValue.last_name">Last Name is required.</small>
    </div>
    
    <div class="field">
      <label for="carNumber">Car Number</label>
      <InputText 
        id="carNumber" 
        v-model="modelValue.car_number" 
        required 
        :class="{'p-invalid': submitted && !modelValue.car_number}" 
      />
      <small class="p-error" v-if="submitted && !modelValue.car_number">Car Number is required.</small>
    </div>
    
    <div class="field">
      <label for="rank">Rank</label>
      <Dropdown 
        id="rank" 
        v-model="modelValue.rank" 
        :options="rankOptions" 
        optionLabel="name" 
        optionValue="value"
        placeholder="Select a Rank" 
        required 
        :class="{'p-invalid': submitted && !modelValue.rank}" 
      />
      <small class="p-error" v-if="submitted && !modelValue.rank">Rank is required.</small>
    </div>
    
    <div class="field">
      <label for="den">Den (Optional)</label>
      <Dropdown 
        id="den" 
        v-model="modelValue.den" 
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
        v-model="modelValue.weight" 
        mode="decimal" 
        :minFractionDigits="2" 
        :maxFractionDigits="2"
        placeholder="Enter weight" 
      />
    </div>
    
    <div v-if="showStatus" class="field">
      <label for="checkinStatus">Check-in Status</label>
      <Dropdown 
        id="checkinStatus" 
        v-model="modelValue.checkin_status" 
        :options="statusOptions" 
        optionLabel="name"
        optionValue="value" 
        placeholder="Select Status" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// Define a type for the racer model
interface RacerModel {
  first_name: string;
  last_name: string;
  car_number: string;
  rank: string;
  den?: string;
  weight?: number;
  checkin_status?: 'registered' | 'checked_in' | 'passed_inspection';
  [key: string]: any;
}

// Define a type for the dropdown options
interface DropdownOption {
  name: string;
  value: string;
}

defineProps({
  modelValue: {
    type: Object as () => RacerModel,
    required: true
  },
  submitted: {
    type: Boolean,
    default: false
  },
  showStatus: {
    type: Boolean,
    default: false
  },
  rankOptions: {
    type: Array as () => DropdownOption[],
    default: () => [
      { name: 'Lion', value: 'Lion' },
      { name: 'Tiger', value: 'Tiger' },
      { name: 'Wolf', value: 'Wolf' },
      { name: 'Bear', value: 'Bear' },
      { name: 'Webelos', value: 'Webelos' },
      { name: 'Arrow of Light', value: 'Arrow of Light' }
    ]
  },
  denOptions: {
    type: Array as () => DropdownOption[],
    default: () => [
      { name: 'Den 1', value: 'Den 1' },
      { name: 'Den 2', value: 'Den 2' },
      { name: 'Den 3', value: 'Den 3' },
      { name: 'Den 4', value: 'Den 4' },
      { name: 'Den 5', value: 'Den 5' }
    ]
  }
})

defineEmits(['update:modelValue'])

const statusOptions = [
  { name: 'Registered', value: 'registered' },
  { name: 'Checked In', value: 'checked_in' },
  { name: 'Passed Inspection', value: 'passed_inspection' }
]
</script>

<style scoped>
.racer-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>