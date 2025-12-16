import { createTheme } from '@mui/material'

export const theme = createTheme({
  typography: {
    fontFamily: '"Source Code Pro", monospace',
    h1: {
      fontWeight: 900,
      fontSize: '3rem',
      lineHeight: 1.08,
      letterSpacing: '1.18px',
      marginBottom: '2rem',
    },
    h2: {
      fontWeight: 900,
      fontSize: '2.5rem',
      lineHeight: 1.1,
      letterSpacing: '1px',
    },
    body1: {
      fontSize: '1.25rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.5px',
    },
    navLink: {
      fontSize: '1.125rem',
      fontWeight: 700,
      textDecoration: 'underline',
    },
  },
})
