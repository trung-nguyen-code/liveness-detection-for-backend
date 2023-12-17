import React from 'react'
import _ from 'lodash'
import { Paper, Table, TableHead, TableRow, Box, TableContainer, TableCell, TableBody, Tooltip } from '@mui/material'
import moment from 'moment'
import { bodyMapping, fumesMapping, degreeMapping, familySituationMapping, religioutMapping, hasChildrenMapping, wantChildrenMapping, getOriginName, salatPratiqueMapping, eatHalalMapping, veilMapping } from '../../utils'
import { createNasPath } from '../../utils'
import { PHOTO_TYPE_BASE, PHOTO_SIZE_BIG } from '../../constants'

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
const PROFILE_URL = `https://www.mektoube.fr/main/profil/`

function LinkComponent({ userid }) {
    return (
        <Tooltip title="Click here to see user profile">
            <a target="_blank" style={{ color: '#000000' }} href={`${PROFILE_URL}${userid}`} rel="noreferrer">{userid}</a>
        </Tooltip>
    )
}

function transform(candidate) {
    let res = { ...candidate }
    if (Number.isInteger(candidate.body)) {
        _.set(res, 'body', bodyMapping[Number(candidate.body)])
    }
    if (Number.isInteger(candidate.religious)) {
        _.set(res, 'religious', religioutMapping[Number(candidate.religious)])
    }
    if (Number.isInteger(candidate.want_children)) {
        _.set(res, 'want_children', wantChildrenMapping[Number(candidate.want_children)])
    }
    if (Number.isInteger(candidate.has_children)) {
        _.set(res, 'has_children', hasChildrenMapping[Number(candidate.has_children)])
    }
    if (Number.isInteger(candidate.family_situation)) {
        _.set(res, 'family_situation', familySituationMapping[Number(candidate.family_situation)])
    }
    if (Number.isInteger(candidate.degree)) {
        _.set(res, 'degree', degreeMapping[Number(candidate.degree)])
    }
    if (Number.isInteger(candidate.fume)) {
        _.set(res, 'fume', fumesMapping[Number(candidate.fume)])
    }
    if (Number.isInteger(candidate.salat_pratique)) {
        _.set(res, 'salat_pratique', salatPratiqueMapping[Number(candidate.salat_pratique)])
    }
    if (Number.isInteger(candidate.eat_halal)) {
        _.set(res, 'eat_halal', eatHalalMapping[Number(candidate.eat_halal)])
    }
    if (Number.isInteger(candidate.veil)) {
        _.set(res, 'veil', veilMapping[Number(candidate.veil)])
    }
    if (Array.isArray(candidate.origin)) {
        _.set(res, 'origin', candidate.origin.map(id => getOriginName(id) ? getOriginName(Number(id)).code : '').join(', '))
    }
    return res
}

// function openProfileURL(userid) {
//     window.open(`${PROFILE_URL}${userid}`, '_blank')
// }

export default function TableList(props) {
    const { candidates, setCurrentViewImage, setIsOpenImage } = props

    return (
        <>
            {candidates && candidates.length > 0 ? <TableContainer style={{ maxHeight: 628, overflow: 'auto' }} component={Paper}>
                <Table aria-label="simple table">
                    <TableHead style={{ position: 'sticky', top: 0, left: 0, background: '#e1e1e1' }}>
                        <TableRow>
                            {candidates.length > 0 && Object.keys(candidates[0]).map((feature, index) => {
                                const label = capitalizeFirstLetter(feature.replaceAll("_", " "))
                                if (index === 0) {
                                    return <TableCell style={{ fontWeight: 'bold' }} key={label}>{label}</TableCell>
                                } else {
                                    return <TableCell style={{ fontWeight: 'bold' }} key={label} align="right">{label}</TableCell>
                                }
                            })}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {candidates.map((row) => {
                            console.log("row", row);
                            const transformedRow = transform(row)
                            return (
                                <TableRow
                                    key={transformedRow.candidate_id}
                                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                >
                                    {Object.keys(transformedRow).map((feature, index) => {
                                        if (feature === 'candidate_id') {
                                            return <TableCell key={feature} component="th" scope="row">{<LinkComponent userid={transformedRow[feature]} />}</TableCell>
                                        }
                                        else if (feature === 'photos' && row.photos) {
                                            return <TableCell key={feature} align="right">
                                                <img
                                                    height="70px"
                                                    width="70px"
                                                    alt='avatar'
                                                    style={{ cursor: 'pointer', borderRadius: '5px' }}
                                                    onClick={() => {
                                                        setCurrentViewImage(createNasPath({
                                                            id: row.candidate_id,
                                                            gender: row.id_genre,
                                                            photoId: row.photos.id_photo,
                                                            photoHash: row.photos.hash,
                                                            photoType: PHOTO_TYPE_BASE,
                                                            photoSize: PHOTO_SIZE_BIG
                                                        }))
                                                        setIsOpenImage(true)

                                                    }}
                                                    src={createNasPath({
                                                        id: row.candidate_id,
                                                        gender: row.id_genre,
                                                        photoId: row.photos.id_photo,
                                                        photoHash: row.photos.hash,
                                                        photoType: PHOTO_TYPE_BASE,
                                                        photoSize: PHOTO_SIZE_BIG
                                                    })} />
                                            </TableCell>
                                        }
                                        else if (feature === 'last_live_time' || feature === 'date_create' || feature === 'date_mise_avant') {
                                            return <TableCell key={feature} align="right">{transformedRow[feature] && moment(transformedRow[feature]).format('DD-MM-YYYY HH:mm')}</TableCell>
                                        }
                                        else {
                                            return <TableCell key={feature} align="right">{transformedRow[feature]}</TableCell>
                                        }

                                    })}
                                </TableRow>
                            )
                        })}
                    </TableBody>
                </Table>

            </TableContainer>
                : <Box display="flex" justifyContent="center">
                    <h3>No Data</h3>
                </Box>}
        </>
    )
}
