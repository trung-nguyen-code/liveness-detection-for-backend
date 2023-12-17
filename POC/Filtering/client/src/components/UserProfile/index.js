import React, { useState, useEffect } from 'react'
import { Box, Avatar, Typography } from '@mui/material'
import ContactsIcon from '@mui/icons-material/ContactsOutlined';
import { capitalizeFirstLetter } from '../SearchModal'
import {
    bodyMapping,
    localisationMapping,
    familySituationMapping,
    religioutMapping,
    degreeMapping,
    hasChildrenMapping,
    wantChildrenMapping,
    fumesMapping,
    getOriginName,
    createNasPath,
    salatPratiqueMapping,
    veilMapping,
    eatHalalMapping,
} from '../../utils'
import { PHOTO_TYPE_BASE, PHOTO_SIZE_BIG } from '../../constants'
import { ManProfileIcon } from './man-profile'
import { WomanProfileIcon } from './woman-profile'
// const searchOptions = {
//     "id_genre": "2",
//     "longitude": "0.0939173887803",
//     "latitude": "0.755674333571",
//     "taille_begin": 150,
//     "taille_end": 230,
//     "age_begin": 18,
//     "age_end": 40,
//     "family_situation": [
//         0
//     ],
//     "has_children": [],
//     "want_children": 1,
//     "religious": 1,
//     "degree": [
//         0
//     ],
//     "fumes": [],
//     "body": [
//         1,
//         2,
//         3,
//         4
//     ],
//     "id_localisation": [
//         2
//     ],
//     "dept_code": "13",
//     "pays_code": "FR",
//     "region_code": "93",
//     "geoname_id": 2995469
// }

function TextBox(props) {
    return <div style={{
        background: props.background,
        border: `1px solid ${props.background}`,
        borderRadius: 5,
        textAlign: 'center',
        height: 21,
        width: 'auto',
        display: 'flex',
        justifyContent:
            'center',
        alignItems: 'center',
        padding: '0 8px'
    }}>
        <Box style={{
            height: '100%',
            color: 'white', fontSize: 12, display: 'flex',
            justifyContent:
                'center',
            alignItems: 'center',
        }}>
            {props.text}
        </Box>
    </div>
}

function UserSummary(props) {
    const { searchOptions } = props
    return (
        <>
            {searchOptions && <>
                <Box gap="5px" display="flex" flexDirection="column" borderBottom="1px solid gray" padding="10px">
                    <Box display="flex" alignItems="center" gap="10px">
                        <ContactsIcon />
                        <b>Summary</b>
                    </Box>
                    {searchOptions.id_utilisateur && searchOptions.id_utilisateur !== 0 && <Box display="flex" alignItems="center" gap="10px">
                        <TextBox text={searchOptions.id_utilisateur} background="#000" />
                        <TextBox text={searchOptions.actif ? 'Active' : 'Unactive'} background="#28a745" />
                        <TextBox text={searchOptions.app_origin === 1 ? 'Mashallah' : 'Mektoube'} background="#3c8dbc" />

                    </Box>
                    }
                    <Box gap="5px" display="flex" height="auto" width="100%" >
                        <b>Age: </b>
                        <p style={{ fontWeight: 300, margin: 0 }}>{searchOptions.age}</p>
                    </Box>
                    <Box gap="5px" display="flex" height="auto" width="100%" >
                        <b>Height: </b>
                        <p style={{ fontWeight: 300, margin: 0 }}>{searchOptions.size}</p>
                    </Box>



                </Box>
                {searchOptions.accroche && searchOptions.accroche !== '' && <Box height="80px" overflow="auto" width="100%">
                    <p style={{ fontWeight: 300, margin: 0 }}>
                        {searchOptions.accroche}
                    </p>
                </Box>}
            </>}
        </>

    )
}

function Feature(props) {
    return (
        <Box gap="5px" display="flex" flexDirection="column" height="auto" width="100%" borderBottom="1px solid gray" padding="5px 10px">
            <b>{props.label}</b>
            <p style={{ fontWeight: 300, margin: 0 }}>{props.value}</p>
        </Box>
    )
}

