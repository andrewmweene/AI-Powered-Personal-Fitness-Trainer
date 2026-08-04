/**
 * Authentication API calls.
 */
import client from './client.js';

export async function login(username, password) {
  const response = await client.post('/users/login', { username, password });
  return response.data.access_token;
}

export async function register(userData) {
  const response = await client.post('/users/register', userData);
  return response.data;
}

export async function getMe() {
  const response = await client.get('/users/me');
  return response.data;
}
