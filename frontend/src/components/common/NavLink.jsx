import { Typography } from '@mui/material'

export function NavLink({ href, children, color, hoverColor }) {
  return (
    <Typography
      component="a"
      href={href}
      target="_blank"
      variant="navLink"
      sx={{
        color,
        '&:hover': {
          color: hoverColor,
        },
      }}
    >
      {children}
    </Typography>
  )
}
