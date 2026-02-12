import { Box, TextField, Button, CircularProgress, Alert } from '@mui/material'
import { Save } from '@mui/icons-material'
import { ThemeListInput } from './ThemeListInput'

export function PromptConfigForm({
  validationPrompt,
  imagePrompt,
  themes,
  holidayMainTheme,
  onValidationPromptChange,
  onImagePromptChange,
  onThemesChange,
  onHolidayMainThemeChange,
  onSave,
  loading,
  error,
  success,
}) {
  const isFormValid =
    validationPrompt.trim() && imagePrompt.trim() && themes.length > 0 && holidayMainTheme.trim()

  return (
    <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <TextField
        label="Holiday Main Theme Name"
        value={holidayMainTheme}
        onChange={(e) => onHolidayMainThemeChange(e.target.value)}
        disabled={loading}
        fullWidth
        placeholder="e.g., New Year's Eve Party, Carnival, FIFA World Cup"
        helperText="This name will be displayed in the card generation UI (e.g., 'Generating Your Hero Card...')"
      />

      <TextField
        label="Validation Prompt"
        multiline
        rows={8}
        value={validationPrompt}
        onChange={(e) => onValidationPromptChange(e.target.value)}
        disabled={loading}
        fullWidth
        placeholder="Enter the validation prompt..."
        helperText="This prompt is used to validate user input before generating the card"
      />

      <TextField
        label="Image Generation Prompt"
        multiline
        rows={12}
        value={imagePrompt}
        onChange={(e) => onImagePromptChange(e.target.value)}
        disabled={loading}
        fullWidth
        placeholder="Enter the image generation prompt..."
        helperText="This prompt is used to generate the card image. Use {theme} placeholder for theme substitution."
      />

      <ThemeListInput themes={themes} onChange={onThemesChange} disabled={loading} />

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Configuration saved successfully!
        </Alert>
      )}

      <Button
        variant="contained"
        size="large"
        onClick={onSave}
        disabled={loading || !isFormValid}
        startIcon={loading ? <CircularProgress size={20} /> : <Save />}
        sx={{ mt: 2 }}
      >
        {loading ? 'Saving...' : 'Save Configuration'}
      </Button>
    </Box>
  )
}
