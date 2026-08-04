/**
 * Onboarding API calls.
 */
import client from './client.js';

export async function completeOnboarding(data) {
  const response = await client.post('/onboarding/complete', data);
  return response.data;
}

export async function getStatus() {
  const response = await client.get('/onboarding/status');
  return response.data;
}

export async function getProfile() {
  const response = await client.get('/onboarding/profile');
  return response.data;
}