export default function UserProfile(props) {
    const { searchOptions, group } = props
    const [groups, setGroups] = useState([])

    useEffect(() => {
        if (searchOptions) {
            const ageGroup = [{ label: 'min_age', value: searchOptions['min_age'] }, { label: 'max_age', value: searchOptions['max_age'] }]
            const sizeGroup = [{ label: 'min_tall', value: searchOptions['min_tall'] }, { label: 'max_tall', value: searchOptions['max_tall'] }]
            const locationGroup = [{ label: 'longitude', value: searchOptions['longitude'] }, { label: 'latitude', value: searchOptions['latitude'] }]
            const childrenGroup = [{ label: 'has_children', value: searchOptions['has_children'] }, { label: 'want_children', value: searchOptions['want_children'] }]
            const localisationGroup = [
                { label: 'id_localisation', value: searchOptions['id_localisation'] },
                { label: 'family_situation', value: searchOptions['family_situation'] },
            ]
            const rawGroups = [
                ageGroup,
                sizeGroup,
                locationGroup,
                childrenGroup,
                localisationGroup,
                [{ label: 'region_code', value: searchOptions['region_code'] }, { label: 'dept_code', value: searchOptions['dept_code'] }],
                [{ label: 'pays_code', value: searchOptions['pays_code'] }, { label: 'geoname_id', value: searchOptions['geoname_id'] }],
                [{ label: 'pratiquant', value: searchOptions['pratiquant'] }, { label: 'study_level', value: searchOptions['study_level'] }],
                [{ label: 'fume', value: searchOptions['fume'] }, { label: 'figure', value: searchOptions['figure'] }],
                [{ label: 'id_origine', value: searchOptions['id_origine'] }, { label: 'salat_pratique', value: searchOptions['salat_pratique'] }],
                [{ label: 'eat_halal', value: searchOptions['eat_halal'] }, { label: 'veil', value: searchOptions['veil'] }]
            ]
            const mappedGroups = rawGroups.map(group => {
                return group.map(item => {
                    if (item.label === 'figure') {
                        return {
                            label: 'figure',
                            value: Array.isArray(item.value) ? item.value.map(val => bodyMapping[Number(val)]) : bodyMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'id_localisation') {
                        return {
                            label: 'id_localisation',
                            value: Array.isArray(item.value) ? item.value.map(val => localisationMapping[Number(val)]) : localisationMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'family_situation') {
                        return {
                            label: 'family_situation',
                            value: Array.isArray(item.value) ? item.value.map(val => familySituationMapping[Number(val)]) : familySituationMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'pratiquant') {
                        return {
                            label: 'pratiquant',
                            value: Array.isArray(item.value) ? item.value.map(val => religioutMapping[Number(val)]) : religioutMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'study_level') {
                        return {
                            label: 'study_level',
                            value: Array.isArray(item.value) ? item.value.map(val => degreeMapping[Number(val)]) : degreeMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'has_children') {
                        return {
                            label: 'has_children',
                            value: Array.isArray(item.value) ? item.value.map(val => hasChildrenMapping[Number(val)]) : hasChildrenMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'want_children') {
                        return {
                            label: 'want_children',
                            value: Array.isArray(item.value) ? item.value.map(val => wantChildrenMapping[Number(val)]) : wantChildrenMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'fume') {
                        return {
                            label: 'fume',
                            value: Array.isArray(item.value) ? item.value.map(val => fumesMapping[Number(val)]) : fumesMapping[Number(item.value)]
                        }
                    }
                    if (item.label === 'id_origine') {
                        if (item.value) {
                            return {
                                label: 'id_origine',
                                value: Array.isArray(item.value) ? item.value.map(val => getOriginName(Number(val))?.code) : getOriginName(Number(item.value).code)
                            }
                        }

                    }
                    if (item.label === 'salat_pratique') {
                        if (item.value) {
                            return {
                                label: 'salat_pratique',
                                value: Array.isArray(item.value) ? item.value.map(val => salatPratiqueMapping[Number(val)]) : salatPratiqueMapping[Number(item.value)]
                            }
                        }
                        console.log("item.value", Array.isArray(item.value) ? item.value.map(val => salatPratiqueMapping[Number(val)]) : salatPratiqueMapping[Number(item.value)]);
                    }
                    if (item.label === 'eat_halal') {
                        if (item.value) {
                            return {
                                label: 'eat_halal',
                                value: Array.isArray(item.value) ? item.value.map(val => eatHalalMapping[Number(val)]) : eatHalalMapping[Number(item.value)]
                            }
                        }

                    }
                    if (item.label === 'veil') {
                        if (item.value) {
                            return {
                                label: 'veil',
                                value: Array.isArray(item.value) ? item.value.map(val => veilMapping[Number(val)]) : veilMapping[Number(item.value)]
                            }
                        }

                    }
                    return item
                })
            })
            setGroups(mappedGroups)
        }
    }, [searchOptions])

    return (
        <Box display="flex" flexDirection="column" gap="10px">
            <Box width="100%" height="220px" style={{ backgroundColor: searchOptions.id_genre === 1 ? '#298d4b' : '#f67f7f' }} display="flex" justifyContent="center" alignItems="center">
                <Box display="flex" flexDirection="column" alignItems="center" >
                    {searchOptions?.photos?.id_photo ? <Avatar style={{ border: '2px solid #ffffff', marginBottom: 20 }} alt="Remy Sharp" sx={{ width: 78, height: 80 }}
                        src={createNasPath({
                            id: searchOptions.id_utilisateur,
                            gender: searchOptions.id_genre,
                            photoId: searchOptions.photos.id_photo,
                            photoHash: searchOptions.photos.hash,
                            photoType: PHOTO_TYPE_BASE,
                            photoSize: PHOTO_SIZE_BIG
                        })} />
                        : <div style={{ background: '#FFFFFF', width: 80, height: 80, borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                            <span>{searchOptions.id_genre === 1 ? <ManProfileIcon size={38} /> : <WomanProfileIcon size={38} />}</span>
                        </div>
                    }
                    <Typography variant='h5' style={{ color: 'white', fontWeight: 'bold' }}>{searchOptions.pseudo}</Typography>
                    <Typography style={{ color: 'white' }}>{searchOptions.email}</Typography>
                </Box>
            </Box>
            <UserSummary searchOptions={searchOptions} />
            <Box height="500px" style={{ overflowY: 'auto' }}>

                {groups.map((group, index) => {
                    return (
                        <Box key={index} display="flex" gap="5px">
                            {group.map(feature => {
                                return <Feature key={feature.label} value={Array.isArray(feature.value) ? feature.value.join(', ') : feature.value} label={capitalizeFirstLetter(feature.label.replace("_", ' '))} />
                            })}
                        </Box>
                    )
                })}
            </Box>
            {/* {Object.keys(searchOptions).map((key, index) => {
                return <Feature value={searchOptions[key]} label={capitalizeFirstLetter(key.replace("_", ' '))} />
            })} */}
        </Box>

    )
}
