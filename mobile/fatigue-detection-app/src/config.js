// src/config.js - API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
export const POLL_INTERVAL = 500; // ms
export const VIDEO_STREAM_URL = `${API_URL}/video`;
export const STATS_ENDPOINT = `${API_URL}/stats`;
