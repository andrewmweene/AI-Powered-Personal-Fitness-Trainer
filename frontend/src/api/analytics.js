/**
 * Analytics API calls.
 */
import client from './client.js';

export async function getSummary() {
  const response = await client.get('/analytics/summary');
  return response.data;
}

export async function getWeekly() {
  const response = await client.get('/analytics/weekly');
  return response.data;
}

export async function getByExercise() {
  const response = await client.get('/analytics/by-exercise');
  return response.data;
}

export async function getTrend() {
  const response = await client.get('/analytics/accuracy-trend');
  return response.data;
}
