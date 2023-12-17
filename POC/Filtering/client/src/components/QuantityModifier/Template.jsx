import React from 'react';
import useStyles from './styles';
import RemoveOutlinedIcon from '@mui/icons-material/RemoveOutlined';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import clsx from 'clsx';


const QuantityModifier = ({ max, min, style, onChange }) => {
  const [quantity, setQuantity] = React.useState(0);
  const classes = useStyles();

  React.useEffect(() => {
    onChange && onChange(quantity);
    // _.set(ref, 'current', quantity);
  }, [quantity, onChange]);

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
