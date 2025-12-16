import { useState, useEffect } from 'react'
import { Container, Box, Typography, ThemeProvider } from '@mui/material'
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

  const pollTaskStatus = async (taskId, apiUrl) => {
    const maxAttempts = 60 // Poll for up to 5 minutes (60 * 5 seconds)
    let attempts = 0

    const poll = async () => {
      try {
        const statusResponse = await axios.get(`${apiUrl}/status/${taskId}`)
        const { status, image_base64, status_description } = statusResponse.data

        if (status === 'complete' && image_base64) {
          setGeneratedImage(`data:image/png;base64,${image_base64}`)
          setLoading(false)
          return
        }

        if (status === 'error') {
          setError(status_description || 'Failed to generate hero card. Please try again.')
          setLoading(false)
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000) // Poll every 5 seconds
        } else {
          setError('Card generation is taking longer than expected. Please try again later.')
          setLoading(false)
        }
      } catch (err) {
        setError('Something went wrong. Please try again or contact us.')
        setLoading(false)
      }
    }

    poll()
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
      const formData = new FormData()
      formData.append('text', holidayTheme ? holidayMessage : skills)
      formData.append('image', imageFile)
      formData.append('session_id', crypto.randomUUID())
      formData.append('holiday_theme', holidayTheme)

      const apiUrl = import.meta.env.VITE_API_URL || ''

      const response = await axios.post(`${apiUrl}/generate-hero-card`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.status === 202 && response.data.task_id) {
        pollTaskStatus(response.data.task_id, apiUrl)
      } else {
        setGeneratedImage(`data:image/png;base64,${response.data.image_base64}`)
        setLoading(false)
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error ||
        'Uh oh. Something went wrong... Please try again or contact us.'
      setError(errorMessage)
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
            {!generatedImage ? (
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
            ) : (
              <GeneratedCard
                imageData={generatedImage}
                holidayTheme={holidayTheme}
                onDownload={handleDownload}
                onRegenerate={handleRegenerate}
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
