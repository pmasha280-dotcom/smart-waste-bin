import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiService from '../services/apiService'

export const useBinStore = defineStore('bin', () => {
  const floorsData = ref({})
  const currentFloor = ref(1)
  const currentUserRole = ref('worker')
  const selectedBin = ref(null)
  const showModal = ref(false)
  const loading = ref(false)
  const error = ref(null)

  const compNames = { plastic: "Пластик", glass: "Стекло", paper: "Бумага", general: "Смешанный" }

  const currentFloorData = computed(() => floorsData.value[currentFloor.value])
  
  // получение значений заполненности
  const getSafeFillValues = (compartments) => {
    if (!compartments || typeof compartments !== 'object') return []
    return Object.values(compartments).filter(v => typeof v === 'number' && !isNaN(v) && isFinite(v))
  }

  //получение максимального заполнения
  const getSafeMaxFill = (compartments) => {
    const values = getSafeFillValues(compartments)
    if (values.length === 0) return 0
    return Math.max(...values)
  }

  // получение среднего заполнения
  const getSafeAvgFill = (compartments) => {
    const values = getSafeFillValues(compartments)
    if (values.length === 0) return 0
    return values.reduce((a, b) => a + b, 0) / values.length
  }


  async function fetchFloors() {
    loading.value = true
    error.value = null
    try {
      const data = await apiService.getFloors()
      floorsData.value = data
    } catch (err) {
      error.value = 'Не удалось загрузить данные этажей'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchBinsForFloor(floorId) {
    loading.value = true
    try {
      const bins = await apiService.getBinsByFloor(floorId)
      if (!floorsData.value[floorId]) {
        floorsData.value[floorId] = { name: `Этаж ${floorId}`, bins: [] }
      }
      floorsData.value[floorId].bins = bins
    } catch (err) {
      error.value = `Не удалось загрузить данные для этажа ${floorId}`
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function refreshCurrentFloor() {
    await fetchBinsForFloor(currentFloor.value)
  }

  async function cleanBin(binId) {
    try {
      await apiService.cleanBin(binId, currentFloor.value)
      await refreshCurrentFloor()
      return true
    } catch (err) {
      error.value = 'Не удалось очистить урну'
      return false
    }
  }

  function setFloor(floor) {
    currentFloor.value = floor
    fetchBinsForFloor(floor)
  }

  function getBinColor(compartments) {
    const maxFill = getSafeMaxFill(compartments)
    if (maxFill >= 85) return "#E74C3C"
    if (maxFill >= 50) return "#F5C542"
    return "#38EB2E"
  }

  function getOverallStatus(compartments) {
    const maxFill = getSafeMaxFill(compartments)
    if (maxFill >= 85) return "Переполнение"
    if (maxFill >= 50) return "Внимание"
    return "Норма"
  }

  function getCleanFrequency(bin) {
    if (!bin || !bin.compartments) return "Нет данных"
    const maxFill = getSafeMaxFill(bin.compartments)
    if (maxFill >= 85) return "Требуется немедленная уборка"
    if (maxFill >= 70) return "Уборка требуется ежедневно"
    if (maxFill >= 50) return "Уборка каждые 2-3 дня"
    return "Редкая уборка"
  }


  function getStats() {
    const bins = currentFloorData.value?.bins || []
    const total = bins.length
    
    // Если нет урн - возвращаем нули
    if (total === 0) {
      return { 
        total: 0, 
        attentionCount: 0, 
        avgTotal: 0, 
        alertBins: [] 
      }
    }
    
    let attentionCount = 0
    let sumFill = 0
    let alertBins = []
    
    for (let bin of bins) {
      // Проверяем отсеки 
      if (!bin.compartments) {
        console.warn(`Урна ${bin.id} (${bin.name}) не имеет данных о заполнении`)
        continue
      }
      
      // получаем значения
      const values = getSafeFillValues(bin.compartments)
      
      // Если все значения пустые пропускаем урну
      if (values.length === 0) {
        console.warn(`Урна ${bin.id} (${bin.name}) имеет невалидные данные:`, bin.compartments)
        continue
      }
      
      const maxFill = Math.max(...values)
      const avgFill = values.reduce((a, b) => a + b, 0) / values.length
      
      sumFill += avgFill
      
      if (maxFill >= 85) {
        attentionCount++
        let fullTypes = []
        for (let [type, val] of Object.entries(bin.compartments)) {
          if (typeof val === 'number' && val >= 85) {
            fullTypes.push(compNames[type] || type)
          }
        }
        alertBins.push({ 
          id: bin.id,
          name: bin.name, 
          types: fullTypes, 
          maxFill: Math.round(maxFill) 
        })
      } else if (maxFill >= 50) {
        attentionCount++
      }
    }
    
    // Вычисляем среднее если были обработаны урны
    const processedCount = bins.filter(bin => {
      if (!bin.compartments) return false
      const values = getSafeFillValues(bin.compartments)
      return values.length > 0
    }).length
    
    const avgTotal = processedCount > 0 ? Math.round(sumFill / processedCount) : 0
    
    return { 
      total, 
      attentionCount, 
      avgTotal, 
      alertBins 
    }
  }

  // метод для статистики конкретной урны 
  function getBinStats(binId) {
    if (!binId) return null
    
    const allBins = currentFloorData.value?.bins || []
    const bin = allBins.find(b => b.id === binId)
    
    if (!bin || !bin.compartments) return null
    
    const compartments = bin.compartments
    const maxFill = getSafeMaxFill(compartments)
    const avgFill = getSafeAvgFill(compartments)
    const status = getOverallStatus(compartments)
    const frequency = getCleanFrequency(bin)
    
    // Данные по каждому отсеку
    const compartmentDetails = Object.entries(compartments).map(([type, value]) => ({
      type: compNames[type] || type,
      typeKey: type,
      fillLevel: typeof value === 'number' && !isNaN(value) ? value : 0,
      color: value >= 85 ? 'red' : value >= 50 ? 'yellow' : 'green'
    }))
    
    return {
      id: bin.id,
      name: bin.name,
      maxFill: Math.round(maxFill),
      avgFill: Math.round(avgFill),
      status,
      frequency,
      compartments: compartmentDetails,
      lastUpdated: bin.updated_at || new Date().toISOString()
    }
  }

  function openModal(bin) {
    selectedBin.value = bin
    showModal.value = true
  }

  function closeModal() {
    showModal.value = false
    selectedBin.value = null
  }

  async function init() {
    await fetchFloors()
    await fetchBinsForFloor(currentFloor.value)
  }

  return {
    floorsData,
    currentFloor,
    currentUserRole,
    selectedBin,
    showModal,
    loading,
    error,
    
  
    currentFloorData,
    compNames,
    

    setFloor,
    refreshCurrentFloor,
    cleanBin,
    getBinColor,
    getOverallStatus,
    getCleanFrequency,
    getStats,
    getBinStats,      
    openModal,
    closeModal,
    init
  }
})