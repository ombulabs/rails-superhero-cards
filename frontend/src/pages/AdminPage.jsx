import { useState, useEffect } from 'react'
import { Container, Box, Typography, Card, CardContent, CircularProgress } from '@mui/material'
import { PromptConfigForm } from '../components/admin/PromptConfigForm'
import { fetchPromptConfig, updatePromptConfig } from '../services/adminApi'

export function AdminPage() {
  const [validationPrompt, setValidationPrompt] = useState('')
  const [imagePrompt, setImagePrompt] = useState('')
  const [themes, setThemes] = useState([])
  const [holidayMainTheme, setHolidayMainTheme] = useState("New Year's Eve Party")
  const [loading, setLoading] = useState(false)
  const [loadingConfig, setLoadingConfig] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  // Load config when component mounts
  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoadingConfig(true)
      setError(null)
      setSuccess(false)

      const config = await fetchPromptConfig()

      setValidationPrompt(config.validation_prompt)
      setImagePrompt(config.image_prompt)
      setThemes(config.themes || [])
      setHolidayMainTheme(config.holiday_main_theme || "New Year's Eve Party")
    } catch (err) {
      setError('Failed to load configuration. Please try again.')
      console.error('Error loading config:', err)
    } finally {
      setLoadingConfig(false)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      setError(null)
      setSuccess(false)

      const configData = {
        validation_prompt: validationPrompt,
        image_prompt: imagePrompt,
        themes: themes,
        holiday_main_theme: holidayMainTheme,
      }

      await updatePromptConfig(configData)

      setSuccess(true)

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Failed to save configuration. Please try again.'
      setError(errorMessage)
      console.error('Error saving config:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ py: 8, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Container maxWidth="lg">
        <Box sx={{ mb: 6 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
            Admin Panel
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Manage prompt configurations for card generation
          </Typography>
        </Box>

        <Card elevation={3}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                Prompt Configuration
              </Typography>
            </Box>

            {loadingConfig ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
                <CircularProgress />
              </Box>
            ) : (
              <PromptConfigForm
                validationPrompt={validationPrompt}
                imagePrompt={imagePrompt}
                themes={themes}
                holidayMainTheme={holidayMainTheme}
                onValidationPromptChange={setValidationPrompt}
                onImagePromptChange={setImagePrompt}
                onThemesChange={setThemes}
                onHolidayMainThemeChange={setHolidayMainTheme}
                onSave={handleSave}
                loading={loading}
                error={error}
                success={success}
              />
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  )
}
