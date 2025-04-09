<template>
    <div class="login-page">
      <Card class="login-card">
        <template #title>
          <h1 class="login-title">Derby Director</h1>
        </template>
        <template #content>
          <form @submit.prevent="handleSubmit" class="login-form">
            <div class="field">
              <label for="username">Username</label>
              <InputText 
                id="username" 
                v-model="username" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !username }"
              />
              <small v-if="submitted && !username" class="p-error">Username is required</small>
            </div>
            
            <div class="field mt-4">
              <label for="password">Password</label>
              <InputText 
                id="password" 
                type="password" 
                v-model="password" 
                class="w-full"
                :class="{ 'p-invalid': submitted && !password }"
              />
              <small v-if="submitted && !password" class="p-error">Password is required</small>
            </div>
            
            <div v-if="authStore.error" class="login-error mt-3">
              {{ authStore.error }}
            </div>
            
            <div class="flex justify-content-end mt-4">
              <Button 
                type="submit" 
                label="Login" 
                icon="pi pi-sign-in" 
                :loading="authStore.loading"
              />
            </div>
          </form>
        </template>
      </Card>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '../stores/auth'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  const username = ref('')
  const password = ref('')
  const submitted = ref(false)
  
  async function handleSubmit() {
    submitted.value = true
    
    if (!username.value || !password.value) {
      return
    }
    
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push('/dashboard')
    }
  }
  </script>
  
  <style scoped>
  .login-page {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7f9;
  }
  
  .login-card {
    width: 100%;
    max-width: 450px;
  }
  
  .login-title {
    text-align: center;
    color: var(--primary-color);
    margin: 0 0 1rem 0;
  }
  
  .login-error {
    color: var(--red-500);
    font-size: 0.875rem;
  }
  </style>