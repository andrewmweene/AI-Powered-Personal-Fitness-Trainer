/**
 * Pose API call for analysing a video frame.
 */
import client from './client.js';

export async function analyseFrame(blob, exercise, sessionId) {
  const formData = new FormData();
  formData.append('file', blob, 'frame.jpg');
  formData.append('exercise', exercise);
  formData.append('session_id', sessionId);

  const response = await client.post('/pose/analyse-frame', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}
