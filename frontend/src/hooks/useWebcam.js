/**
 * Hook for accessing the webcam and preparing an offscreen canvas.
 */
import { useEffect, useRef, useState } from 'react';

export default function useWebcam({ width = 640, height = 480, enabled = true } = {}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!enabled) {
      setIsReady(false);
      setError(null);
      if (canvasRef.current) {
        canvasRef.current.width = width;
        canvasRef.current.height = height;
      }
      return undefined;
    }

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
          if (videoRef.current.readyState >= 2) {
            setIsReady(true);
          }
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
  }, [enabled, height, width]);

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    function handleLoaded() {
      setIsReady(true);
    }

    const videoElement = videoRef.current;
    if (!videoElement) {
      return undefined;
    }

    videoElement.addEventListener('loadedmetadata', handleLoaded);
    if (videoElement.readyState >= 2) {
      setIsReady(true);
    }

    return () => {
      videoElement.removeEventListener('loadedmetadata', handleLoaded);
    };
  }, [enabled]);

  return { videoRef, canvasRef, isReady, error };
}
