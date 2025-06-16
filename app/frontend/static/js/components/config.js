// components/config.js

// API Configuration - Change this to switch between test and production
const API_MODE = 'production'; // Change to 'production' for real Gemini API
const API_ENDPOINT = API_MODE === 'test' ? '/generate/test' : '/generate';

console.log(`🔧 API Mode: ${API_MODE} | Endpoint: ${API_ENDPOINT}`);