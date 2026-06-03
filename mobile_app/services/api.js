import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

// Resolve API base at runtime. This allows overriding for physical devices by
// setting a persisted value with `setApiBase(...)` (useful when running on a
// phone that cannot reach 10.0.2.2). Defaults are safe for web and emulator.
export async function getApiBase() {
  // Allow an explicit override stored in AsyncStorage (set via developer).
  try {
    const override = await AsyncStorage.getItem('API_BASE');
    if (override) return override;
  } catch (e) {
    // ignore
  }

  if (Platform.OS === 'web') {
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    return `http://${hostname}:8000`;
  }

  // If expo config provides an extra.apiBase, prefer that (useful for EAS).
  try {
    const extraBase = Constants.manifest?.extra?.API_BASE || Constants.expoConfig?.extra?.API_BASE;
    if (extraBase) return extraBase;
  } catch (e) {
    // ignore
  }

  if (Platform.OS === 'android') {
    // For Android emulators use host machine loopback address. For physical
    // devices the developer should call `setApiBase('http://<host-ip>:8000')`.
    return 'http://10.0.2.2:8000';
  }

  return 'http://localhost:8000';
}

export async function setApiBase(url) {
  if (!url) throw new Error('Invalid API base');
  await AsyncStorage.setItem('API_BASE', url);
}

async function handleResponse(res) {
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || 'API error');
  }
  return res.json();
}

export async function register({ username, email, password }) {
  const API_BASE = await getApiBase();
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

  const API_BASE = await getApiBase();

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
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/history`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return handleResponse(res);
}

export async function getRecord(token, id) {
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/records/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return handleResponse(res);
}

export async function updateRecord(token, id, payload) {
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/records/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}

export async function createRecord(token, payload) {
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
}
