import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const adminApi = axios.create({
  baseURL: `${API_BASE_URL}/admin`,
  headers: {
    'Content-Type': 'application/json',
  },
})

const publicApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Fetch the public configuration (holiday_main_theme only)
 * @returns {Promise<Object>} Public config data
 */
export const fetchPublicConfig = async () => {
  try {
    const response = await publicApi.get('/config')
    return response.data
  } catch (error) {
    console.error('Error fetching public config:', error)
    throw error
  }
}

/**
 * Fetch the prompt configuration
 * @returns {Promise<Object>} Config data
 */
export const fetchPromptConfig = async () => {
  try {
    const response = await adminApi.get('/prompt-config')
    return response.data
  } catch (error) {
    console.error('Error fetching prompt config:', error)
    throw error
  }
}

/**
 * Update the prompt configuration
 * @param {Object} configData - The configuration data to update
 * @param {string} [configData.validation_prompt] - Validation prompt text
 * @param {string} [configData.image_prompt] - Image generation prompt text
 * @param {Array<string>} [configData.themes] - List of themes
 * @param {string} [configData.holiday_main_theme] - Holiday main theme name for card display
 * @returns {Promise<Object>} Updated config
 */
export const updatePromptConfig = async (configData) => {
  try {
    const response = await adminApi.put('/prompt-config', configData)
    return response.data
  } catch (error) {
    console.error('Error updating prompt config:', error)
    throw error
  }
}
