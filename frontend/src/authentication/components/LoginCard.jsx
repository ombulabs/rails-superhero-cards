import { Stack, Typography } from '@mui/material'
import GoogleLoginButton from './GoogleLoginButton.jsx'

export default function LoginCard() {
  return (
    <Stack
      sx={{
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'column',
        borderWidth: 2,
        borderColor: 'primary.main',
        borderStyle: 'solid',
        borderRadius: 2,
        p: 4,
      }}
    >
      <Typography variant="h2" gutterBottom>
        Welcome
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Sign in with your @ombulabs.com Google account
      </Typography>

      <GoogleLoginButton />
    </Stack>
  )
}
