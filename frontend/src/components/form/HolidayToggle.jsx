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
        border: checked ? '2px solid #d32f2f' : '2px solid transparent',
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
                color: '#d32f2f',
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: '#d32f2f',
              },
            }}
          />
        }
        label={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AcUnit sx={{ color: checked ? '#d32f2f' : '#666' }} />
            <Typography variant="body1" sx={{ fontWeight: checked ? 600 : 400 }}>
              🎄 Holiday Theme
            </Typography>
          </Box>
        }
      />
    </Box>
  )
}
