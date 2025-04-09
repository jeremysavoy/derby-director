<template>
    <MainLayout>
      <div class="not-found-container">
        <div class="not-found-content">
          <h1>404</h1>
          <h2>Page Not Found</h2>
          <p>Sorry, the page you are looking for does not exist.</p>
          <Button label="Go to Dashboard" icon="pi pi-home" @click="router.push('/dashboard')" />
        </div>
      </div>
    </MainLayout>
  </template>
  
  <script setup lang="ts">
  import { useRouter } from 'vue-router'
  import MainLayout from '../layouts/MainLayout.vue'
  
  const router = useRouter()
  </script>
  
  <style scoped>
  .not-found-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
  }
  
  .not-found-content {
    text-align: center;
    max-width: 500px;
  }
  
  .not-found-content h1 {
    font-size: 5rem;
    margin: 0;
    color: var(--primary-color);
  }
  
  .not-found-content h2 {
    margin: 0 0 1rem 0;
  }
  
  .not-found-content p {
    margin-bottom: 2rem;
    color: var(--text-color-secondary);
  }
  </style>