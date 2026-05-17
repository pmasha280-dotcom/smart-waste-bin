<template>
  <div id="app">
    <DashboardView />
  </div>
</template>

<script setup>
import DashboardView from './views/DashboardView.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #EAE6C7;
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
  padding: 20px;
}
</style>