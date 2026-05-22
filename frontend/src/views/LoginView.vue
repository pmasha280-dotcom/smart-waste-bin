<template>
  <div class="login-container">
    <!-- Кнопка гостевого входа вверху -->
    <div class="guest-banner">
      <button class="guest-btn" @click="guestLogin">
        🎭 Войти как гость (без регистрации)
      </button>
    </div>

    <div class="login-card">
      <div class="tabs">
        <button 
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >
          Вход
        </button>
        <button 
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'"
        >
          Регистрация
        </button>
      </div>

      <!-- ФОРМА ВХОДА -->
      <div v-if="mode === 'login'" class="form-container">
        <h2>Вход в систему</h2>
        <div class="input-group">
          <label>Имя пользователя</label>
          <input type="text" v-model="loginForm.username" placeholder="admin">
        </div>
        <div class="input-group">
          <label>Пароль</label>
          <input type="password" v-model="loginForm.password" placeholder="••••••••">
        </div>
        <button class="action-btn" @click="handleLogin" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </div>

      <!-- ФОРМА РЕГИСТРАЦИИ -->
      <div v-if="mode === 'register'" class="form-container">
        <div class="role-tabs">
          <button 
            v-for="role in roles" 
            :key="role"
            class="role-btn" 
            :class="{ active: selectedRole === role }"
            @click="selectedRole = role"
          >
            {{ getRoleName(role) }}
          </button>
        </div>

        <h3>Регистрация {{ getRoleName(selectedRole).toLowerCase() }}</h3>
        
        <div class="input-group">
          <label>Имя пользователя</label>
          <input type="text" v-model="registerForm.username" placeholder="username">
        </div>
        <div class="input-group">
          <label>Email</label>
          <input type="email" v-model="registerForm.email" placeholder="user@example.com">
        </div>
        <div class="input-group">
          <label>Пароль</label>
          <input type="password" v-model="registerForm.password" placeholder="••••••••">
        </div>
        <div class="input-group">
          <label>Инвайт-ключ</label>
          <input type="text" v-model="registerForm.inviteKey" placeholder="Введите ключ доступа">
          <div class="reg-hint">Получите ключ у администратора</div>
        </div>
        <button class="action-btn" @click="handleRegister" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
        <p v-if="registerError" class="error">{{ registerError }}</p>
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

const mode = ref('login')
const loading = ref(false)
const loginError = ref('')
const registerError = ref('')
const selectedRole = ref('worker')

const roles = ['worker', 'admin']

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  inviteKey: ''
})

const getRoleName = (role) => {
  const names = {
    worker: 'Работник',
    admin: 'Администратор'
  }
  return names[role] || role
}

// Гостевой вход (без регистрации, только просмотр)
const guestLogin = () => {
  authStore.setGuestMode()
  router.push('/dashboard')
}

// Вход в систему
const handleLogin = async () => {
  loading.value = true
  loginError.value = ''
  
  try {
    const response = await authStore.login(loginForm.value.username, loginForm.value.password)
    if (response.success) {
      router.push('/dashboard')
    } else {
      loginError.value = response.message || 'Неверное имя пользователя или пароль'
    }
  } catch (err) {
    loginError.value = 'Ошибка соединения с сервером'
  } finally {
    loading.value = false
  }
}

// Регистрация
const handleRegister = async () => {
  loading.value = true
  registerError.value = ''
  
  try {
    const response = await authStore.register({
      username: registerForm.value.username,
      email: registerForm.value.email,
      password: registerForm.value.password,
      invite_key: registerForm.value.inviteKey
    })
    
    if (response.success) {
      router.push('/dashboard')
    } else {
      registerError.value = response.message || 'Ошибка регистрации. Неверный инвайт-ключ.'
    }
  } catch (err) {
    registerError.value = 'Ошибка соединения с сервером'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.guest-banner {
  margin-bottom: 20px;
  text-align: center;
}

.guest-btn {
  background: linear-gradient(135deg, #38EB2E, #28B520);
  border: none;
  border-radius: 50px;
  padding: 14px 28px;
  font-size: 1.1rem;
  font-weight: bold;
  color: #00450B;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
}

.guest-btn:hover {
  transform: scale(1.02);
}

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

.tabs button {
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

.tabs button.active {
  background-color: #38EB2E;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.role-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.role-btn {
  flex: 1;
  background: #EAE6C7;
  border: 1px solid #1A3A1A;
  padding: 8px;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 600;
  color: #00450B;
}

.role-btn.active {
  background-color: #38EB2E;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.form-container h2, .form-container h3 {
  text-align: center;
  color: #00450B;
  margin-bottom: 24px;
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

.error {
  color: red;
  text-align: center;
  margin-top: 16px;
  font-size: 0.85rem;
}
</style>
