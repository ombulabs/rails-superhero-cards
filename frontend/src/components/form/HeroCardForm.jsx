import { Box, Button, Card, CardContent, CircularProgress, Alert } from '@mui/material'
import { AutoAwesome } from '@mui/icons-material'
import { SkillsInput } from './SkillsInput'
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
}) {
  return (
    <Card elevation={3}>
      <CardContent sx={{ p: 4 }}>
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <HolidayToggle checked={holidayTheme} onChange={onHolidayThemeChange} />

          {holidayTheme ? (
            <SkillsInput
              value={holidayMessage}
              onChange={onHolidayMessageChange}
              label="Your Holiday Message"
              placeholder="Merry Christmas from the Fastruby.io team! 🎄"
              helperText="Add a festive message for your holiday card (max 30 characters)"
              maxLength={30}
            />
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
              bgcolor: holidayTheme ? '#d32f2f' : COLORS.primary,
              '&:hover': {
                bgcolor: holidayTheme ? '#b71c1c' : COLORS.primaryHover,
              },
            }}
          >
            {loading
              ? holidayTheme
                ? 'Generating Your Holiday Card...'
                : 'Generating Your Hero Card...'
              : holidayTheme
                ? '🎄 Generate Holiday Card'
                : 'Generate Hero Card'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}
