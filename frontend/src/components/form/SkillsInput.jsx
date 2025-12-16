import { Box, Typography, TextField } from '@mui/material'

export function SkillsInput({
  value,
  onChange,
  label = 'What cool stuff do you work on? What are your main Rails superhero skills?',
  placeholder = 'e.g., Building scalable web applications, creating developer tools...',
  helperText = '',
  maxLength = null,
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
