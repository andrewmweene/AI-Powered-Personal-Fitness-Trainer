import { useEffect, useState } from 'react';

const CAMERA_STORAGE_KEY = 'fitness-trainer.selected-camera-device-id';

export default function useCameraDevices({ enabled = true } = {}) {
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!enabled || !navigator.mediaDevices) {
      return undefined;
    }

    let isCancelled = false;

    async function enumerateCameras() {
      try {
        const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true });
        permissionStream.getTracks().forEach((track) => track.stop());

        const availableDevices = await navigator.mediaDevices.enumerateDevices();
        const cameras = availableDevices.filter((device) => device.kind === 'videoinput');
        if (isCancelled) {
          return;
        }

        setDevices(cameras);
        setError(cameras.length ? null : 'No camera was found. Connect a camera to start pose tracking.');
        setSelectedDeviceId((currentDeviceId) => {
          const savedDeviceId = window.localStorage.getItem(CAMERA_STORAGE_KEY);
          const preferredDeviceId = currentDeviceId || savedDeviceId || '';
          const availableDevice = cameras.find((device) => device.deviceId === preferredDeviceId);
          const nextDeviceId = availableDevice?.deviceId || cameras[0]?.deviceId || '';
          if (nextDeviceId) {
            window.localStorage.setItem(CAMERA_STORAGE_KEY, nextDeviceId);
          }
          return nextDeviceId;
        });
      } catch (captureError) {
        if (isCancelled) {
          return;
        }
        if (captureError.name === 'NotAllowedError' || captureError.name === 'SecurityError') {
          setError('Camera permission was denied. Allow camera access in your browser settings to use pose tracking.');
        } else if (captureError.name === 'NotFoundError') {
          setError('No camera was found. Connect a camera to start pose tracking.');
        } else {
          setError('Unable to access the camera. Check your browser permissions and camera connection.');
        }
      }
    }

    function handleDeviceChange() {
      enumerateCameras();
    }

    enumerateCameras();
    navigator.mediaDevices.addEventListener?.('devicechange', handleDeviceChange);

    return () => {
      isCancelled = true;
      navigator.mediaDevices.removeEventListener?.('devicechange', handleDeviceChange);
    };
  }, [enabled]);

  const selectDevice = (deviceId) => {
    setSelectedDeviceId(deviceId);
    if (deviceId) {
      window.localStorage.setItem(CAMERA_STORAGE_KEY, deviceId);
    }
  };

  return { devices, selectedDeviceId, selectDevice, error };
}
