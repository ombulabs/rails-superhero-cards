import { Box, Container, Typography } from '@mui/material'
import { NavLink } from '../common/NavLink'
import { NAV_LINKS, COLORS } from '../../utils/constants'

export function Footer() {
  return (
    <Box
      sx={{
        bgcolor: COLORS.footerBg,
        color: 'white',
        py: 6,
        mt: 8,
        position: 'relative',
        zIndex: 1,
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center' }}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 1,
              mb: 4,
            }}
          >
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.href}
                href={link.href}
                color={COLORS.footerText}
                hoverColor={COLORS.primary}
              >
                {link.label}
              </NavLink>
            ))}
          </Box>

          <Typography variant="body2" sx={{ mb: 2, color: '#ccc' }}>
            Brought to you by
          </Typography>

          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
            <Box
              component="a"
              href="https://www.ombulabs.com"
              target="_blank"
              sx={{ display: 'block' }}
            >
              <Box component="img" src="/footer-logo.png" alt="OmbuLabs" sx={{ height: 50 }} />
            </Box>
          </Box>
        </Box>
      </Container>
    </Box>
  )
}
