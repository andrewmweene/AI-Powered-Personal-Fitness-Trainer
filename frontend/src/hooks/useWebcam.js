/**
 * Hook for accessing the webcam and preparing an offscreen canvas.
 */
import { useEffect, useRef, useState } from 'react';

export default function useWebcam({ width = 640, height = 480, enabled = true, deviceId = '' } = {}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);
  const [streamVersion, setStreamVersion] = useState(0);

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
    let isCancelled = false;
    setIsReady(false);
    setStreamVersion((version) => version + 1);

    async function startCamera() {
      try {
        const videoConstraints = { width, height };
        if (deviceId) {
          videoConstraints.deviceId = { exact: deviceId };
        }
        stream = await navigator.mediaDevices.getUserMedia({
          video: videoConstraints,
        });
        if (isCancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
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
        if (!isCancelled) {
          setIsReady(false);
          if (captureError.name === 'NotAllowedError' || captureError.name === 'SecurityError') {
            setError('Camera permission was denied. Allow camera access in your browser settings to use pose tracking.');
          } else if (captureError.name === 'NotFoundError' || captureError.name === 'OverconstrainedError') {
            setError('The selected camera is unavailable. Choose another camera or reconnect it.');
          } else {
            setError('Unable to access the camera. Check your browser permissions and camera connection.');
          }
        }
      }
    }

    startCamera();

    return () => {
      isCancelled = true;
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [deviceId, enabled, height, width]);

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

  return { videoRef, canvasRef, isReady, error, streamVersion };
}
