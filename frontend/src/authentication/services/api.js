import axios from 'axios'
import { tokenStorage } from '../utils/tokenStorage'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export const authService = {
  loginWithGoogle: async (googleToken) => {
    const response = await axios.post(`${API_BASE_URL}/auth/google`, {
      google_token: googleToken,
    })

    return response.data
  },
  getCurrentUser: async (token) => {
    const response = await axios.get(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  },
  logout: async () => {
    tokenStorage.remove()
  },
}
