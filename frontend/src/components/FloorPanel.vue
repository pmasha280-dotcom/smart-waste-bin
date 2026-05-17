<template>
  <div class="floor-panel">
    <button
      v-for="floor in Object.keys(floorsData)"
      :key="floor"
      class="floor-btn"
      :class="{ active: currentFloor === parseInt(floor) }"
      @click="setFloor(parseInt(floor))"
    >
      {{ floor }}
    </button>
  </div>
</template>

<script setup>
import { useBinStore } from '../stores/binStore'
import { storeToRefs } from 'pinia'

const store = useBinStore()
const { floorsData, currentFloor } = storeToRefs(store)
const { setFloor } = store
</script>

<style scoped>
.floor-panel {
  width: 100px;
  background: #B2E9D8;
  border-radius: 32px;
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid #1A3A1A;
  height: fit-content;
}

.floor-btn {
  width: 100%;
  background: #EAE6C7;
  border: 2px solid #1E3A1E;
  border-radius: 60px;
  padding: 14px 0;
  font-weight: 700;
  font-size: 1.2rem;
  color: #00450B;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-family: inherit;
}

.floor-btn.active {
  background: #38EB2E;
  border-color: #00450B;
  box-shadow: 0 6px 0 #0A5C08, 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.floor-btn:not(.active):hover {
  background: #d9d4b0;
  transform: scale(0.96);
}

@media (max-width: 1000px) {
  .floor-panel {
    width: 100%;
    flex-direction: row;
    justify-content: center;
    padding: 16px;
  }
  .floor-btn {
    width: auto;
    padding: 10px 24px;
  }
}
</style>