/** Axios client with in-memory JWT handling and cookie refresh rotation. */
import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const client = axios.create({
  baseURL: apiBaseUrl,
  withCredentials: true,
});

let accessToken = null;
let refreshRequest = null;

export function setAccessToken(token) {
  accessToken = token;
}

export function clearAccessToken() {
  accessToken = null;
}

export function getAccessToken() {
  return accessToken;
}

client.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthRequest = originalRequest?.url?.startsWith('/auth/');

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthRequest) {
      originalRequest._retry = true;
      try {
        refreshRequest ||= client.post('/auth/refresh', null, { skipAuthRefresh: true });
        const response = await refreshRequest;
        refreshRequest = null;
        setAccessToken(response.data.access_token);
        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${response.data.access_token}`,
        };
        return client(originalRequest);
      } catch (refreshError) {
        refreshRequest = null;
        clearAccessToken();
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export default client;
