import AsyncStorage from '@react-native-async-storage/async-storage';

// Hardcoded LAN IP to ensure Android device reaches PC Backend directly
const API_BASE = "http://192.168.0.108:8000";
const TIMEOUT_MS = 30000; 

const getHeaders = async (contentType) => {
  const token = await AsyncStorage.getItem('userToken');
  const headers = {
    'Content-Type': contentType,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
  return headers;
};

export const apiRequest = async (endpoint, method = 'GET', body = null) => {
  let url = `${API_BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let requestBody = null;
  let contentType = 'application/json';

  // Special handling for the /explain endpoint which FastAPI expects as Query Params
  if (endpoint === '/explain' && method === 'POST' && body) {
    const params = new URLSearchParams();
    params.append('question', body.question || '');
    params.append('context', body.context || '');
    url = `${url}?${params.toString()}`;
    requestBody = null; // No body needed for query params
  } 
  // Standard handling for OAuth2 /token and other JSON requests
  else if (body instanceof URLSearchParams) {
    requestBody = body.toString();
    contentType = 'application/x-www-form-urlencoded';
  } else if (body) {
    requestBody = JSON.stringify(body);
  }

  const headers = await getHeaders(contentType);

  try {
    console.log(`[API Request] ${method} ${url}`);
    
    // Token validation: Ensure token exists for protected routes (exclude public ones)
    const isPublic = endpoint.startsWith('/token') || endpoint.startsWith('/register') || endpoint.startsWith('/health');
    if (!isPublic && !headers['Authorization']) {
      throw new Error("Authentication required. Please log in.");
    }

    const response = await fetch(url, {
      method,
      headers,
      body: requestBody,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    const contentType = response.headers.get("content-type");
    const isJson = contentType && contentType.includes("application/json");

    if (!response.ok) {
      const errorText = await response.text();
      let detail = `Server Error: ${response.status}`;
      
      if (response.status === 401) {
        await AsyncStorage.removeItem('userToken'); // Clear stale token
        throw new Error("Session expired or invalid. Please log in again.");
      }
      if (isJson) {
        try { detail = JSON.parse(errorText).detail || detail; } catch(e) {}
      }
      throw new Error(detail);
    }

    return isJson ? await response.json() : null;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') throw new Error("Request timed out. Ensure the backend is running.");
    if (error.message.includes('Network request failed')) {
      throw new Error(`Network error. Connect to the same Wi-Fi and check ${API_BASE}`);
    }
    throw error;
  }
};

// Authentication services
export const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const responseData = await apiRequest('/token', 'POST', formData);
    await AsyncStorage.setItem('userToken', responseData.access_token);
    return responseData.access_token;
};

export const logout = async () => {
  await AsyncStorage.removeItem('userToken');
};

export const register = (userData) => apiRequest('/register', 'POST', userData);

export const authService = {
  login,
  logout,
  register,
  getUsersMe: () => apiRequest('/users/me', 'GET')
};

export const getUsersMe = () => apiRequest('/users/me', 'GET'); // Added for fetching current user

// Financial services
export const analyze = (data) => apiRequest('/analyze', 'POST', data);

export const explain = (question, context = "") => apiRequest('/explain', 'POST', { question, context });

export const getHistory = () => apiRequest('/history', 'GET');

export const getRecord = (id) => apiRequest(`/records/${id}`, 'GET');

export const updateRecord = (id, payload) => apiRequest(`/records/${id}`, 'PUT', payload);