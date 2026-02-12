import { Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { paths } from '../../routes/paths.jsx'

export default function LogoutButton() {
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate(paths.login())
  }

  return (
    <Button
      variant="contained"
      onClick={handleLogout}
      sx={{
        backgroundColor: 'brand.secondary',
        '&:hover': { opacity: 0.8 },
        pt: 1.2,
        pb: 1.2,
        px: 2,
        ml: 2,
      }}
    >
      Logout
    </Button>
  )
}
