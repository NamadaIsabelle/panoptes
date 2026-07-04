// ---------------------------------------------------------------
// Panoptes — frontend configuration
//
// Gate layout and mock users now live on the backend (backend/config.py)
// as the single source of truth. This file just points the dashboard
// at the API.
// ---------------------------------------------------------------

const API_BASE = 'http://localhost:5000';
const POLL_INTERVAL_MS = 1500;   // how often to check for new logs/alerts/state
const LOG_FETCH_LIMIT = 40;
const ALERT_FETCH_LIMIT = 20;