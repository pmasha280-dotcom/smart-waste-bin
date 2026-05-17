<template>
  <div v-if="show" class="modal" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <span>{{ bin?.name }}</span>
        <button class="close-modal" @click="close">✕</button>
      </div>
      <div v-if="bin" class="modal-body">
        <div class="status-badge">
          <strong>Общий статус:</strong> {{ getOverallStatus(bin.compartments) }}
        </div>
        
        <div v-for="(value, type) in bin.compartments" :key="type" class="comp-detail">
          <div class="comp-label">
            <span>{{ compNames[type] }}</span>
            <span><strong>{{ value }}%</strong></span>
          </div>
          <div class="comp-bar">
            <div class="comp-fill" :class="getFillClass(value)" :style="{ width: value + '%' }"></div>
          </div>
        </div>
        
        <div class="clean-frequency">
          Рекомендуемая частота уборки:<br>
          <strong>{{ getCleanFrequency(bin) }}</strong>
        </div>
        
        <div class="status-message" :class="{ 'alert': maxFill >= 85 }">
          {{ maxFill >= 85 ? '⚠️ Требуется немедленная очистка переполненных отсеков' : '✓ Состояние под контролем' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBinStore } from '../stores/binStore'

const props = defineProps(['show', 'bin'])
const emit = defineEmits(['close'])

const store = useBinStore()
const compNames = store.compNames

const maxFill = computed(() => {
  if (!props.bin) return 0
  return Math.max(...Object.values(props.bin.compartments))
})

const getFillClass = (value) => {
  if (value >= 85) return 'fill-r'
  if (value >= 50) return 'fill-y'
  return 'fill-g'
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #B2E9D8;
  border-radius: 48px;
  max-width: 480px;
  width: 90%;
  padding: 28px;
  border: 2px solid #1A3A1A;
  box-shadow: 0 30px 40px rgba(0,0,0,0.4);
  color: #00450B;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-weight: 800;
  font-size: 1.4rem;
}

.close-modal {
  background: #EAE6C7;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.comp-detail {
  margin-bottom: 16px;
}

.comp-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.comp-bar {
  background: #EAE6C7;
  border-radius: 20px;
  height: 12px;
  overflow: hidden;
}

.comp-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 0.3s ease;
}

.fill-g { background-color: #38EB2E; }
.fill-y { background-color: #F5C542; }
.fill-r { background-color: #E74C3C; }

.clean-frequency {
  background: #00450B;
  color: #EAE6C7;
  padding: 10px 14px;
  border-radius: 28px;
  margin: 16px 0;
  text-align: center;
  font-weight: 600;
  font-size: 0.85rem;
}

.status-message {
  padding: 8px;
  background: #EAE6C7;
  border-radius: 20px;
  text-align: center;
  font-size: 0.8rem;
}

.status-message.alert {
  background: #fdcbc6;
  font-weight: bold;
}
</style>