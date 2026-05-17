<template>
  <div class="map-area">
    <div class="map-header">
      <h2>План этажа</h2>
      <div class="floor-badge">{{ floorData?.name || `Этаж ${currentFloor}` }}</div>
    </div>
    <div class="map-svg-container" ref="mapContainer">
      <svg 
        ref="svgMap" 
        viewBox="0 0 800 600" 
        width="100%" 
        height="auto"
        @click="handleSvgClick"
      >
        <!-- Фон -->
        <rect width="800" height="600" fill="#FCF9E8" stroke="#1E3A1E" stroke-width="2" rx="16" />
        
        <!-- Сетка для ориентира -->
        <g stroke="#C0B87A" stroke-width="1" stroke-dasharray="4 4">
          <line v-for="x in [200, 400, 600]" :key="x" :x1="x" y1="0" :x2="x" y2="600" />
          <line v-for="y in [150, 300, 450]" :key="y" x1="0" :y1="y" x2="800" :y2="y" />
        </g>
        
        <!-- Урны -->
        <g v-for="bin in bins" :key="bin.id" class="bin-marker" @click="onBinClick(bin)">
          <!-- Круг с цветом статуса -->
          <circle 
            :cx="scaleX(bin.position_x)" 
            :cy="scaleY(bin.position_y)" 
            r="22" 
            :fill="getBinColor(bin.compartments)"
            stroke="#1A3A1A" 
            stroke-width="2.5"
          />
          <!-- Иконка урны (текстовая) -->
          <text 
            :x="scaleX(bin.position_x)" 
            :y="scaleY(bin.position_y) + 6" 
            text-anchor="middle" 
            fill="#00450B" 
            font-size="16" 
            font-weight="bold" 
            pointer-events="none"
          >
            ♻️
          </text>
          <!-- Название урны -->
          <text 
            :x="scaleX(bin.position_x) + 28" 
            :y="scaleY(bin.position_y) - 10" 
            fill="#00450B" 
            font-size="10" 
            font-weight="500"
            pointer-events="none"
          >
            {{ bin.name }}
          </text>
          <!-- Процент заполнения -->
          <text 
            :x="scaleX(bin.position_x)" 
            :y="scaleY(bin.position_y) - 15" 
            text-anchor="middle" 
            fill="#00450B" 
            font-size="11" 
            font-weight="bold"
            pointer-events="none"
          >
            {{ getMaxFill(bin.compartments) }}%
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  floorData: {
    type: Object,
    default: () => ({ bins: [] })
  },
  currentFloor: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['bin-click'])

// Размеры SVG карты 
const MAP_WIDTH = 800
const MAP_HEIGHT = 600

// Масштабирование координат из БД (0-100) в пиксели SVG
const scaleX = (x) => {
  if (x === null || x === undefined || isNaN(x)) return MAP_WIDTH / 2
  return (Math.min(100, Math.max(0, x)) / 100) * MAP_WIDTH
}

const scaleY = (y) => {
  if (y === null || y === undefined || isNaN(y)) return MAP_HEIGHT / 2
  return (Math.min(100, Math.max(0, y)) / 100) * MAP_HEIGHT
}

// Список урн с проверкой на валидность координат
const bins = computed(() => {
  const binsList = props.floorData?.bins || []
  return binsList.filter(bin => {
    // Фильтруем урны с невалидными координатами
    const xValid = bin.position_x !== null && !isNaN(bin.position_x)
    const yValid = bin.position_y !== null && !isNaN(bin.position_y)
    if (!xValid || !yValid) {
      console.warn(`Урна ${bin.id} (${bin.name}) имеет невалидные координаты: x=${bin.position_x}, y=${bin.position_y}`)
    }
    return xValid && yValid
  })
})

const getBinColor = (compartments) => {
  const maxFill = getMaxFill(compartments)
  if (maxFill >= 85) return "#E74C3C"
  if (maxFill >= 50) return "#F5C542"
  return "#38EB2E"
}

const getMaxFill = (compartments) => {
  if (!compartments || !Array.isArray(compartments) || compartments.length === 0) return 0
  const fillLevels = compartments.map(c => c.fill_level || 0)
  return Math.max(...fillLevels)
}

const onBinClick = (bin) => {
  emit('bin-click', bin)
}

const handleSvgClick = (event) => {
  // Опционально: обработка клика по SVG для создания новой урны (для админа)
  const rect = event.target.getBoundingClientRect()
  const x = (event.clientX - rect.left) / rect.width * MAP_WIDTH
  const y = (event.clientY - rect.top) / rect.height * MAP_HEIGHT
  console.log(`Клик на карте: x=${Math.round(x)}, y=${Math.round(y)}`)
  // Можно отправить координаты для создания урны
}
</script>

<style scoped>
.map-area {
  flex: 1;
  background: #FFFFFF;
  border-radius: 40px;
  border: 2px solid #1A3A1A;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px dashed #1E3A1E;
}

.map-header h2 {
  color: #00450B;
  font-size: 1.5rem;
  font-weight: 700;
}

.floor-badge {
  background: #B2E9D8;
  padding: 6px 16px;
  border-radius: 40px;
  color: #00450B;
  font-weight: 600;
  border: 1px solid #1E3A1E;
}

.map-svg-container {
  flex: 1;
  background: #F8F7EF;
  border-radius: 28px;
  padding: 16px;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.1);
}

svg {
  width: 100%;
  height: auto;
  background: #FDFCF5;
  border-radius: 24px;
  cursor: crosshair;
}

.bin-marker {
  cursor: pointer;
  transition: transform 0.2s ease, filter 0.2s;
}

.bin-marker:hover {
  transform: scale(1.05);
}

.bin-marker:hover circle {
  filter: drop-shadow(0 0 6px rgba(0,0,0,0.3));
}
</style>