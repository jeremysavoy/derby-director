<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />
    <router-view />
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: var(--font-family);
}

.app-container {
  min-height: 100vh;
}
</style>