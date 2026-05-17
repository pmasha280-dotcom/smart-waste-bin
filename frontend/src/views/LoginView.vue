<template>
  <div class="login-card">
    <div class="tabs">
      <button 
        v-for="role in roles" 
        :key="role"
        class="tab-btn" 
        :class="{ active: currentRole === role }"
        @click="currentRole = role"
      >
        {{ getRoleName(role) }}
      </button>
    </div>

    <!-- Гость -->
    <div v-if="currentRole === 'guest'" class="tab-content active-content">
      <div class="guest-welcome">
        <div class="guest-icon-symbol">♻️</div>
        <h2>Демо-доступ</h2>
        <p>Просмотр карты и состояния урн без регистрации</p>
      </div>
      <button class="action-btn" @click="guestLogin">Войти как гость</button>
      <div class="demo-note">
        <span class="role-badge">без пароля</span>
        <p>Вы сможете изучить карту этажей, цветовые индикаторы и детальную информацию об урнах.</p>
      </div>
    </div>

    <!-- Работник -->
    <div v-if="currentRole === 'worker'" class="tab-content active-content">
      <h3>Доступ сотрудника</h3>
      <div class="input-group">
        <label>Email</label>
        <input type="email" v-model="worker.email" placeholder="worker@smartbin.ru">
      </div>
      <div class="input-group">
        <label>Пароль</label>
        <input type="password" v-model="worker.password" placeholder="••••••••">
      </div>
      <div class="input-group">
        <label>Регистрационный ключ (для новых сотрудников)</label>
        <input type="text" v-model="worker.inviteKey" placeholder="Введите ключ сотрудника">
        <div class="reg-hint">Если вы уже зарегистрированы, ключ необязателен. При регистрации нужен ключ доступа.</div>
      </div>
      <button class="action-btn" @click="loginOrRegister('worker')" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Войти / Зарегистрироваться' }}
      </button>
      <div class="demo-note">
        Работник видит карту, список урн для уборки и может отмечать очистку.
      </div>
    </div>

    <!-- Администратор -->
    <div v-if="currentRole === 'admin'" class="tab-content active-content">
      <h3>Панель администратора</h3>
      <div class="input-group">
        <label>Email</label>
        <input type="email" v-model="admin.email" placeholder="admin@smartbin.ru">
      </div>
      <div class="input-group">
        <label>Пароль</label>
        <input type="password" v-model="admin.password" placeholder="••••••••">
      </div>
      <div class="input-group">
        <label>Административный ключ регистрации</label>
        <input type="text" v-model="admin.inviteKey" placeholder="Ключ для создания учетной записи админа">
        <div class="reg-hint">Требуется для регистрации новой роли администратора.</div>
      </div>
      <button class="action-btn" @click="loginOrRegister('admin')" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Войти как администратор' }}
      </button>
      <div class="demo-note">
        Полный доступ: управление урнами, пользователями, статистика и аналитика.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const currentRole = ref('guest')
const loading = ref(false)

const roles = ['guest', 'worker', 'admin']

const worker = ref({
  email: '',
  password: '',
  inviteKey: ''
})

const admin = ref({
  email: '',
  password: '',
  inviteKey: ''
})

const getRoleName = (role) => {
  const names = {
    guest: 'Гость',
    worker: 'Работник',
    admin: 'Администратор'
  }
  return names[role]
}

const guestLogin = () => {
  authStore.setGuestMode()
  router.push('/dashboard')
}

const loginOrRegister = async (role) => {
  loading.value = true
  
  const data = role === 'worker' ? worker.value : admin.value
  
  try {
    // Сначала пробуем войти
    let response = await authStore.login(data.email, data.password)
    
    if (!response.success && data.inviteKey) {
      // Если вход не удался и есть ключ - регистрируемся
      response = await authStore.register({
        username: data.email.split('@')[0],
        email: data.email,
        password: data.password,
        invite_key: data.inviteKey
      })
    }
    
    if (response.success) {
      // Перенаправляем на дашборд
      router.push('/dashboard')
    } else {
      showNotification(response.message || 'Ошибка входа', true)
    }
  } catch (error) {
    showNotification('Ошибка соединения с сервером', true)
  } finally {
    loading.value = false
  }
}

function showNotification(message, isError = false) {
  // Ваша реализация уведомлений
  alert(message) // Временно, потом замените на красивый тост
}
</script>

<style scoped>
/* Ваш CSS из HTML файла, адаптированный под Vue */
.login-card {
  background-color: #B2E9D8;
  border-radius: 48px;
  width: 100%;
  max-width: 500px;
  padding: 32px 28px 40px 28px;
  border: 2px solid #1A3A1A;
  box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.3);
}

.tabs {
  display: flex;
  gap: 10px;
  background: rgba(0, 69, 11, 0.08);
  padding: 6px;
  border-radius: 100px;
  margin-bottom: 32px;
}

.tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 8px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 40px;
  cursor: pointer;
  color: #00450B;
}

.tab-btn.active {
  background-color: #38EB2E;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.input-group {
  margin-bottom: 22px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #00450B;
}

input {
  background-color: #FEFCF5;
  border: 1.5px solid #1E3A1E;
  border-radius: 28px;
  padding: 14px 18px;
  font-size: 1rem;
  font-family: inherit;
  color: #00450B;
  outline: none;
}

input:focus {
  border-color: #38EB2E;
  box-shadow: 0 0 0 3px rgba(56, 235, 46, 0.3);
}

.action-btn {
  background-color: #38EB2E;
  border: none;
  border-radius: 40px;
  padding: 14px 20px;
  font-weight: 700;
  font-size: 1rem;
  color: #00450B;
  width: 100%;
  cursor: pointer;
  box-shadow: 0 6px 0 #0A5C08;
}

.action-btn:active {
  transform: translateY(4px);
  box-shadow: 0 2px 0 #0A5C08;
}

.reg-hint {
  font-size: 0.7rem;
  color: #00450B;
  opacity: 0.7;
  margin-top: -6px;
}

.demo-note {
  text-align: center;
  margin-top: 28px;
  font-size: 0.8rem;
  color: #00450B;
  border-top: 1px solid rgba(30, 58, 30, 0.4);
  padding-top: 20px;
}

.role-badge {
  background: rgba(0, 69, 11, 0.15);
  display: inline-block;
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.7rem;
  font-weight: 600;
}

.guest-welcome {
  text-align: center;
}

.guest-icon-symbol {
  font-size: 3rem;
  margin-bottom: 12px;
}
</style>