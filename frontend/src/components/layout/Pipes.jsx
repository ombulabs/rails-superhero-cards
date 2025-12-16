import { Box } from '@mui/material'
import { COLORS } from '../../utils/constants'

export function Pipes() {
  return (
    <>
      {/* Yellow/Gold Left Side */}
      <Box
        component="svg"
        sx={{
          position: 'absolute',
          top: 280,
          left: -30,
          width: 250,
          height: 600,
          zIndex: 0,
          display: { xs: 'none', lg: 'block' }, // Hide on mobile/tablet/iPad, show on desktop (1200px+)
        }}
        viewBox="0 0 250 600"
        fill="none"
      >
        <circle cx="150" cy="50" r="35" fill="white" stroke={COLORS.yellow} strokeWidth="8" />
        <line x1="150" y1="85" x2="150" y2="520" stroke={COLORS.yellow} strokeWidth="20" />
        <path d="M 150 520 Q 150 570 100 570" fill="none" stroke={COLORS.yellow} strokeWidth="20" />
        <line x1="100" y1="570" x2="0" y2="570" stroke={COLORS.yellow} strokeWidth="20" />
      </Box>

      {/* Green Right Side */}
      <Box
        component="svg"
        sx={{
          position: 'absolute',
          top: 100,
          right: -30,
          width: 250,
          height: 700,
          zIndex: 0,
          display: { xs: 'none', lg: 'block' }, // Hide on mobile/tablet/iPad, show on desktop (1200px+)
        }}
        viewBox="0 0 250 700"
        fill="none"
      >
        <path
          d="M 80 0 L 80 400 Q 80 500 160 500 L 250 500"
          fill="none"
          stroke={COLORS.primary}
          strokeWidth="20"
        />
      </Box>
    </>
  )
}
