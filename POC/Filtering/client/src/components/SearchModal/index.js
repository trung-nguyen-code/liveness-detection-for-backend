import React, { useState, useEffect } from 'react';
import { Card, Dialog, Typography, Button, DialogContent, DialogTitle, CardContent, Box, CircularProgress } from '@mui/material';
import AppRadioGroup from '../radiogroup'
import QuantityModifier from '../QuantityModifier'
import AppTextField from '../textfield'

import axios from 'axios'
import { BASE_URL } from '../../App'
import { useForm } from "react-hook-form";

const searchValue = [{ label: 'Exact Match', value: 'false' }, { label: 'Score Function', value: 'true' }]
const searchSettings = ['religious', 'salat_pratique', 'eat_halal', 'veil', 'want_children', 'has_children', 'family_situation', 'degree', 'fume', 'body', 'localisation', 'origin']

export function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function stringToBoolean(string) {
    return string === 'true'
}
const MAX = 100


export default function AlertDialog(props) {
    const { open, handleClose } = props

    const [isLoading, setIsLoading] = useState(false)
    const { handleSubmit, watch, control, reset,
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
            origin: {
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
            paging: 10
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
            origin: {
                setting_type: result.data.origin.setting_type.toString(),
                score: Number(result.data.origin.score)
            },
        })
        setIsLoading(false)
    }
    useEffect(() => {
        setIsLoading(true)

        fetchData()
    }, [])
    // const handleChange = (event, isExpanded) => {
    //     setIsExpand(isExpanded);
    // };
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
            paging: Number(data.paging)
        }, {})
        if (res.data) {
            setIsLoading(false)
            fetchData()
        } else {
            setIsLoading(false)
        }
    }

    return (
        <div>

            <Dialog
                open={open}
                onClose={handleClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle>
                    {"Search and score settings"}
                </DialogTitle>
                <DialogContent>
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
                                                            <QuantityModifier min={0} max={MAX} setValue={setValue} name={`${setting}.score`} watch={watch} />
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
                                                            <QuantityModifier min={0} max={MAX} setValue={setValue} name={`${setting}.score`} watch={watch} />
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
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="age_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Size Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="size_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>

                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Push forward Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="push_forward_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Distance Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="distance_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Last connection Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="last_connection_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Seniority Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="seniority_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Photos Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="photos_score" watch={watch} />
                                            </Box>
                                        </Box>
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Profile filling Score</Typography>
                                            <Box display="flex" >
                                                <QuantityModifier min={0} max={MAX} setValue={setValue} name="profile_filling_score" watch={watch} />
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box display="flex" style={{ gap: 10 }} marginBottom="10px" width="397px" justifyContent="space-between">
                                        <Box display="flex" flexDirection="column">
                                            <Typography>Paging</Typography>
                                            <Box display="flex" >
                                                <AppTextField type="number" control={control} name="paging" />
                                            </Box>
                                        </Box>
                                    </Box>

                                </Box>
                                <Box display="flex" justifyContent="flex-end">
                                    <Button variant="contained" color="primary" style={{ marginRight: 10 }} onClick={handleClose}>
                                        Cancel
                                    </Button>
                                    <Button disabled={isLoading} type="submit" variant="contained" color="primary">
                                        {isLoading ? <CircularProgress size={24} /> : "Save"}
                                    </Button>
                                </Box>

                            </form>
                        </CardContent>
                    </Card>
                </DialogContent>

            </Dialog>
        </div>
    );
}
