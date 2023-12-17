import React from 'react';

import {   FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormLabel,
  FormHelperText, } from '@mui/material'
import {  Controller } from 'react-hook-form';
import useStyles from './styles';
import clsx from 'clsx';

export default function AppRadioGroup(props) {
  const {
    control,
    error,
    helperText,
    label,
    icon,
    rules,
    values,
    disabled,
    margin,
    color,
    controllerExtras = {},
    style,
    className,
    ...other
  } = props;
  const classes = useStyles({ margin });

  return (
    <Controller
      render={({ field, ...rest }) => (
        <FormControl
          component="fieldset"
          error={error}
          disabled={Boolean(disabled)}
          className={clsx(classes.formControl, className)}
          style={style}
        >
          <FormLabel component="legend">{label}</FormLabel>
          <RadioGroup {...other} value={field.value} onChange={field.onChange}>
            {values.map(({ label, value }, index) => (
              <FormControlLabel
                key={index}
                value={value}
                control={<Radio color={color || 'primary'} />}
                label={label}
              />
            ))}
          </RadioGroup>
          <FormHelperText>{helperText}</FormHelperText>
        </FormControl>
      )}
      name={other.name}
      control={control}
      rules={rules}
      {...controllerExtras}
    />
  );
}
