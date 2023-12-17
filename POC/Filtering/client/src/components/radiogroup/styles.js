import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme) => ({
  formControl: {
    marginTop: ({ margin }) =>
      margin === 'normal' ? theme.spacing(1) : 0,
  },
}));

export default useStyles;
