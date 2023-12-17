import React, { useRef, useEffect, useState } from 'react';
import * as tf from '@tensorflow/tfjs';
import * as tfd from '@tensorflow/tfjs-core';
import * as blazeface from '@tensorflow-models/blazeface';
import axios from 'axios';
import useInterval from './useInterval';

const constrants = {
  video: {
    aspectRatio: 4 / 3
  }
}

const FaceDetection = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [blob, setBlob] = useState(null)
  const [screenshots, setScreenshots] = useState([])
  const [loading, setLoading] = useState(false)
  const [label, setLabel] = useState("FakeFace")
  const labelRef = useRef("FakeFace")
  const [prob, setProb] = useState(0)

  async function detectLiveness(blobFile) {
    if (blobFile) {
      // Create a new FormData object
      const formData = new FormData();
      // Append the blob to the FormData object as a file with a name and type
      formData.append('file', blob, 'face.jpg');

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

  // useInterval(async () => {
  //   async function detectLiveness(blobFile) {
  //     if (blobFile) {
  //       // Create a new FormData object
  //       const formData = new FormData();
  //       // Append the blob to the FormData object as a file with a name and type
  //       formData.append('file', blob, 'face.jpg');

  //       // Set the headers for the request
  //       const headers = {
  //         'accept': 'application/json',
  //         'Content-Type': 'multipart/form-data',
  //       };

  //       try {
  //         // Make the axios POST request
  //         const response = await axios.post('https://liveness-detection.ltservices.ovh/liveness_detection', formData, { headers });

  //         // Handle the response
  //         console.log("prob", response.data.probability, response.data.probability.toFixed(2));
  //         setLabel(response.data.label)
  //         labelRef.current = response.data.label
  //         setProb(Number(response.data.probability).toFixed(2))

  //       } catch (error) {
  //         // Handle the error
  //         console.log(error);
  //       }
  //     }

  //   }
  //   // blob && detectLiveness(blob)
  // }, 3000);

  useInterval(() => {
    const canvas = canvasRef.current;
    canvas.toBlob(async (blob) => {
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
          const { videoWidth, videoHeight } = video;
          // Resize the canvas to match the video dimensions
          canvas.width = videoWidth;
          canvas.height = videoHeight;

          // Draw the video frame onto the canvas
          const ctx = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0, videoWidth, videoHeight);

          canvas.toBlob(async (blob) => {
            setBlob(blob)
          }, 'image/jpeg', 1.0);
          // Detect faces in the video frame
          if (canvas.width > 0 && canvas.height > 0) {
            const predictions = await model.estimateFaces(canvas);
            // Draw a rectangle around each detected face
            predictions.forEach(prediction => {
              try {
                // const topLeft = prediction.topLeft
                const topLeft = [prediction.topLeft[0] - 50, prediction.topLeft[1] - 50];
                // const bottomRight = prediction.bottomRight;
                const bottomRight = [prediction.bottomRight[0] - 50, prediction.bottomRight[1] - 50];

                const width = bottomRight[0] - topLeft[0] + 100;
                const height = bottomRight[1] - topLeft[1] + 100;
                ctx.beginPath();
                ctx.rect(topLeft[0], topLeft[1], width, height);
                ctx.strokeStyle = labelRef.current === "FakeFace" ? 'red' : 'green';
                ctx.lineWidth = 2;
                ctx.stroke();

                const faceCanvas = document.createElement('canvas');
                const faceCtx = faceCanvas.getContext('2d');
                faceCanvas.width = width;
                faceCanvas.height = height;
                faceCtx.drawImage(canvas, topLeft[0], topLeft[1], width, height, 0, 0, width, height);
                // faceCtx.fillText("Hello a Quan", );
                // Add label and probability text to canvas


              } catch (error) {
                console.log("error", error);
              }
              // const dataUrl = faceCanvas.toDataURL('image/png');
              // console.log('Face image:', dataUrl);
            });
          }


          // Call the detectFaces function again after a short delay
          setTimeout(detectFaces, 10);
        };

        detectFaces();
      } catch (error) {
        console.error(error);
      }
    };

    run();
  }, []);

  useEffect(() => {
    console.log("loadding", loading);
  }, [loading])

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
    console.log("count", count, results[0].probability);
    if (count >= 2) {
      setLabel("RealFace")
      setProb(results[0].probability)
      setLoading(false)
    } else if (count === 0) {
      setLabel("FakeFace")
      setProb(results[0].probability)
      setLoading(false)
    } else {
      checkLiveNess()
    }
    if (count >= 2) {
      setLabel("RealFace")
      setProb(Number(results.map(r => r.probability).reduce((a, b) => {
        return Number(a) + Number(b)
      }, 0) / results.length).toFixed(2))
      setLoading(false)
      labelRef.current = "RealFace"
    } else if (count === 0) {
      setLabel("FakeFace")
      setProb(Number(results.map(r => r.probability).reduce((a, b) => {
        return Number(a) + Number(b)
      }, 0) / results.length).toFixed(2))
      setLoading(false)
      labelRef.current = "FakeFace"
    } else {
      checkLiveNess()
    }
  }

  return (
    <div>
      <button
        onClick={(e) => {
          e.preventDefault()
          if (screenshots && screenshots.length > 0) {
            checkLiveNess()
          } else {
            setTimeout(() => {
              checkLiveNess()
            }, 3000);
          }
          // videoRef.current.play();
        }}
        style={{
          position: "absolute",
          height: 50,
          width: 100,
          top: 0,
          left: 0,
          zIndex: 9999,
        }}>Start</button>
      {loading && <div
        style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", backgroundColor: "rgba(0,0,0,0.5)", zIndex: 9999 }}
      >Loading ....</div>}
      <div style={{ position: "absolute", right: 0, top: 0, zIndex: 9999, fontWeight: 'bold', color: label === "FakeFace" ? 'red' : "green", fontSize: 40 }}>{`${label}: ${prob}`}</div>
      <video style={{
        display: "none",
        position: "relative",
        width: "100%",
        height: "100%",
        left: 0,
        top: 0,
      }} playsInline muted autoPlay ref={videoRef} />
      <canvas
        style={{
          width: "100%",
          height: "100%",
          // objectFit: "contain",
          position: "absolute",
          left: 0,
          top: 0,
        }}
        id="canvas" ref={canvasRef} />
    </div>
  );
};

export default FaceDetection;
