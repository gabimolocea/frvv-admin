import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';


export default function TextForm({label, before, value, name, onChange, onBlur, error, helperText}) {
return (
    <Box>
        <TextField 
        id="outlined-basic" 
        label={label} 
        sx={{ width: '100%' }}
        variant="outlined" 
        value = {value}
        name = {name}
        onChange = {onChange}
        onBlur = {onBlur}
        error = {error}
        helperText = {helperText}
        slotProps={{
            input: {
              startAdornment: <InputAdornment position="start">{before}</InputAdornment>,
            },
          }}
        />
    </Box>
);
}