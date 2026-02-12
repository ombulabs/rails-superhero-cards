import { Box, Typography, TextField } from '@mui/material'

export function ThemedInput({
  value,
  onChange,
  holidayMainTheme,
  label = `Your ${holidayMainTheme} Message`,
  placeholder = `Happy ${holidayMainTheme} from the FastRuby.io team! 🎆`,
  helperText = `Add a ${holidayMainTheme} message for your best wishes card (max 30 characters)`,
  maxLength = 30,
}) {
  return (
    <Box>
      <Typography variant="body1" component="label" gutterBottom sx={{ display: 'block', mb: 1 }}>
        {label}
      </Typography>
      <TextField
        multiline
        rows={3}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        helperText={helperText}
        fullWidth
        inputProps={{
          maxLength: maxLength,
        }}
      />
    </Box>
  )
}
