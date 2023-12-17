import React, { useEffect, useState } from 'react';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

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
import axios from 'axios'
import useDebounce from './hooks/useDebounce';

import './App.css'

const ENVIRONMENT = `http://51.91.137.230:5005/`
// const ENVIRONMENT = `http://localhost:5005/`

const PROFILE_URL = `https://www.mektoube.fr/main/profil/`


function LinkComponent({ userid }) {
  return (
    <Tooltip title="Click here to see user profile">
      <a target="_blank" style={{ color: '#000000' }} href={`${PROFILE_URL}${userid}`} rel="noreferrer">{userid}</a>
    </Tooltip>
  )

}

function App() {
  const [searchTerm, setSearchTerm] = useState(0);
  const [num, setNum] = useState(10)

  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const debouncedNum = useDebounce(num, 500);

  const [searchUser, setSearchUser] = useState(null)
  const [candidate, setCandidate] = useState([])
  const [url, setUrl] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const userids = `${ENVIRONMENT}static/userid/users.csv`


  async function fetchData(userid, num) {
    setIsLoading(true)
    const res = await axios.get(`${ENVIRONMENT}main?user_id=${userid}&num=${num}`)
    setSearchUser(res.data.a_user)
    setCandidate(res.data.candidates)
    setUrl(res.data.url)
    setIsLoading(false)

  }

  useEffect(
    () => {
      if (debouncedSearchTerm) {
        fetchData(debouncedSearchTerm, num)
      } else {
        setSearchUser(null)
        setCandidate([])
        setUrl(null)
      }
    },
    [debouncedSearchTerm] // Only call effect if debounced search term changes
  );
  useEffect(
    () => {
      if (debouncedNum && searchTerm) {
        fetchData(searchTerm, debouncedNum)
      } else {
        setSearchUser(null)
        setCandidate([])
        setUrl(null)
      }
    },
    [debouncedNum] // Only call effect if debounced search term changes
  );

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  return (
    <>
      <Box display="flex" justifyContent="center" marginTop="20px" marginBottom="20px">
        <h1>Content based Recommendation Demo</h1>
      </Box>
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
            onChange={e => setSearchTerm(e.target.value)}
          />
          <IconButton type="submit" sx={{ p: '10px' }} aria-label="search">
            <SearchIcon />
          </IconButton>
        </Paper>

        <TextField
          sx={{ width: 300, marginRight: 10 }}
          label="Number of similar user"
          placeholder="Number of similar user"
          inputProps={{ 'aria-label': 'numbe of similar' }}
          type="number"
          value={num}
          onChange={e => setNum(e.target.value)}
        />
        <Button style={{ textTransform: 'none', width: 200, height: 40 }} variant="contained" color="primary" href={userids} download>Download sample users</Button>

      </Box>
      <>
        {isLoading ? <Box style={{ position: 'fixed', height: '100vh', width: '100vw', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: 'transparent' }}>
          <CircularProgress />
        </Box> : null}
      </>
      <Grid container style={{ gap: 10, display: 'flex', justifyContent: 'center' }} >
        <Grid item sm={12} md={3}>
          <Card style={{ height: 628 }}>
            <CardHeader title={<div>{`Current search user:`} <LinkComponent userid={searchTerm} /> </div>} />
            <CardContent>
              {searchUser ? <List>
                {Object.keys(searchUser).map((feature) => {
                  const label = capitalizeFirstLetter(feature.replaceAll("_", " "))
                  return (
                    <ListItem>
                      {`${label}: ${searchUser[feature]}`}
                    </ListItem>
                  )
                })}
              </List>
                : <div>No Data</div>
              }
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
                      if (index === 0) {
                        return <TableCell key={index} component="th" scope="row">
                          {row[feature]}
                        </TableCell>
                      } else if (feature === 'candidate_id') {
                        return <TableCell key={index} align="right">{<LinkComponent userid={row[feature]} />}</TableCell>
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
      {url && <Box display="flex" justifyContent="center" marginTop="20px">
        <img src={`${ENVIRONMENT}${url}`} alt="Visualize" />
      </Box>
      }
    </>

  );
}

export default App;
