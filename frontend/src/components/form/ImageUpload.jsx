import { Box, Button, Paper, Tooltip, IconButton, CircularProgress } from '@mui/material'
import { CloudUpload, InfoOutlined } from '@mui/icons-material'

export function ImageUpload({ onImageUpload, imagePreview, imageProcessing, disabled }) {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Button
          variant="outlined"
          component="label"
          startIcon={<CloudUpload />}
          fullWidth
          disabled={imageProcessing || disabled}
        >
          Upload Your Photo
          <input
            type="file"
            hidden
            accept="image/*"
            onChange={onImageUpload}
            disabled={imageProcessing || disabled}
          />
        </Button>
        <Tooltip
          title="We DO NOT store your uploaded images. Only the generated superhero cards are saved."
          arrow
          placement="right"
        >
          <IconButton size="small" sx={{ color: '#666' }}>
            <InfoOutlined fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {imageProcessing && (
        <Paper
          elevation={1}
          sx={{
            p: 2,
            textAlign: 'center',
            minHeight: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress />
            <Box sx={{ color: 'text.secondary', fontSize: '14px' }}>Processing image...</Box>
          </Box>
        </Paper>
      )}

      {!imageProcessing && imagePreview && (
        <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
          {imagePreview === 'heic-placeholder' ? (
            <Box
              sx={{
                minHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                gap: 1,
                color: 'text.secondary',
              }}
            >
              <CloudUpload sx={{ fontSize: 48, opacity: 0.5 }} />
              <Box>HEIC image uploaded</Box>
              <Box sx={{ fontSize: '12px' }}>(Preview not available)</Box>
            </Box>
          ) : (
            <img
              src={imagePreview}
              alt="Preview"
              style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '8px' }}
            />
          )}
        </Paper>
      )}
    </Box>
  )
}
