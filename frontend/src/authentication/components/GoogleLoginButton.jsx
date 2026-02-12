import { GoogleLogin } from '@react-oauth/google'
import { Alert, Box } from '@mui/material'
import { useGoogleLogin } from '../hooks/useGoogleLogin.js'

export default function GoogleLoginButton() {
  const { handleGoogleSuccess, handleGoogleError, error, loading } = useGoogleLogin()

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          You cannot access the Admin Panel.
          <br />
          Please contact an administrator.
        </Alert>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={loading}
          text="signin_with"
          shape="rectangular"
          size="large"
        />
      </Box>
    </Box>
  )
}
