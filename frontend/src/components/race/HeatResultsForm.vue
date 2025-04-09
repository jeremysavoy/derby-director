<template>
  <div class="heat-results-form">
    <div v-for="lane in lanes" :key="lane.lane_id" class="lane-result">
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
</template>

<script setup lang="ts">
interface HeatLane {
  lane_id: number;
  lane_number: number;
  racer_name: string;
  car_number: string;
  finish_position?: number;
  finish_time?: number;
  dnf: boolean;
  racer_id?: number;
}

defineProps({
  lanes: {
    type: Array as () => HeatLane[],
    required: true
  },
  submitted: {
    type: Boolean,
    default: false
  },
  positionOptions: {
    type: Array as () => number[],
    default: () => [1, 2, 3, 4, 5, 6, 7, 8]
  }
})

const emit = defineEmits(['update:lanes', 'dnf-change'])

function handleDnfChange(lane: HeatLane) {
  if (lane.dnf) {
    lane.finish_position = undefined;
    lane.finish_time = undefined;
  }
  emit('dnf-change', lane)
}
</script>

<style scoped>
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
</style>