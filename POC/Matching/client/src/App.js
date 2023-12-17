import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import InputBase from '@mui/material/InputBase';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import { Button, TextField, CircularProgress, Tooltip } from '@mui/material';

import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import axios from 'axios'
// import useDebounce from './hooks/useDebounce';

import './App.css'

// const ENVIRONMENT = `http://51.91.137.230:5005/`
// const ENVIRONMENT = `http://localhost:5005/`
const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});
const PROFILE_URL = `https://www.mektoube.fr/main/profil/`


function LinkComponent({ userid }) {
  return (
    <Tooltip title="Click here to see user profile">
      <a target="_blank" style={{ color: '#000000' }} href={`${PROFILE_URL}${userid}`} rel="noreferrer">{userid}</a>
    </Tooltip>
  )
}

function FilterDialog(props) {
  const [error, setError] = React.useState(false);
  const [errorText, setErrorText] = React.useState("");


  const { context, setContext, setCandidate, open, setOpen, setIsLoading } = props

  async function onSubmit() {
    setIsLoading(true)
    try {
      const res = await axios.post(`https://ai.mektou.be/recommend/${context.user_id}`, {}, {
        headers: {
          'Authorization': `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwiaWF0IjoxNjU3MTYxMDI5LCJuYmYiOjE2NTcxNjEwMjksImp0aSI6Ijg0NDEwNzY3LTNmOGEtNDc0NC1iMzAxLTZlODRkODdiMDE3ZiIsInR5cGUiOiJhY2Nlc3MiLCJmcmVzaCI6ZmFsc2V9.OW2cOXdbYIyNFF9YcUgIjcRswAMqYAjE2RoVx8p3cuo`
        }
      })
      if (res.status === 200) {
        setCandidate(res.data)
        setOpen(false)
        setIsLoading(false)
      }
    } catch (error) {
      setIsLoading(false)
      setError(true)

      setErrorText(error.response.data)
    }
  }
  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setError(false);
    setErrorText("")
  };


  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <Snackbar open={error} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="error" sx={{ width: '100%' }}>
          {errorText}
        </Alert>
      </Snackbar>
      <DialogTitle id="alert-dialog-title">
        {"Fill in user search context"}
      </DialogTitle>
      <DialogContent>
        <TextField
          label="User ID"
          variant="outlined"
          margin="normal"
          fullWidth
          type="number"
          id="userid"
          value={context['user_id']}
          onChange={(e) => {
            setContext({ ...context, user_id: e.target.value })
          }}
        />

        <Button variant='contained' color="primary" onClick={onSubmit}>Submit</Button>
      </DialogContent>

    </Dialog>
  )
}

function App() {
  // const [searchTerm, setSearchTerm] = useState(0);
  // const [num, setNum] = useState(10)

  const [candidate, setCandidate] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const [open, setOpen] = useState(false)

  const [context, setContext] = useState({
    user_id: 0,
  })


  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  return (
    <>
      <Box display="flex" justifyContent="center" marginTop="20px" marginBottom="20px">
        <h1>Recommendation Demo</h1>
      </Box>
      <FilterDialog
        context={context}
        setContext={setContext}
        setCandidate={setCandidate}
        open={open}
        setOpen={setOpen}
        setIsLoading={setIsLoading}
      />
      <Box display="flex" justifyContent="center" marginTop="20px" marginBottom="20px">
        <Paper
          component="form"
          sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', width: 400, marginRight: 10 }}
        >
          <InputBase
            sx={{ ml: 1, flex: 1 }}
            placeholder="Search User ID"
            inputProps={{ 'aria-label': 'Search User ID' }}
            type="number"
            onClick={() => {
              setOpen(true)
            }}
          // onChange={e => setSearchTerm(e.target.value)}
          />
          <IconButton type="submit" sx={{ p: '10px' }} aria-label="search">
            <SearchIcon />
          </IconButton>
        </Paper>

        {/* <TextField
          sx={{ width: 300, marginRight: 10 }}
          label="Number of similar user"
          placeholder="Number of similar user"
          inputProps={{ 'aria-label': 'numbe of similar' }}
          type="number"
          value={num}
          onChange={e => setNum(e.target.value)}
        /> */}
        {/* <Button style={{ textTransform: 'none', width: 200, height: 40 }} variant="contained" color="primary" href={userids} download>Download sample users</Button> */}

      </Box>
      <>
        {isLoading ? <Box style={{ position: 'fixed', height: '100vh', width: '100vw', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: 'transparent' }}>
          <CircularProgress />
        </Box> : null}
      </>
      <Grid container style={{ gap: 10, display: 'flex', justifyContent: 'center' }} >
        <Grid item sm={12} md={3}>
          <Card style={{ height: 628 }}>
            <CardHeader title={<div>{`Current search user:`} <LinkComponent userid={context.user_id} /> </div>} />
            <CardContent>
              {context ? <List>
                {Object.keys(context).map((feature) => {
                  const label = capitalizeFirstLetter(feature.replaceAll("_", " "))
                  return (
                    <ListItem>
                      {`${label}: ${context[feature]}`}
                    </ListItem>
                  )
                })}
              </List>
                : <div>No Data</div>
              }
              {/* <div>No Data</div> */}
            </CardContent>
          </Card>
        </Grid>
        <Grid item sm={12} md={8}>
          {candidate.length > 0 ? <TableContainer style={{ maxHeight: 628, overflow: 'auto' }} component={Paper}>
            <Table sx={{ minWidth: 650 }} aria-label="simple table">
              <TableHead style={{ position: 'sticky', top: 0, left: 0, background: '#e1e1e1' }}>
                <TableRow>
                  {candidate.length > 0 && Object.keys(candidate[0]).map((feature, index) => {
                    const label = capitalizeFirstLetter(feature.replaceAll("_", " "))
                    if (index === 0) {
                      return <TableCell style={{ fontWeight: 'bold' }} key={index}>{label}</TableCell>
                    } else {
                      return <TableCell style={{ fontWeight: 'bold' }} key={index} align="right">{label}</TableCell>
                    }
                  })}
                </TableRow>
              </TableHead>
              <TableBody>
                {candidate.map((row) => (
                  <TableRow
                    key={row.name}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    {Object.keys(row).map((feature, index) => {
                      if (feature === 'candidate_id') {
                        console.log("here");
                        return <TableCell key={index} component="th" scope="row">{<LinkComponent userid={row[feature]} />}</TableCell>
                      }
                      else {
                        return <TableCell key={index} align="right">{row[feature]}</TableCell>
                      }

                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>

          </TableContainer>
            : <Box display="flex" justifyContent="center">
              <h3>No Data</h3>
            </Box>}
        </Grid>
      </Grid>
      {/* {url && <Box display="flex" justifyContent="center" marginTop="20px">
        <img src={`${ENVIRONMENT}${url}`} alt="Visualize" />
      </Box>
      } */}
    </>

  );
}

export default App;
