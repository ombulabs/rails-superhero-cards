import { Box, Button, Card, CardContent, CircularProgress, Alert } from '@mui/material'
import { AutoAwesome } from '@mui/icons-material'
import { SkillsInput } from './SkillsInput'
import { ThemedInput } from './ThemedInput'
import { ImageUpload } from './ImageUpload'
import { HolidayToggle } from './HolidayToggle'
import { COLORS } from '../../utils/constants'

export function HeroCardForm({
  skills,
  onSkillsChange,
  imageFile,
  imagePreview,
  imageProcessing,
  onImageUpload,
  loading,
  error,
  onGenerate,
  onErrorClose,
  holidayTheme,
  onHolidayThemeChange,
  holidayMessage,
  onHolidayMessageChange,
  holidayMainTheme,
}) {
  return (
    <Card elevation={3}>
      <CardContent sx={{ p: 4 }}>
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <HolidayToggle checked={holidayTheme} onChange={onHolidayThemeChange} holidayMainTheme={holidayMainTheme} />

          {holidayTheme ? (
            <ThemedInput value={holidayMessage} onChange={onHolidayMessageChange} holidayMainTheme={holidayMainTheme} />
          ) : (
            <SkillsInput value={skills} onChange={onSkillsChange} />
          )}

          <ImageUpload
            onImageUpload={onImageUpload}
            imagePreview={imagePreview}
            imageProcessing={imageProcessing}
            disabled={loading}
          />

          {error && (
            <Alert severity="error" onClose={onErrorClose}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            onClick={onGenerate}
            disabled={
              loading ||
              (!holidayTheme && !skills) ||
              (holidayTheme && !holidayMessage) ||
              !imageFile
            }
            startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
            sx={{
              py: 1.5,
              bgcolor: holidayTheme ? '#FFD700' : COLORS.primary,
              '&:hover': {
                bgcolor: holidayTheme ? '#FFC700' : COLORS.primaryHover,
              },
            }}
          >
            {loading
              ? holidayTheme
                ? `Generating Your ${holidayMainTheme} Card...`
                : 'Generating Your Super Hero Card...'
              : holidayTheme
                ? `🎆 Generate ${holidayMainTheme} Card`
                : 'Generate Super Hero Card'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}
