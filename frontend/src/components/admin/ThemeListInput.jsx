import { useState } from 'react'
import {
  Box,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Typography,
  Button,
} from '@mui/material'
import { Delete, Add } from '@mui/icons-material'

export function ThemeListInput({ themes, onChange, disabled = false }) {
  const [newTheme, setNewTheme] = useState('')

  const handleAddTheme = () => {
    if (newTheme.trim()) {
      onChange([...themes, newTheme.trim()])
      setNewTheme('')
    }
  }

  const handleRemoveTheme = (index) => {
    const updatedThemes = themes.filter((_, i) => i !== index)
    onChange(updatedThemes)
  }

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleAddTheme()
    }
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Themes
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Add a theme (e.g., Champagne Toast)"
          value={newTheme}
          onChange={(e) => setNewTheme(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
        />
        <Button
          variant="contained"
          onClick={handleAddTheme}
          disabled={!newTheme.trim() || disabled}
          startIcon={<Add />}
          sx={{ minWidth: 'auto' }}
        >
          Add
        </Button>
      </Box>

      {themes.length > 0 ? (
        <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1, border: '1px solid #e0e0e0' }}>
          {themes.map((theme, index) => (
            <ListItem key={index} divider={index < themes.length - 1}>
              <ListItemText
                primary={theme}
                primaryTypographyProps={{
                  variant: 'body2',
                }}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleRemoveTheme(index)}
                  disabled={disabled}
                  size="small"
                >
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
          No themes added yet. Add at least one theme.
        </Typography>
      )}
    </Box>
  )
}
