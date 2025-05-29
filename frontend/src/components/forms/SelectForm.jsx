import * as React from "react";
import Box from "@mui/material/Box";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";

export default function SelectForm({
  label,
  options = [], // Default to an empty array to avoid errors
  name,
  value,
  onChange,
  onBlur,
  error,
  helperText,
}) {
  return (
    <Box>
      <FormControl fullWidth>
        <InputLabel>{label}</InputLabel>
        <Select
          label={label}
          value={value}
          name={name}
          onChange={onChange}
          onBlur={onBlur}
          error={error}
        >
          {/* Default option to allow clearing the selection */}
          <MenuItem value="">
            None
          </MenuItem>
          {options.length > 0 ? (
            options.map((option) => (
              <MenuItem key={option.id} value={option.id}>
                {option.name}
              </MenuItem>
            ))
          ) : (
            <MenuItem disabled value="">
              No options available
            </MenuItem>
          )}
        </Select>
        {helperText && (
          <Box sx={{ color: "error.main", fontSize: "0.75rem", marginTop: "0.25rem" }}>
            {helperText}
          </Box>
        )}
      </FormControl>
    </Box>
  );
}
