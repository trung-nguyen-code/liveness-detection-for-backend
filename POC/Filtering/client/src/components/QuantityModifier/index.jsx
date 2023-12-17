import React from 'react';
import useStyles from './styles';
import RemoveOutlinedIcon from '@mui/icons-material/RemoveOutlined';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import clsx from 'clsx';
import QuantityModifierTemplate from './Template';


const QuantityModifier = ({
  max,
  min,
  style,
  watch,
  setValue,
  name,
}) => {
  var quantity = watch(name) ?? min;
  const setQuantity = (value) => setValue(name, value);

  const classes = useStyles();

  const updateQuantity = (newQuantity) => {
    if (typeof min === 'number' && newQuantity < min) return;
    if (typeof max === 'number' && newQuantity > max) return;
    setQuantity(newQuantity);
  };

  return (
    <div
      className={classes.container}
      style={{
        minWidth: '140px',
        ...style,
      }}
    >
      <RemoveOutlinedIcon
        onClick={() => updateQuantity(quantity - 1)}
        className={clsx({
          [classes.icon]: true,
          [classes.inactiveIcon]: true,
          [classes.activeIcon]:
            typeof min === 'number' && quantity - 1 < min ? false : true,
        })}
      />
      <span>{quantity}</span>
      <AddOutlinedIcon
        onClick={() => updateQuantity(quantity + 1)}
        className={clsx({
          [classes.icon]: true,
          [classes.inactiveIcon]: true,
          [classes.activeIcon]:
            typeof max === 'number' && quantity + 1 > max ? false : true,
        })}
      />
    </div>
  );
};

export default QuantityModifier;

export { QuantityModifierTemplate };
