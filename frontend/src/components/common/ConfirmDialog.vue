<template>
    <ConfirmDialog>
      <template #message="slotProps">
        <div class="confirm-dialog-content">
          <i :class="slotProps.message.icon" style="font-size: 1.5rem"></i>
          <div class="confirm-text">
            <h3>{{ slotProps.message.header }}</h3>
            <p>{{ slotProps.message.message }}</p>
          </div>
        </div>
      </template>
    </ConfirmDialog>
  </template>
  
  <script setup lang="ts">
  // This component extends PrimeVue's ConfirmDialog with custom styling
  </script>
  
  <style scoped>
  .confirm-dialog-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.5rem 0;
  }
  
  .confirm-text h3 {
    margin: 0 0 0.5rem 0;
  }
  
  .confirm-text p {
    margin: 0;
    line-height: 1.5;
  }
  </style>