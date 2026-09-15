/** Body measurement history API calls. */
import client from './client.js';

export async function getMeasurements() {
  const response = await client.get('/measurements/');
  return response.data;
}

export async function saveMeasurement(data) {
  const response = await client.post('/measurements/', data);
  return response.data;
}
