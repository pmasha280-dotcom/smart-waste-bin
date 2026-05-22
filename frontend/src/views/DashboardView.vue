<template>
  <div class="dashboard">
    <div class="sidebar">
      <div class="user-info">
        <h3>{{ userRole }}</h3>
        <p>{{ userName }}</p>
        <button v-if="!isGuest" @click="logout" class="logout-btn">Выйти</button>
        <button v-else @click="goToLogin" class="logout-btn">Войти</button>
      </div>
      
      <div class="stats">
        <h4>Сводка</h4>
        <p>Всего урн: {{ totalBins }}</p>
        <p>Требуют внимания: {{ needAttentionCount }}</p>
        <p>Средний уровень: {{ averageFillLevel }}%</p>
      </div>
      
      <div class="attention-list">
        <h4>Срочная уборка</h4>
        <div v-if="urgentBins.length === 0">Все урны в норме</div>
        <div v-for="bin in urgentBins" :key="bin.id" class="urgent-item">
          {{ bin.name }} - {{ bin.status }}
          <button v-if="isWorker" class="clean-btn-small" @click="cleanBin(bin)">Очистить</button>
        </div>
      </div>
    </div>
    
    <div class="main-content">
      <div class="floor-selector">
        <button 
          v-for="floor in floors" 
          :key="floor.id"
          :class="{ active: currentFloor === floor.id }"
          @click="selectFloor(floor.id)"
        >
          {{ floor.name }}
        </button>
      </div>
      
      <div class="map-area">
        <div v-if="loading" class="loading">Загрузка...</div>
        <svg v-else viewBox="0 0 800 600" width="100%" height="500">
          <rect width="800" height="600" fill="#FCF9E8" stroke="#1E3A1E" stroke-width="2" rx="16" />
          
          <!-- Урны -->
          <g v-for="bin in currentBins" :key="bin.id" @click="selectBin(bin)" style="cursor: pointer">
            <circle
              :cx="bin.position_x * 8"
              :cy="bin.position_y * 8"
              r="25"
              :fill="getBinColor(bin)"
              stroke="#1A3A1A"
              stroke-width="2.5"
            />
            <text
              :x="bin.position_x * 8"
              :y="bin.position_y * 8 + 6"
              text-anchor="middle"
              fill="#00450B"
              font-size="16"
              font-weight="bold"
            >
              🗑️
            </text>
            <text
              :x="bin.position_x * 8 + 30"
              :y="bin.position_y * 8 - 10"
              fill="#00450B"
              font-size="10"
            >
              {{ bin.name }}
            </text>
            <text
              :x="bin.position_x * 8"
              :y="bin.position_y * 8 - 15"
              text-anchor="middle"
              fill="#00450B"
              font-size="11"
              font-weight="bold"
            >
              {{ getMaxFill(bin) }}%
            </text>
            <!-- Кнопка очистки на карте для работников -->
            <circle
              v-if="isWorker && getMaxFill(bin) >= 85"
              :cx="bin.position_x * 8 + 35"
              :cy="bin.position_y * 8 - 20"
              r="12"
              fill="#38EB2E"
              stroke="#1A3A1A"
              stroke-width="1.5"
              @click.stop="cleanBin(bin)"
            />
            <text
              v-if="isWorker && getMaxFill(bin) >= 85"
              :x="bin.position_x * 8 + 35"
              :y="bin.position_y * 8 - 16"
              text-anchor="middle"
              fill="#00450B"
              font-size="10"
              font-weight="bold"
              @click.stop="cleanBin(bin)"
            >
              ✓
            </text>
          </g>
        </svg>
      </div>
    </div>
    
    <!-- Модальное окно с деталями урны -->
    <div v-if="selectedBin" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <h3>{{ selectedBin.name }}</h3>
        <div v-for="comp in selectedBin.compartments" :key="comp.id" class="compartment">
          <span>{{ comp.waste_type }}:</span>
          <div class="progress-bar">
            <div class="progress" :style="{ width: comp.fill_level + '%' }"></div>
          </div>
          <span>{{ comp.fill_level }}%</span>
        </div>
        <button v-if="isWorker" class="clean-btn" @click="cleanBin(selectedBin)">Отметить очистку</button>
        <button @click="closeModal">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import apiService from '../services/apiService'

const router = useRouter()
const authStore = useAuthStore()

const floors = ref([])
const bins = ref([])
const currentFloor = ref(1)
const selectedBin = ref(null)
const loading = ref(false)
const cleaning = ref(false)

