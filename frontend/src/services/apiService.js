import axios from 'axios'

const API_BASE_URL = '/api'

const apiService = {
  async post(url, data) {
    try {
      const response = await axios.post(`${API_BASE_URL}${url}`, data)
      return response
    } catch (error) {
      throw error
    }
  },

  async get(url) {
    try {
      const response = await axios.get(`${API_BASE_URL}${url}`)
      return response
    } catch (error) {
      throw error
    }
  },

  async put(url, data) {
    try {
      const response = await axios.put(`${API_BASE_URL}${url}`, data)
      return response
    } catch (error) {
      throw error
    }
  },

  async delete(url) {
    try {
      const response = await axios.delete(`${API_BASE_URL}${url}`)
      return response
    } catch (error) {
      throw error
    }
  },

  // Аутентификация
  async login(username, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        username,
        password
      })
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        this.setAuthHeader(response.data.access_token)
      }
      return response.data
    } catch (error) {
      console.error('Ошибка входа:', error)
      throw error
    }
  },

  async demoLogin() {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/demo`)
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        this.setAuthHeader(response.data.access_token)
      }
      return response.data
    } catch (error) {
      console.error('Ошибка демо-входа:', error)
      throw error
    }
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  },

  setAuthHeader(token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  // Получить все этажи
  async getFloors() {
    try {
      const response = await axios.get(`${API_BASE_URL}/floors`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения этажей:', error)
      throw error
    }
  },

  // Получить урны по этажу
  async getBinsByFloor(floorId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/bins`, {
        params: { floor_id: floorId }
      })
      return response.data
    } catch (error) {
      console.error(`Ошибка получения урн для этажа ${floorId}:`, error)
      throw error
    }
  },

  // Получить данные конкретной урны
  async getBinData(binId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/bins/${binId}`)
      return response.data
    } catch (error) {
      console.error(`Ошибка получения данных урны ${binId}:`, error)
      throw error
    }
  },

  // Отметить очистку урны
  async cleanBin(binId, floorId, notes = '') {
    try {
      const response = await axios.post(`${API_BASE_URL}/bins/${binId}/clean`, {
        floorId,
        timestamp: new Date().toISOString(),
        notes
      })
      return response.data
    } catch (error) {
      console.error('Ошибка отметки очистки:', error)
      throw error
    }
  },

  // Получить статистику
  async getStatistics(days = 7) {
    try {
      const response = await axios.get(`${API_BASE_URL}/statistics`, {
        params: { days }
      })
      return response.data
    } catch (error) {
      console.error('Ошибка получения статистики:', error)
      throw error
    }
  },

  // Админские методы
  async getAllUsers() {
    try {
      const response = await axios.get(`${API_BASE_URL}/users`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения пользователей:', error)
      throw error
    }
  },

  async createUser(userData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/users`, userData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания пользователя:', error)
      throw error
    }
  },

  async deleteUser(userId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/users/${userId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка удаления пользователя:', error)
      throw error
    }
  },

  async createBin(binData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/bins`, binData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания урны:', error)
      throw error
    }
  },

  async updateBin(binId, binData) {
    try {
      const response = await axios.put(`${API_BASE_URL}/bins/${binId}`, binData)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления урны:', error)
      throw error
    }
  },

  async deleteBin(binId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/bins/${binId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка удаления урны:', error)
      throw error
    }
  },

  checkAuth() {
    const token = localStorage.getItem('token')
    if (token) {
      this.setAuthHeader(token)
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user
    }
    return null
  }
}

const token = localStorage.getItem('token')
if (token) {
  apiService.setAuthHeader(token)
}

export default apiService
