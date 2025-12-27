import { Box, FormControlLabel, Switch, Typography } from '@mui/material'
import { AcUnit } from '@mui/icons-material'

export function HolidayToggle({ checked, onChange }) {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        bgcolor: checked ? '#f8f9fa' : 'transparent',
        borderRadius: 2,
        border: checked ? '2px solid #FFD700' : '2px solid transparent',
        transition: 'all 0.3s ease',
      }}
    >
      <FormControlLabel
        control={
          <Switch
            checked={checked}
            onChange={onChange}
            sx={{
              '& .MuiSwitch-switchBase.Mui-checked': {
                color: '#FFD700',
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: '#FFD700',
              },
            }}
          />
        }
        label={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AcUnit sx={{ color: checked ? '#FFD700' : '#666' }} />
            <Typography variant="body1" sx={{ fontWeight: checked ? 600 : 400 }}>
              🎆 New Year Theme
            </Typography>
          </Box>
        }
      />
    </Box>
  )
}