const isGuest = computed(() => authStore.isGuest)
const isWorker = computed(() => {
  return authStore.user?.role === 'worker' || authStore.user?.role === 'admin'
})

const userRole = computed(() => {
  if (authStore.isGuest) return 'Гость'
  if (authStore.user?.role === 'admin') return 'Администратор'
  if (authStore.user?.role === 'worker') return 'Работник'
  return 'Пользователь'
})

const userName = computed(() => {
  if (authStore.isGuest) return 'Гостевой доступ'
  return authStore.user?.username || 'Пользователь'
})

const totalBins = computed(() => bins.value.length)

const needAttentionCount = computed(() => {
  return bins.value.filter(b => {
    const maxFill = getMaxFill(b)
    return maxFill >= 85
  }).length
})

const averageFillLevel = computed(() => {
  if (bins.value.length === 0) return 0
  const total = bins.value.reduce((sum, bin) => sum + getMaxFill(bin), 0)
  return Math.round(total / bins.value.length)
})

const urgentBins = computed(() => {
  return bins.value.filter(b => getMaxFill(b) >= 85)
})

const currentBins = computed(() => {
  return bins.value.filter(b => b.floor_id === currentFloor.value)
})

const getMaxFill = (bin) => {
  if (!bin.compartments || bin.compartments.length === 0) return 0
  const fills = bin.compartments.map(c => c.fill_level || 0)
  return Math.max(...fills)
}

const getBinColor = (bin) => {
  const fill = getMaxFill(bin)
  if (fill >= 85) return '#E74C3C'
  if (fill >= 50) return '#F5C542'
  return '#38EB2E'
}

const selectFloor = (floorId) => {
  currentFloor.value = floorId
}

const selectBin = (bin) => {
  selectedBin.value = bin
}

const closeModal = () => {
  selectedBin.value = null
}

const cleanBin = async (bin) => {
  if (!confirm(`Отметить очистку урны "${bin.name}"?`)) return
  
  cleaning.value = true
  try {
    await apiService.cleanBin(bin.id, currentFloor.value)
    alert(`✅ Урна "${bin.name}" отмечена как очищенная`)
    // Обновляем данные
    await loadData()
    closeModal()
  } catch (error) {
    console.error('Ошибка при очистке:', error)
    alert('❌ Ошибка при отметке очистки')
  } finally {
    cleaning.value = false
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const goToLogin = () => {
  router.push('/login')
}

const loadData = async () => {
  loading.value = true
  try {
    console.log('Загрузка данных...')
    const [floorsData, binsData] = await Promise.all([
      apiService.getFloors(),
      apiService.getBins()
    ])
    console.log('Этажи получены:', floorsData)
    console.log('Урны получены:', binsData)
    floors.value = floorsData || []
    bins.value = binsData || []
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  min-height: 100vh;
  background: #EAE6C7;
}

.sidebar {
  width: 280px;
  background: #B2E9D8;
  padding: 20px;
  border-right: 2px solid #1A3A1A;
}

.user-info {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #1A3A1A;
  margin-bottom: 20px;
}

.logout-btn {
  background: #38EB2E;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 10px;
}

.stats {
  margin-bottom: 20px;
}

.attention-list {
  max-height: 300px;
  overflow-y: auto;
}

.urgent-item {
  background: #FFE0E0;
  padding: 8px;
  margin: 5px 0;
  border-radius: 8px;
  color: #C0392B;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clean-btn-small {
  background: #38EB2E;
  border: none;
  padding: 4px 8px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 11px;
}

.main-content {
  flex: 1;
  padding: 20px;
}

.floor-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.floor-selector button {
  background: #FEFCF5;
  border: 2px solid #1A3A1A;
  padding: 10px 20px;
  border-radius: 30px;
  cursor: pointer;
  font-weight: 600;
}

.floor-selector button.active {
  background: #38EB2E;
}

.map-area {
  background: #FDFCF5;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

svg {
  width: 100%;
  height: auto;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 24px;
  min-width: 300px;
}

.compartment {
  margin: 15px 0;
}

.progress-bar {
  background: #E0E0E0;
  border-radius: 10px;
  height: 20px;
  overflow: hidden;
  margin: 5px 0;
}

.progress {
  background: #38EB2E;
  height: 100%;
  transition: width 0.3s;
}

.clean-btn {
  background: #38EB2E;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 15px;
  width: 100%;
  font-size: 14px;
  font-weight: bold;
}
</style>
