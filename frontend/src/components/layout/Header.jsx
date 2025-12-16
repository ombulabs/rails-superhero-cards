import { useState } from 'react'
import {
  Box,
  Container,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material'
import { Menu as MenuIcon, Close as CloseIcon } from '@mui/icons-material'
import { NavLink } from '../common/NavLink'
import { NAV_LINKS } from '../../utils/constants'
import { COLORS } from '../../utils/constants'

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  return (
    <Box sx={{ bgcolor: 'transparent', py: 3, position: 'relative', zIndex: 1 }}>
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Logo - responsive */}
          <Box
            component="img"
            src="/header-logo.png"
            alt="FastRuby.io"
            sx={{
              height: { xs: 50, md: 60 },
              content: {
                xs: 'url(/header-logo-small.png)',
                md: 'url(/header-logo.png)',
              },
            }}
          />

          {/* Desktop Navigation */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 4 }}>
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.href}
                href={link.href}
                color={COLORS.headerLink}
                hoverColor={COLORS.headerLinkHover}
              >
                {link.label}
              </NavLink>
            ))}
          </Box>

          {/* Mobile Hamburger Menu */}
          <IconButton
            sx={{ display: { xs: 'block', md: 'none' }, color: COLORS.headerLink }}
            onClick={toggleMobileMenu}
            aria-label="menu"
          >
            <MenuIcon />
          </IconButton>
        </Box>
      </Container>

      {/* Mobile Drawer */}
      <Drawer anchor="right" open={mobileMenuOpen} onClose={toggleMobileMenu}>
        <Box sx={{ width: 250, pt: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', px: 2 }}>
            <IconButton onClick={toggleMobileMenu} aria-label="close menu">
              <CloseIcon />
            </IconButton>
          </Box>
          <List>
            {NAV_LINKS.map((link) => (
              <ListItem key={link.href} disablePadding>
                <ListItemButton
                  component="a"
                  href={link.href}
                  sx={{
                    '&:hover': {
                      bgcolor: 'rgba(16, 191, 122, 0.08)',
                    },
                  }}
                >
                  <ListItemText
                    primary={link.label}
                    sx={{
                      '& .MuiTypography-root': {
                        fontWeight: 600,
                        color: COLORS.headerLink,
                      },
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </Box>
  )
}
