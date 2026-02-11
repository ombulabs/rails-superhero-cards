import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box, ThemeProvider } from '@mui/material'
import { theme } from './theme/theme'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Pipes } from './components/layout/Pipes'
import { HomePage } from './pages/HomePage'
import { AdminPage } from './pages/AdminPage'
import { LoginPage } from './pages/LoginPage'
import { AuthProvider, AdminRoute } from './authentication'
import { GoogleOAuthProvider } from '@react-oauth/google'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <AuthProvider>
          <BrowserRouter>
            <Box sx={{ position: 'relative', overflow: 'hidden', minHeight: '100vh', bgcolor: 'white' }}>
              <Pipes />
              <Header />

              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/admin"
                  element={
                    <AdminRoute>
                      <AdminPage />
                    </AdminRoute>
                  }
                />
              </Routes>

              <Footer />
            </Box>
          </BrowserRouter>
        </AuthProvider>
      </GoogleOAuthProvider>
    </ThemeProvider>
  )
}

export default App
