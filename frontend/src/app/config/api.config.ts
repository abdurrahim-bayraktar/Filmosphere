// Detect production by hostname instead of relying on environment file replacement
const isProduction = typeof window !== 'undefined' && 
  !window.location.hostname.includes('localhost') && 
  !window.location.hostname.includes('127.0.0.1');

export const API_URL = isProduction 
  ? 'https://filmosphere.onrender.com/api' 
  : 'http://127.0.0.1:8000/api';

