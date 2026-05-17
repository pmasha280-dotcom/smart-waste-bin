<template>
  <div v-if="authStore.isLoading" class="loading">
    <div class="loader">Загрузка...</div>
  </div>
  
  <div v-else-if="!authStore.isAuthenticated" class="unauthorized">
    <h2>Доступ запрещён</h2>
    <p>Пожалуйста, <router-link to="/login">войдите в систему</router-link></p>
  </div>
  
  <div v-else-if="error" class="error">
    <p>Ошибка: {{ error }}</p>
    <button @click="refreshData" class="action-btn">Повторить</button>
  </div>
  
  <div v-else class="dashboard">
    <FloorPanel 
      :currentFloor="currentFloor" 
      :floors="floors"
      @change-floor="changeFloor" 
    />
    <MapArea 
      :floorData="currentFloorData" 
      :currentFloor="currentFloor"
      @bin-click="openBinModal"
    />
    <RightSidebar 
      :stats="stats"
      :userRole="authStore.userRole"
      @logout="handleLogout"
      @refresh="refreshData"
      @clean-request="handleCleanRequest"
    />
    <BinModal 
      :show="showModal" 
      :bin="selectedBin"
      :stats="binStats"
      @close="closeModal"
      @clean="handleCleanBin"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useBinStore } from '../stores/binStore'
import FloorPanel from '../components/FloorPanel.vue'
import MapArea from '../components/MapArea.vue'
import RightSidebar from '../components/RightSidebar.vue'
import BinModal from '../components/BinModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const binStore = useBinStore()

// Local state
const currentFloor = ref(1)
const showModal = ref(false)
const selectedBin = ref(null)
const error = ref(null)

// Computed
const floors = computed(() => binStore.floors)
const currentFloorData = computed(() => binStore.getFloorData(currentFloor.value))
const stats = computed(() => binStore.getStats(currentFloor.value))
const binStats = computed(() => binStore.getBinStats(selectedBin.value?.id))

// Methods
const loadInitialData = async () => {
  // Проверяем авторизацию перед загрузкой
  if (!authStore.isAuthenticated) {
    console.log('Пользователь не авторизован, пропускаем загрузку данных')
    return
  }
  
  error.value = null
  try {
    await binStore.loadFloors()
    if (floors.value.length > 0) {
      await binStore.loadBinsForFloor(currentFloor.value)
    }
  } catch (err) {
    console.error('Ошибка загрузки данных:', err)
    error.value = 'Не удалось загрузить данные'
  }
}

const refreshData = () => {
  loadInitialData()
}

const changeFloor = async (floor) => {
  currentFloor.value = floor
  if (authStore.isAuthenticated) {
    await binStore.loadBinsForFloor(floor)
  }
}

const openBinModal = (bin) => {
  selectedBin.value = bin
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedBin.value = null
}

const handleCleanBin = async (binId) => {
  if (authStore.userRole !== 'admin' && authStore.userRole !== 'worker') {
    alert('У вас нет прав для этого действия')
    return
  }
  
  try {
    await binStore.cleanBin(binId, currentFloor.value)
    await refreshData()
    closeModal()
    alert('Урна отмечена как очищенная')
  } catch (err) {
    alert('Ошибка при очистке')
  }
}

const handleCleanRequest = () => {
  // Открыть список урн для очистки
  console.log('Запрос на очистку')
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// Lifecycle
onMounted(() => {
  // Загружаем данные ТОЛЬКО если пользователь авторизован
  if (authStore.isAuthenticated) {
    loadInitialData()
  }
})

// Следим за изменением статуса авторизации
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    loadInitialData()
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 40px);
}

.loading, .unauthorized, .error {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 40px;
  margin: 40px auto;
  max-width: 500px;
}

.loader {
  font-size: 18px;
  color: #00450B;
}

.unauthorized h2 {
  color: #E74C3C;
  margin-bottom: 16px;
}

.action-btn {
  background-color: #38EB2E;
  border: none;
  border-radius: 40px;
  padding: 10px 20px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 16px;
}

@media (max-width: 1000px) {
  .dashboard {
    flex-direction: column;
  }
}
</style>