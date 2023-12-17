import React from 'react';
import CloseIcon from '@mui/icons-material/CloseOutlined';
import { Card, Dialog, DialogContent, CardContent, Box, IconButton } from '@mui/material';



export default function AvatarDialog(props) {
    const { open, handleClose, image } = props

    return (
        <div>

            <Dialog
                open={open}
                onClose={handleClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                {/* <DialogTitle>
                    {"Search and score settings"}
                </DialogTitle> */}
                <DialogContent>
                    <Card>
                        <Box display="flex" justifyContent="flex-end">
                            <IconButton onClick={handleClose}>
                                <CloseIcon />
                            </IconButton>
                        </Box>
                        <CardContent>
                            {image && <img src={image} alt="avatar" height="400px" width="auto" />}
                        </CardContent>
                    </Card>
                </DialogContent>

            </Dialog>
        </div>
    );
}
