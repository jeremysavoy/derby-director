<template>
    <div class="layout-wrapper">
      <header class="layout-header">
        <div class="layout-header-content">
          <div class="layout-logo">
            <h1>Derby Director</h1>
          </div>
          <div class="layout-menu">
            <ul class="menu-list">
              <li><router-link to="/dashboard">Dashboard</router-link></li>
              <li><router-link to="/racers">Racers</router-link></li>
              <li><router-link to="/races">Races</router-link></li>
              <li><router-link to="/reports">Reports</router-link></li>
            </ul>
          </div>
          <div class="layout-topbar-actions">
            <span class="username">{{ user?.username }}</span>
            <Button 
              icon="pi pi-sign-out" 
              class="p-button-rounded p-button-text" 
              @click="logout"
              tooltip="Logout"
            />
          </div>
        </div>
      </header>
      
      <main class="layout-main">
        <slot></slot>
      </main>
      
      <footer class="layout-footer">
        <div class="layout-footer-content">
          <p>Derby Director &copy; {{ currentYear }}</p>
        </div>
      </footer>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed } from 'vue'
  import { useAuthStore } from '../stores/auth'
  
  const authStore = useAuthStore()
  const user = computed(() => authStore.user)
  const currentYear = new Date().getFullYear()
  
  function logout() {
    authStore.logout()
  }
  </script>
  
  <style scoped>
  .layout-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  .layout-header {
    background-color: var(--primary-color);
    color: white;
    padding: 0.5rem 2rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .layout-header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .layout-logo h1 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .menu-list {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  
  .menu-list li {
    margin-right: 1.5rem;
  }
  
  .menu-list a {
    color: white;
    text-decoration: none;
    font-weight: 500;
  }
  
  .menu-list a.router-link-active {
    font-weight: 700;
    border-bottom: 2px solid white;
  }
  
  .layout-topbar-actions {
    display: flex;
    align-items: center;
  }
  
  .username {
    margin-right: 1rem;
    font-weight: 500;
  }
  
  .layout-main {
    flex: 1;
    padding: 2rem;
  }
  
  .layout-footer {
    background-color: #f8f9fa;
    padding: 1rem 2rem;
    text-align: center;
    border-top: 1px solid #e9ecef;
  }
  </style>