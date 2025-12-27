import { Box, Button, Card, CardContent, Typography } from '@mui/material'
import { Download, LinkedIn } from '@mui/icons-material'
import { COLORS } from '../../utils/constants'

export function GeneratedCard({ imageData, holidayTheme, onDownload, onRegenerate }) {
  const handleLinkedInShare = () => {
    const cardType = holidayTheme ? 'holiday card' : 'hero card'
    const message = `Get your ${cardType} at https://fastruby.io`
    const linkedInUrl = `https://www.linkedin.com/feed/?shareActive&mini=true&text=${encodeURIComponent(message)}`
    window.open(linkedInUrl, '_blank')
  }
  return (
    <Card elevation={3}>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
          {holidayTheme ? '🎆 Your New Year Card' : '🦸 Your Hero Card'}
        </Typography>

        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <img
            src={imageData}
            alt="Generated Hero Card"
            style={{
              maxWidth: '100%',
              maxHeight: '600px',
              width: 'auto',
              height: 'auto',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            }}
          />
        </Box>

        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'column', md: 'row' },
            gap: 2,
          }}
        >
          <Button
            variant="contained"
            fullWidth
            size="large"
            startIcon={<Download />}
            onClick={onDownload}
            sx={{
              py: { xs: 2, sm: 2, md: 1.5 },
              bgcolor: COLORS.primary,
              '&:hover': {
                bgcolor: COLORS.primaryHover,
              },
            }}
          >
            Download
          </Button>
          <Button
            variant="contained"
            fullWidth
            size="large"
            startIcon={<LinkedIn />}
            onClick={handleLinkedInShare}
            sx={{
              py: { xs: 2, sm: 2, md: 1.5 },
              bgcolor: '#0077B5',
              '&:hover': {
                bgcolor: '#005885',
              },
            }}
          >
            Share on LinkedIn
          </Button>
          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={onRegenerate}
            sx={{
              py: { xs: 2, sm: 2, md: 1.5 },
              bgcolor: COLORS.secondary,
              '&:hover': {
                bgcolor: COLORS.secondaryHover,
              },
            }}
          >
            Regenerate
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}
