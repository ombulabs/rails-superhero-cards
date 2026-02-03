import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box, ThemeProvider } from '@mui/material'
import { theme } from './theme/theme'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Pipes } from './components/layout/Pipes'
import { HomePage } from './pages/HomePage'
import { AdminPage } from './pages/AdminPage'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Box sx={{ position: 'relative', overflow: 'hidden', minHeight: '100vh', bgcolor: 'white' }}>
          <Pipes />
          <Header />

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>

          <Footer />
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
