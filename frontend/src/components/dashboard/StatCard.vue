<template>
    <div class="stat-card">
      <div class="stat-icon" :style="{ backgroundColor: iconBgColor }">
        <i :class="icon" :style="{ color: iconColor }"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps({
    icon: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    label: {
      type: String,
      required: true
    },
    iconColor: {
      type: String,
      default: 'var(--primary-color)'
    },
    iconBgColor: {
      type: String,
      default: 'rgba(var(--primary-color-rgb), 0.1)'
    }
  })
  </script>
  
  <style scoped>
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
    margin-right: 1rem;
  }
  
  .stat-icon i {
    font-size: 1.5rem;
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
  </style>