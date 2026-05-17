import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiService from '../services/apiService'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const userRole = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  async function login(username, password) {
    try {
      // API ожидает username, а не email
      const response = await apiService.login(username, password)
      if (response.access_token) {
        token.value = response.access_token
        user.value = response.user
        userRole.value = response.user.role
        isAuthenticated.value = true
        localStorage.setItem('token', token.value)
        return { success: true }
      }
      return { success: false, message: 'Ошибка входа' }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, message: error.response?.data?.detail || 'Ошибка входа' }
    }
  }

  async function register(userData) {
    try {
      const response = await apiService.register(
        userData.username,
        userData.email,
        userData.password,
        userData.invite_key
      )
      if (response.access_token) {
        token.value = response.access_token
        user.value = response.user
        userRole.value = response.user.role
        isAuthenticated.value = true
        localStorage.setItem('token', token.value)
        return { success: true }
      }
      return { success: false, message: 'Ошибка регистрации' }
    } catch (error) {
      console.error('Register error:', error)
      return { success: false, message: error.response?.data?.detail || 'Неверный инвайт-ключ' }
    }
  }

  function setGuestMode() {
    user.value = { role: 'guest', username: 'Гость' }
    userRole.value = 'guest'
    isAuthenticated.value = true
    token.value = null
    localStorage.removeItem('token')
  }

  function logout() {
    apiService.logout()
    user.value = null
    isAuthenticated.value = false
    userRole.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  function getRoleName() {
    const role = user.value?.role
    const roleNames = {
      'admin': 'Администратор',
      'worker': 'Работник',
      'guest': 'Гость'
    }
    return roleNames[role] || 'Неизвестно'
  }

  return {
    user,
    isAuthenticated,
    userRole,
    token,
    login,
    getRoleName,
    register,
    setGuestMode,
    logout
  }
})