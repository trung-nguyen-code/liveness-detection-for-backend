import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Button, Card, CardContent, ListItem, Box, CircularProgress, InputLabel, Input, TextField } from '@mui/material'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AppRadioGroup from '../radiogroup'
import QuantityModifier from '../QuantityModifier'
import { BASE_URL } from '../../App'

import { useForm } from "react-hook-form";

const searchValue = [{ label: 'Exact Match', value: 'false' }, { label: 'Score Function', value: 'true' }]
const searchSettings = ['religious', 'salat_pratique', 'veil', 'eat_halal', 'want_children', 'has_children', 'family_situation', 'degree', 'fume', 'body', 'localisation']

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function stringToBoolean(string) {
    return string === 'true'
}

export default function SearchSetting(props) {
    const { searchOption, searchTerm, total } = props
    const [isExpand, setIsExpand] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const { register, handleSubmit, watch, formState: { errors }, control, reset,
        setValue
    } = useForm({
        defaultValues: {
            localisation: {
                setting_type: 'false',
                score: 10
            },
            religious: {
                setting_type: 'false',
                score: 10
            },
            salat_pratique: {
                setting_type: 'false',
                score: 10
            },
            veil: {
                setting_type: 'false',
                score: 10
            },
            eat_halal: {
                setting_type: 'false',
                score: 10
            },
            want_children: {
                setting_type: 'false',
                score: 10
            },
            has_children: {
                setting_type: 'false',
                score: 10
            },
            family_situation: {
                setting_type: 'false',
                score: 10
            },
            degree: {
                setting_type: 'false',
                score: 10
            },
            fume: {
                setting_type: 'false',
                score: 10
            },
            body: {
                setting_type: 'false',
                score: 10
            },
            age_score: 10,
            size_score: 10,
            push_forward_score: 10,
            distance_score: 10,
            last_connection_score: 10,
            seniority_score: 10,
            photos_score: 10,
            profile_filling_score: 10,
        }
    });
    async function fetchData() {
        const result = await axios.get(`${BASE_URL}/settings`)
        reset({
            ...result.data,
            localisation: {
                setting_type: result.data.localisation.setting_type.toString(),
                score: Number(result.data.localisation.score)
            },
            religious: {
                setting_type: result.data.religious.setting_type.toString(),
                score: Number(result.data.religious.score)
            },
            salat_pratique: {
                setting_type: result.data.salat_pratique.setting_type.toString(),
                score: Number(result.data.salat_pratique.score)
            },
            veil: {
                setting_type: result.data.veil.setting_type.toString(),
                score: Number(result.data.veil.score)
            },
            eat_halal: {
                setting_type: result.data.eat_halal.setting_type.toString(),
                score: Number(result.data.eat_halal.score)
            },
            want_children: {
                setting_type: result.data.want_children.setting_type.toString(),
                score: Number(result.data.want_children.score)
            },
            has_children: {
                setting_type: result.data.has_children.setting_type.toString(),
                score: Number(result.data.has_children.score)
            },
            family_situation: {
                setting_type: result.data.family_situation.setting_type.toString(),
                score: Number(result.data.family_situation.score)
            },
            degree: {
                setting_type: result.data.degree.setting_type.toString(),
                score: Number(result.data.degree.score)
            },
            fume: {
                setting_type: result.data.fume.setting_type.toString(),
                score: Number(result.data.fume.score)
            },
            body: {
                setting_type: result.data.body.setting_type.toString(),
                score: Number(result.data.body.score)
            },
        })
        setIsLoading(false)
    }
    useEffect(() => {
        setIsLoading(true)

        fetchData()
    }, [])
    const handleChange = (event, isExpanded) => {
        setIsExpand(isExpanded);
    };
    const onSubmit = async (data) => {
        setIsLoading(true)
        const res = await axios.post(`${BASE_URL}/settings`, {
            ...data,
            localisation: {
                setting_type: stringToBoolean(data.localisation.setting_type),
                score: data.localisation.score
            },
            religious: {
                setting_type: stringToBoolean(data.religious.setting_type),
                score: data.religious.score
            },
            salat_pratique: {
                setting_type: stringToBoolean(data.salat_pratique.setting_type),
                score: data.salat_pratique.score
            },
            veil: {
                setting_type: stringToBoolean(data.veil.setting_type),
                score: data.veil.score
            },
            eat_halal: {
                setting_type: stringToBoolean(data.eat_halal.setting_type),
                score: data.eat_halal.score
            },
            want_children: {
                setting_type: stringToBoolean(data.want_children.setting_type),
                score: data.want_children.score
            },
            has_children: {
                setting_type: stringToBoolean(data.has_children.setting_type),
                score: data.has_children.score
            },
            family_situation: {
                setting_type: stringToBoolean(data.family_situation.setting_type),
                score: data.family_situation.score
            },
            degree: {
                setting_type: stringToBoolean(data.degree.setting_type),
                score: data.degree.score
            },
            fume: {
                setting_type: stringToBoolean(data.fume.setting_type),
                score: data.fume.score
            },
            body: {
                setting_type: stringToBoolean(data.body.setting_type),
                score: data.body.score
            },
            origin: {
                setting_type: stringToBoolean(data.origin.setting_type),
                score: data.origin.score
            },
        }, {})
        if (res.data) {
            setIsLoading(false)
            fetchData()
        } else {
            setIsLoading(false)
        }
    }


    return (
        <>
            <Accordion expanded={isExpand} onChange={handleChange}>
                <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls="panel1a-content"
                    id="panel1a-header"
                >
                    <Typography>Search Setting</Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Card>
                        <CardContent>
                            <form onSubmit={handleSubmit(onSubmit)}>
                                <Box display="flex" flexDirection="column" style={{ height: 400, overflowY: 'auto' }} marginBottom="10px">
                                    {searchSettings.map((setting, index) => {
                                        if (setting.includes('_')) {
                                            return (
                                                <Box key={index} >
                                                    <Typography>
                                                        {capitalizeFirstLetter(setting.replace("_", ' '))}
                                                    </Typography>
                                                    <Box display="flex" alignItems="center" style={{ gap: 10 }} width="397px" justifyContent="space-between">
                                                        <AppRadioGroup name={`${setting}.setting_type`} control={control} values={searchValue} />
                                                        <Box>
                                                            <Typography>
                                                                Score
                                                            </Typography>
                                                            <QuantityModifier min={0} max={20} setValue={setValue} name={`${setting}.score`} watch={watch} />
                                                        </Box>
                                                    </Box>
                                                </Box>
                                            )
                                        } else {
                                            return (
                                                <Box key={index}>
                                                    <Typography>
                                                        {capitalizeFirstLetter(setting)}
                                                    </Typography>
                                                    <Box display="flex" alignItems="center" style={{ gap: 10 }} width="397px" justifyContent="space-between">
                                                        <AppRadioGroup name={`${setting}.setting_type`} control={control} values={searchValue} />
                                                        <Box>
                                                            <Typography>
                                                                Score
                                                            </Typography>
                                                            <QuantityModifier min={0} max={20} setValue={setValue} name={`${setting}.score`} watch={watch} />
                                                        </Box>
                                                    </Box>

                                                </Box>
                                            )
                                        }
                                    })}
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Age Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="age_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Size Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="size_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>

                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Push forward Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="push_forward_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Distance Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="distance_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Last connection Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="last_connection_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Seniority Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="seniority_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Photos Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="photos_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Profile filling Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={20} setValue={setValue} name="profile_filling_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>

                                </Box>
                                <Box display="flex">
                                    <Button disabled={isLoading} fullWidth type="submit" variant="contained" color="primary">
                                        {isLoading ? <CircularProgress size={24} /> : "Save"}
                                    </Button>
                                </Box>

                            </form>
                        </CardContent>
                    </Card>
                </AccordionDetails>
            </Accordion>

            <Card>
                <CardContent>
                    <Typography style={{ fontWeight: 700 }}>{`Current user search profile: ${searchTerm}`}</Typography>
                    <Typography style={{ fontWeight: 700 }}>{`Total: ${total}`}</Typography>

                    {Object.keys(searchOption).map((key, index) => {
                        return <ListItem key={key}>{`${key}: ${searchOption[key]}`}</ListItem>
                    })}
                </CardContent>
            </Card>
        </>
    )
}
