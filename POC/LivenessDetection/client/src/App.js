import React, { useRef, useEffect, useState } from 'react'
import * as blazeface from '@tensorflow-models/blazeface';
import * as tf from '@tensorflow/tfjs';
import * as tfd from '@tensorflow/tfjs-core';
import axios from 'axios';
import useInterval from './useInterval';
import Swal from 'sweetalert2'

const constrants = {
    video: {
        aspectRatio: 4 / 3
    }
}

export default function App() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const hiddenCanvasRef = useRef(null)
    const [screenshots, setScreenshots] = useState([])
    const [loading, setLoading] = useState(false)
    const [label, setLabel] = useState("FakeFace")
    const [prob, setProb] = useState(0)
    const validRef = useRef(false)

    useInterval(() => {
        const video = videoRef.current;
        const { videoWidth, videoHeight } = video
        const hiddenCanvas = hiddenCanvasRef.current
        hiddenCanvas.width = videoWidth;
        hiddenCanvas.height = videoHeight
        const hiddenCtx = hiddenCanvas.getContext('2d');
        hiddenCtx.drawImage(video, 0, 0);
        hiddenCanvas.toBlob(async (blob) => {
            const current_shots = screenshots
            if (current_shots.length < 3) {
                current_shots.push(blob)
                setScreenshots(current_shots)
            } else {
                const current_shots = screenshots
                current_shots.shift()
                current_shots.push(blob)
                setScreenshots(current_shots)
            }
        }, 'image/jpeg', 1.0);
    }, 1000)

    useEffect(() => {
        const run = async () => {
            try {
                // Load the blazeface model
                const model = await blazeface.load();
                console.log('Blazeface model loaded.');

                // Get the video stream from the user's webcam
                const stream = await navigator.mediaDevices.getUserMedia(constrants);
                videoRef.current.srcObject = stream;
                console.log('Video stream obtained.');

                // Play the video and wait for it to start playing
                videoRef.current.play();
                await new Promise(resolve => videoRef.current.onplaying = resolve);

                // Run the face detection loop
                const detectFaces = async () => {
                    // Get the video and canvas dimensions
                    const video = videoRef.current;
                    const canvas = canvasRef.current;

                    const ctx = canvas.getContext('2d');
                    // ctx.translate(canvas.width, 0);
                    // ctx.scale(-1, 1);
                    ctx.drawImage(video, -100, 0, 600, 500);

                    if (canvas.width > 0 && canvas.height > 0) {
                        const predictions = await model.estimateFaces(canvas);
                        // Draw a rectangle around each detected face
                        predictions.forEach(prediction => {
                            try {
                                // const topLeft = prediction.topLeft
                                const topLeft = [prediction.topLeft[0], prediction.topLeft[1]];
                                // const bottomRight = prediction.bottomRight;
                                const bottomRight = [prediction.bottomRight[0], prediction.bottomRight[1]];

                                const width = bottomRight[0] - topLeft[0];
                                const height = bottomRight[1] - topLeft[1];
                                // ctx.beginPath();
                                // ctx.rect(topLeft[0], topLeft[1], width, height);
                                // ctx.strokeStyle = 'red'
                                // ctx.lineWidth = 2;
                                // ctx.stroke();
                                // console.log("canvas", canvas.width, canvas.height);

                                const faceCanvas = document.createElement('canvas');
                                const faceCtx = faceCanvas.getContext('2d');
                                faceCanvas.width = width;
                                faceCanvas.height = height;
                                faceCtx.drawImage(canvas, topLeft[0], topLeft[1], width, height, 0, 0, width, height);
                                // console.log("faceCanvas", topLeft[0], topLeft[1]);
                                // console.log("faceCanvas height", width, height);
                                if (topLeft[0] > 0 && topLeft[0] + width <= canvas.width && topLeft[1] > 0 && topLeft[1] + height <= canvas.height) {
                                    console.log("valid");
                                    validRef.current = true
                                } else {
                                    console.log("invalid");
                                    validRef.current = false
                                }
                            } catch (error) {
                                console.log("error", error);
                            }
                        });
                    }


                    setTimeout(detectFaces, 10);
                };

                detectFaces();
            } catch (error) {
                console.error(error);
            }
        };

        run();
    }, []);

    async function detectLiveness(blobFile) {
        if (blobFile) {
            // Create a new FormData object
            const formData = new FormData();
            // Append the blob to the FormData object as a file with a name and type
            formData.append('file', blobFile, 'face.jpg');

            // Set the headers for the request
            const headers = {
                'accept': 'application/json',
                'Content-Type': 'multipart/form-data',
            };

            try {
                // Make the axios POST request
                const response = await axios.post('https://liveness-detection.ltservices.ovh/liveness_detection', formData, { headers });
                return response.data
            } catch (error) {
                // Handle the error
                console.log(error);
                return null
            }
        }

    }

    async function checkLiveNess() {
        setLoading(true)
        const current_shots = screenshots
        const detectLivenesses = current_shots.map(async (blobFile) => {
            return await detectLiveness(blobFile)
        })
        const results = await Promise.all(detectLivenesses)
        let count = 0
        results.forEach((result) => {
            if ((result.label === "RealFace") && result.probability > 0.8) {
                count += 1
            }
        })

        if (count >= 2) {
            setLabel("RealFace")
            setProb(Number(results.map(r => r.probability).reduce((a, b) => {
                return Number(a) + Number(b)
            }, 0) / results.length).toFixed(2))
            setLoading(false)
            //   labelRef.current = "RealFace"
        } else if (count === 0) {
            setLabel("FakeFace")
            setProb(Number(results.map(r => r.probability).reduce((a, b) => {
                return Number(a) + Number(b)
            }, 0) / results.length).toFixed(2))
            setLoading(false)
            //   labelRef.current = "FakeFace"
        } else {
            checkLiveNess()
        }
    }

    return (
        <div
            style={{
                background: '#182D32',
                width: 'auto',
                height: '100vh',
                padding: "0 5px 0 5px",
                display: 'flex',
                flexDirection: 'column',
                justifyContent: "center",
                alignItems: "center",
            }}
        >
            {loading && <div
                style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", backgroundColor: "rgba(0,0,0,0.5)", zIndex: 9999 }}
            />}
            <h1 style={{ color: 'white', margin: 0 }}>Video verification</h1>
            <p style={{ color: 'white', }}>Let's make sure you are a real person</p>
            <video
                playsInline muted autoPlay
                ref={videoRef} style={{
                    display: 'none',
                    width: "100%",
                    height: "100%",
                    transform: 'scaleX(-1)',
                }} />
            <canvas ref={canvasRef} height="400px" width="300px" style={{
                border: '1px solid white',
                borderRadius: '50%',
                // position: "absolute",
            }} />
            <canvas ref={hiddenCanvasRef} style={{
                display: 'none',
                width: "100%",
                height: "100%",
            }} />
            {!loading && <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: "10px 0" }}>
                <p style={{ color: 'white', margin: 0 }}>Your face is {label}</p>
                <p style={{ color: 'white', margin: 0 }}>Probability: {prob}</p>
            </div>}
            <button
                disabled={loading}
                onClick={() => {
                    if (validRef.current) {
                        checkLiveNess()
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            text: 'Please show your face in the camera',
                        })
                    }
                }}
                style={{
                    margin: "20px 0 0 0",
                    background: "#85B284",
                    height: "40px",
                    width: "300px",
                    color: 'white',
                    borderRadius: "25px",
                    border: 'none'
                }}
            >Start verifying</button>
        </div>
    )
}
