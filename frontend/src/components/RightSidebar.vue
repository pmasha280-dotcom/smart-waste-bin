<template>
  <div class="right-sidebar">
    <div class="user-card">
      <div class="user-role">{{ currentUserRole === 'admin' ? 'Администратор' : 'Работник' }}</div>
      <button class="action-button logout-btn" @click="handleLogout">Выйти</button>
    </div>
    
    <button v-if="currentUserRole === 'admin'" class="action-button admin-btn" @click="showAdminStats">
      Статистика (администратор)
    </button>
    
    <div class="stats-summary">
      <h4>Сводка по этажу</h4>
      <div class="stat-item">
        <span>Всего урн:</span>
        <span>{{ stats.total }}</span>
      </div>
      <div class="stat-item">
        <span>Требуют внимания:</span>
        <span>{{ stats.attentionCount }}</span>
      </div>
      <div class="stat-item">
        <span>Средний уровень:</span>
        <span>{{ stats.avgTotal }}%</span>
      </div>
    </div>


    <div class="user-role">{{ authStore.getRoleName() }}</div>
    
    
    <div class="stats-summary">
      <h4>Срочная уборка</h4>
      <ul class="alert-list">
        <li v-for="alert in stats.alertBins" :key="alert.name">
          <strong>{{ alert.name }}</strong><br>
          {{ alert.types.join(', ') }} — {{ alert.maxFill }}%
        </li>
        <li v-if="stats.alertBins.length === 0" style="background:#D9D4B0; border-left-color:#38EB2E;">
          Все урны в норме
        </li>
      </ul>
      <button class="action-button refresh-btn" @click="refresh">Обновить</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBinStore } from '../stores/binStore'
import { storeToRefs } from 'pinia'

const store = useBinStore()
const { currentUserRole } = storeToRefs(store)
const { getStats } = store

const stats = computed(() => getStats())

const emit = defineEmits(['refresh', 'logout', 'showStats'])

const refresh = () => {
  emit('refresh')
}

const handleLogout = () => {
  emit('logout')
}

const showAdminStats = () => {
  emit('showStats')
}
</script>

<style scoped>
.right-sidebar {
  width: 340px;
  background: #B2E9D8;
  border-radius: 40px;
  padding: 24px 20px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid #1A3A1A;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: fit-content;
}

.user-card {
  background: #EAE6C7;
  border-radius: 28px;
  padding: 18px;
  text-align: center;
  border: 1px solid #1E3A1E;
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.user-role {
  background: #38EB2E;
  display: inline-block;
  padding: 6px 20px;
  border-radius: 30px;
  font-weight: 700;
  font-size: 0.8rem;
  color: #00450B;
  margin-bottom: 12px;
  border: 1px solid #1E3A1E;
}

.stats-summary {
  background: #EAE6C7;
  border-radius: 28px;
  padding: 18px;
  border: 1px solid #1E3A1E;
}

.stats-summary h4 {
  color: #00450B;
  margin-bottom: 14px;
  font-size: 1rem;
  border-left: 4px solid #38EB2E;
  padding-left: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: #00450B;
  font-weight: 500;
}

.alert-list {
  list-style: none;
  margin-top: 8px;
}

.alert-list li {
  background: rgba(231, 76, 60, 0.15);
  margin-bottom: 10px;
  padding: 10px 12px;
  border-radius: 24px;
  font-size: 0.8rem;
  border-left: 4px solid #E74C3C;
  font-weight: 500;
}

.action-button {
  background: #38EB2E;
  border: none;
  width: 100%;
  padding: 12px;
  border-radius: 40px;
  font-weight: 700;
  color: #00450B;
  font-family: inherit;
  margin-top: 12px;
  cursor: pointer;
  box-shadow: 0 5px 0 #0A5C08;
  transition: 0.07s linear;
}

.action-button:active {
  transform: translateY(3px);
  box-shadow: 0 2px 0 #0A5C08;
}

.admin-btn {
  background: #00450B;
  color: #EAE6C7;
  box-shadow: 0 5px 0 #1E3A1E;
}

.logout-btn, .refresh-btn {
  background: #EAE6C7;
  box-shadow: 0 3px 0 #8B7A4B;
}

@media (max-width: 1000px) {
  .right-sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .right-sidebar > div {
    flex: 1;
    min-width: 240px;
  }
}
</style>