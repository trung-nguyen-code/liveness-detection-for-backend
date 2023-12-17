import axios from 'axios'
import React, { useState, useEffect } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import { Grid, Box, Paper, InputBase, IconButton, CircularProgress, Tooltip, FormControl, InputLabel, Select, MenuItem } from '@mui/material'
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import SettingsIcon from '@mui/icons-material/Settings';
import SearchIcon from '@mui/icons-material/Search';
import useDebounce from './hooks/useDebounce';

// import SearchSetting from './components/SearchSetting'
import UserProfile from './components/UserProfile'
import TableList from './components/TableList'
import SearchModal from './components/SearchModal'
import ImageModal from './components/ViewAvatarModal'

import { result, search_options } from './data'

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const BASE_URL = process.env.REACT_APP_BASE_URL || "https://ai.mektou.be/api"
// export const BASE_URL = 'http://localhost:8000'


export default function App() {
  const [searchTerm, setSearchTerm] = useState(0);
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const [searchOption, setSearchOption] = useState({})
  const [total, setTotal] = useState(0)
  const [isOpenSnackbar, setIsOpenSnackbar] = useState(false)
  const [openSearchModal, setOpenSearchModal] = useState(false)
  const [candidates, setCandidates] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpenImage, setIsOpenImage] = useState(false)
  const [currentViewImage, setCurrentViewImage] = useState(null)
  const isMobile = useMediaQuery('(max-width:450px)');

  const [group, setGroup] = React.useState(1);

  const handleGroupChange = (event) => {
    setGroup(event.target.value);
  };

  async function recommend(userId) {
    try {
      setIsLoading(true)
      const res = await axios.get(`${BASE_URL}/recommend/${userId}`, {
        headers: {
          'Authorization': `Bearer ${process.env.REACT_APP_TOKEN}`
        }
      }, {
      })
      if (res.status === 200) {
        setCandidates(res.data.result)
        setSearchOption(res.data.search_options)
        setTotal(res.data.total)
        setIsLoading(false)
        setIsOpenSnackbar(true)
      }
    } catch (error) {
      setIsLoading(false)
      setCandidates([])
      setSearchOption({})
      setTotal(0)
    }
  }
  async function similarSearch(userId) {
    // setIsLoading(false)
    // setCandidates(result)
    // setSearchOption(search_options)
    try {
      setIsLoading(true)
      const res = await axios.post(`${BASE_URL}/recommend_search`, [
        userId
      ])
      if (res.status === 200) {
        console.log("res", res.data[0]);
        setCandidates(res.data[0].response)
        setSearchOption(res.data[0].search_options)
        setTotal(res.data.match_count)
        setIsLoading(false)
        setIsOpenSnackbar(true)
      }
    } catch (error) {
      setIsLoading(false)
      setCandidates([])
      setSearchOption({})
      setTotal(0)
    }
  }

  useEffect(
    () => {
      if (debouncedSearchTerm) {
        group === 1 && recommend(debouncedSearchTerm)
        group === 2 && similarSearch(debouncedSearchTerm)
      }
      isMobile ? document.body.style.overflow = "auto" : document.body.style.overflow = "hidden"
    },

    [debouncedSearchTerm, isMobile, group] // Only call effect if debounced search term changes
  );

  function handleCloseAlert(event, reason) {
    if (reason === 'clickaway') {
      return;
    }
    setIsOpenSnackbar(false);
  }

  function handleOpenSearch() {
    setOpenSearchModal(true)
  }
  function handleCloseSearch() {
    setOpenSearchModal(false)
  }

  return (
    <>
      <SearchModal open={openSearchModal} handleClose={handleCloseSearch} />
      <ImageModal open={isOpenImage} setIsOpenImage={setIsOpenImage} image={currentViewImage} handleClose={() => setIsOpenImage(false)} />
      <Grid container spacing={3} padding="10px" style={{ overflow: 'hidden' }}>
        <Grid item xs={12} md={2}>
          <UserProfile group={group} searchOptions={searchOption} />
        </Grid>
        <Grid item xs={12} md={10} >
          <Box display="flex" justifyContent="center" marginTop="20px" marginBottom="20px">
            <h1>Recommendation Demo</h1>
          </Box>
          <Box display="flex" justifyContent="center" marginTop="20px" marginBottom="20px" gap={5}>
            <Paper
              component="form"
              sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', width: 400 }}
            >
              <InputBase
                sx={{ ml: 1, flex: 1 }}
                placeholder="Search User ID"
                inputProps={{ 'aria-label': 'Search User ID' }}
                type="number"
                onChange={e => setSearchTerm(e.target.value)}
              />
              <SearchIcon />
            </Paper>

            <FormControl>
              <InputLabel id="demo-simple-select-label">Group</InputLabel>
              <Select
                value={group}
                label="Group"
                onChange={handleGroupChange}
              >
                <MenuItem value={1}>Group 1</MenuItem>
                <MenuItem value={2}>Group 2</MenuItem>
                <MenuItem value={3}>Group 3</MenuItem>
              </Select>
            </FormControl>
            <Tooltip title="Search setting" placement="top">
              <IconButton onClick={handleOpenSearch}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            {/* <Button variant='contained' style={{ textTransform: 'none' }}>Search Setting</Button> */}
          </Box>
          {isLoading ? <Box display="flex" justifyContent="center">
            <CircularProgress size={40} />
          </Box> : <TableList candidates={candidates} setIsOpenImage={setIsOpenImage} setCurrentViewImage={setCurrentViewImage} />}
        </Grid>
      </Grid>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={isOpenSnackbar}
        severity="success"
        autoHideDuration={2000}
        onClose={handleCloseAlert}
      >
        <Alert severity="success">Search successfully</Alert>
      </Snackbar>
    </>
  );
}
