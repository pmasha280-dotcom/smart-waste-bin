import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:3000/api'

export const binService = {
  async getFloors() {
    try {
      const response = await axios.get(`${API_BASE_URL}/floors`)
      return response.data
    } catch (error) {
      console.error('Error fetching floors:', error)
      throw error
    }
  },
  
  async getBinsByFloor(floorId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/floors/${floorId}/bins`)
      return response.data
    } catch (error) {
      console.error('Error fetching bins:', error)
      throw error
    }
  },
  
  async updateBinData(binId, data) {
    try {
      const response = await axios.put(`${API_BASE_URL}/bins/${binId}`, data)
      return response.data
    } catch (error) {
      console.error('Error updating bin:', error)
      throw error
    }
  }
}