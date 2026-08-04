/**
 * Hook for accessing the webcam and preparing an offscreen canvas.
 */
import { useEffect, useRef, useState } from 'react';

export default function useWebcam({ width = 640, height = 480 } = {}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    canvasRef.current = document.createElement('canvas');
    canvasRef.current.width = width;
    canvasRef.current.height = height;

    let stream;

    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width, height },
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(() => {
            /* ignore autoplay errors */
          });
        }
      } catch (captureError) {
        setError('Unable to access the camera. Please allow webcam access.');
      }
    }

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [height, width]);

  useEffect(() => {
    function handleLoaded() {
      setIsReady(true);
    }

    const videoElement = videoRef.current;
    if (videoElement) {
      videoElement.addEventListener('loadedmetadata', handleLoaded);
    }

    return () => {
      if (videoElement) {
        videoElement.removeEventListener('loadedmetadata', handleLoaded);
      }
    };
  }, []);

  return { videoRef, canvasRef, isReady, error };
}
