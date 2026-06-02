import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const getApiBase = () => {
  if (Platform.OS === 'web') {
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    return `http://${hostname}:8000`;
  }

  if (Platform.OS === 'android') {
    // For Android emulators: use the host machine loopback address.
    return 'http://10.0.2.2:8000';
  }

  return 'http://localhost:8000';
};

export const API_BASE = getApiBase();

async function handleResponse(res) {
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || 'API error');
  }
  return res.json();
}

export async function register({ username, email, password }) {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return handleResponse(res);
}

export async function login(username, password) {
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);

  const res = await fetch(`${API_BASE}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  });
  const data = await handleResponse(res);
  const token = data.access_token;
  await AsyncStorage.setItem('token', token);
  return token;
}

export async function getHistory(token) {
  const res = await fetch(`${API_BASE}/history`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return handleResponse(res);
}

export async function getRecord(token, id) {
  const res = await fetch(`${API_BASE}/records/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return handleResponse(res);
}

export async function updateRecord(token, id, payload) {
  const res = await fetch(`${API_BASE}/records/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function createRecord(token, payload) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}
