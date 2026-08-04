/**
 * Recommendation API calls.
 */
import client from './client.js';

export async function getPlan() {
  const response = await client.get('/recommendations/plan');
  return response.data;
}

export async function refreshPlan() {
  const response = await client.post('/recommendations/plan/refresh');
  return response.data;
}
