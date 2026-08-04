/**
 * Session API calls.
 */
import client from './client.js';

export async function saveSession(sessionData) {
  const response = await client.post('/sessions/', sessionData);
  return response.data;
}

export async function getSessions() {
  const response = await client.get('/sessions/');
  return response.data;
}
