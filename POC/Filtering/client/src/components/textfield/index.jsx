import React from 'react';
import {  InputAdornment,
  TextField } from '@mui/material'
import {  Controller } from 'react-hook-form';


export default function TTextField(props) {
  const {
    control,
    icon,
    rules,
    controllerExtras = {},
    isShowComma,
    setValue,
    ...other
  } = props;
  function getNumber(_str) {
    const arr = _str?.toString().split('');
    const out = [];
    if (arr.length) {
      for (let cnt = 0; cnt < arr.length; cnt++) {
        if (isNaN(arr[cnt]) === false) {
          out.push(arr[cnt]);
        }
      }
    }
    const num = Number(out.join(''));
    if (num === 0) {
      return '';
    }
    return num;
  }
  return (
    <Controller
      render={({
        field: { onChange, value, ...rest },
        fieldState: { invalid, isTouched, isDirty, error },
        formState,
      }) => (
        <TextField
          value={
            isShowComma ? getNumber(value ?? '')?.toLocaleString() : value || ''
          }
          onChange={(e) => {
            if (isShowComma) {
              const event = { ...e };
              const valueNumber = getNumber(e.target.value);
              event.target.value =
                valueNumber === 0 ? '' : valueNumber.toLocaleString();
              onChange(event);
              setValue && setValue(other.name, valueNumber);
            } else {
              onChange(e);
            }
          }}
          {...rest}
          {...other}
          InputProps={{
            endAdornment: icon && icon.ComponentRight && (
              <React.Fragment>
                {
                  <InputAdornment position="start">
                    {icon.ComponentRight}
                  </InputAdornment>
                }
              </React.Fragment>
            ),
            startAdornment: icon && icon.ComponentLeft && (
              <React.Fragment>
                {
                  <InputAdornment position="end">
                    {icon.ComponentLeft}
                  </InputAdornment>
                }
              </React.Fragment>
            ),
            ...other.InputProps,
          }}
        />
      )}
      name={other.name}
      control={control}
      rules={rules}
      {...controllerExtras}
    />
  );
}
