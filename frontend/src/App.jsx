import { useState, useEffect } from 'react'
import {
  Container,
  Box,
  Typography,
  ThemeProvider,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material'
import axios from 'axios'
import heic2any from 'heic2any'
import { theme } from './theme/theme'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Pipes } from './components/layout/Pipes'
import { HeroCardForm } from './components/form/HeroCardForm'
import { GeneratedCard } from './components/result/GeneratedCard'
import { VALID_IMAGE_TYPES } from './utils/constants'

function App() {
  const [skills, setSkills] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [imageProcessing, setImageProcessing] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [partialImage, setPartialImage] = useState(null)
  const [partialIndex, setPartialIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [holidayTheme, setHolidayTheme] = useState(false)
  const [holidayMessage, setHolidayMessage] = useState('')

  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const isHEICFile = (file) => {
      const isHEICType = file.type === 'image/heic' || file.type === 'image/heif'
      const isHEICExtension =
        file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif')
      return isHEICType || isHEICExtension
    }

    const isValidType = VALID_IMAGE_TYPES.includes(file.type) || isHEICFile(file)

    console.log('File upload debug:', {
      fileName: file.name,
      fileType: file.type,
      isHEIC: isHEICFile(file),
      isValidType: isValidType,
    })

    if (!isValidType) {
      setError('Please upload a PNG, JPG, or HEIC image. Other formats are not supported.')
      return
    }

    setError(null)
    setImageProcessing(true)

    try {
      let processedFile = file

      if (isHEICFile(file)) {
        console.log('HEIC file detected, starting conversion...')
        try {
          const convertedBlob = await heic2any({
            blob: file,
            toType: 'image/jpeg',
            quality: 0.9,
          })
          const jpegBlob = convertedBlob instanceof Blob ? convertedBlob : convertedBlob[0]
          processedFile = new File([jpegBlob], file.name.replace(/\.(heic|heif)$/i, '.jpg'), {
            type: 'image/jpeg',
            lastModified: Date.now(),
          })
          console.log('HEIC conversion successful')
        } catch (heicError) {
          console.error('HEIC conversion error:', heicError)
          setError('Failed to convert HEIC image. Please convert to JPG or PNG and try again.')
          setImageProcessing(false)
          return
        }
      }

      const maxSize = 4 * 1024 * 1024
      if (processedFile.size > maxSize) {
        setError('Image too large. Maximum size is 4MB.')
        setImageProcessing(false)
        return
      }

      setImageFile(processedFile)

      const reader = new FileReader()
      reader.onloadend = () => {
        if (reader.result) {
          setImagePreview(reader.result)
        }
        setImageProcessing(false)
      }
      reader.onerror = () => {
        setError('Failed to read image file')
        setImageProcessing(false)
      }
      reader.readAsDataURL(processedFile)
    } catch (err) {
      setError('Failed to process image. Please try a different file.')
      console.error('Image processing error:', err)
      setImageProcessing(false)
    }
  }

  const connectToStream = (sessionId, apiUrl) => {
    const eventSource = new EventSource(`${apiUrl}/stream/${sessionId}`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'partial') {
          setPartialImage(`data:image/png;base64,${data.image_base64}`)
          setPartialIndex(data.partial_index)
        } else if (data.type === 'complete') {
          setGeneratedImage(`data:image/png;base64,${data.image_base64}`)
          setPartialImage(null)
          setLoading(false)
          eventSource.close()
        } else if (data.type === 'error') {
          setError(data.message || 'Failed to generate hero card. Please try again.')
          setPartialImage(null)
          setLoading(false)
          eventSource.close()
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err, 'Raw data:', event.data)
      }
    }

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err, 'ReadyState:', eventSource.readyState)
      setError('Connection error. Please try again.')
      setPartialImage(null)
      setLoading(false)
      eventSource.close()
    }

    return () => eventSource.close()
  }

  const handleGenerate = async () => {
    if (holidayTheme) {
      if (!holidayMessage || !imageFile) {
        setError('Please add a holiday message and upload an image')
        return
      }
    } else {
      if (!skills || !imageFile) {
        setError('Please fill in your main skills and upload an image')
        return
      }
    }

    setLoading(true)
    setError(null)

    try {
      const sessionId = crypto.randomUUID()
      const formData = new FormData()
      formData.append('text', holidayTheme ? holidayMessage : skills)
      formData.append('image', imageFile)
      formData.append('session_id', sessionId)
      formData.append('holiday_theme', holidayTheme)

      const apiUrl = import.meta.env.VITE_API_URL || ''

      const response = await axios.post(`${apiUrl}/generate-hero-card`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.status === 202) {
        connectToStream(sessionId, apiUrl)
      } else {
        setGeneratedImage(`data:image/png;base64,${response.data.image_base64}`)
        setLoading(false)
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error ||
        'Uh oh. Something went wrong... Please try again or contact us.'
      setError(errorMessage)
      setPartialImage(null)
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!generatedImage) return

    try {
      const response = await fetch(generatedImage)
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)

      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `rails-hero-${Date.now()}.png`

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      setTimeout(() => URL.revokeObjectURL(blobUrl), 100)
    } catch (error) {
      console.error('Download error:', error)
      window.open(generatedImage, '_blank')
    }
  }

  const handleRegenerate = () => {
    setGeneratedImage(null)
    setPartialImage(null)
    setPartialIndex(0)
    setSkills('')
    setHolidayTheme(false)
    setHolidayMessage('')
    setImageFile(null)
    setImagePreview(null)
    setError(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ position: 'relative', overflow: 'hidden', minHeight: '100vh', bgcolor: 'white' }}>
        <Pipes />
        <Header />

        <Box sx={{ py: 8, position: 'relative', zIndex: 1 }}>
          <Container maxWidth="lg">
            <Box sx={{ textAlign: 'center', mb: 6 }}>
              <Typography variant="h1" component="h1" gutterBottom>
                Rails Superhero Card Generator
              </Typography>
              <Typography variant="h2" color="text.secondary">
                Get your Rails superhero card!
              </Typography>
            </Box>
          </Container>

          <Container maxWidth="md">
            {generatedImage ? (
              <GeneratedCard
                imageData={generatedImage}
                holidayTheme={holidayTheme}
                onDownload={handleDownload}
                onRegenerate={handleRegenerate}
              />
            ) : partialImage ? (
              <Card elevation={3}>
                <Box sx={{ p: 4 }}>
                  <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
                    {holidayTheme
                      ? '🎄 Generating Your Holiday Card...'
                      : '🦸 Generating Your Hero Card...'}
                  </Typography>

                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <img
                      src={partialImage}
                      alt="Partial preview"
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
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 2,
                      py: 2,
                    }}
                  >
                    <CircularProgress size={20} />
                    <Typography variant="body1" color="text.secondary">
                      {partialIndex === 1
                        ? '🎨 Working on your masterpiece...'
                        : partialIndex === 2
                          ? '⏳ Making it really awesome, one pixel at a time...'
                          : '✨ Hang on just a little longer, perfecting the details...'}
                    </Typography>
                  </Box>
                </Box>
              </Card>
            ) : (
              <HeroCardForm
                skills={skills}
                onSkillsChange={(e) => setSkills(e.target.value)}
                imageFile={imageFile}
                imagePreview={imagePreview}
                imageProcessing={imageProcessing}
                onImageUpload={handleImageUpload}
                loading={loading}
                error={error}
                onGenerate={handleGenerate}
                onErrorClose={() => setError(null)}
                holidayTheme={holidayTheme}
                onHolidayThemeChange={(e) => setHolidayTheme(e.target.checked)}
                holidayMessage={holidayMessage}
                onHolidayMessageChange={(e) => setHolidayMessage(e.target.value)}
              />
            )}
          </Container>
        </Box>

        <Footer />
      </Box>
    </ThemeProvider>
  )
}

export default App
