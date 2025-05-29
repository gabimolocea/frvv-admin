import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import { Typography } from '@mui/material';

export default function MyMessage({messageText, messageColor}) {
return (
    <Box
        sx={{
        width: '100%', 
        height: '100%', 
        color: 'white', 
        marginBottom: '20px', 
        padding: '10px', 
        display: 'flex',
        backgroundColor: messageColor,
        alignItems: 'center',
        }}
    >
       <Typography>{messageText}</Typography>
    </Box>
);
} 