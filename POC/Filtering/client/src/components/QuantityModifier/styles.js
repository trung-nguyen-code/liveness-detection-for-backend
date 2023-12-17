import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme) => ({
  container: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    border: '1px solid #E3E5E6',
    padding: '.5rem',
    borderRadius: '12px',
    fontWeight: 'bold',
  },
  icon: {
    fontWeight: 'lighter',
    cursor: 'pointer',
  },
  activeIcon: {
    // color: `${theme.palette.secondary.main} !important`,
    // '&:hover': {
    //   color: `${theme.palette.secondary.main}`,
    // },
  },
  inactiveIcon: {
    color: '#CDCFD0',
    '&:hover': {
      color: '#CDCFD0',
    },
  },
}));

export default useStyles;
