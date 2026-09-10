/**
 * PredictRail API Client
 * Production backend: https://predictrail-backend.onrender.com
 * Local backend: http://localhost:8000
 */

// Resolve API base URL prioritizing VITE_API_BASE_URL, then VITE_API_URL, then environment fallback
const rawApiUrl =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD
    ? 'https://predictrail-backend.onrender.com'
    : 'http://localhost:8000');

// Strip any trailing slashes for clean URL concatenation
const API_BASE_URL = (rawApiUrl || 'https://predictrail-backend.onrender.com').replace(/\/+$/, '');

// Client-side cache for static train routes & catalog to prevent redundant network queries
const _CLIENT_CACHE = new Map();

/**
 * Generic fetch wrapper with automated retry (for Render cold starts) and error formatting
 */
async function fetchJson(endpoint, options = {}, retries = 2) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${cleanEndpoint}`;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // AbortController with 25-second timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000);

      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        },
        ...options
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorDetail = `Request failed with status ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.error || errorDetail;
        } catch (e) {
          // use default status message
        }
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (error) {
      const isLastAttempt = attempt === retries;
      const isNetworkError = error.name === 'AbortError' || error.message.includes('Failed to fetch') || error.message.includes('NetworkError');

      if (!isLastAttempt && isNetworkError) {
        console.warn(`[PredictRail API] Attempt ${attempt + 1} failed for ${endpoint}. Retrying in 1.5s (server may be waking up)...`);
        await new Promise(resolve => setTimeout(resolve, 1500));
        continue;
      }

      let friendlyMessage = error.message;
      if (error.name === 'AbortError') {
        friendlyMessage = 'Server request timed out. The backend may be spinning up from sleep mode. Please try again.';
      } else if (error.message && error.message.includes('Failed to fetch')) {
        friendlyMessage = 'Cannot connect to backend server. If using cloud deployment, Render is waking up from sleep (~30s). Please retry.';
      }

      console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, friendlyMessage);
      const enhancedError = new Error(friendlyMessage);
      enhancedError.originalError = error;
      throw enhancedError;
    }
  }
}

/**
 * Health Check
 */
export async function checkHealth() {
  return await fetchJson('/health');
}

/**
 * List & search Indian Railways train catalog
 */
export async function getTrains(search = '', limit = 50) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  params.append('limit', limit.toString());
  return await fetchJson(`/trains?${params.toString()}`);
}

/**
 * Get detailed itinerary and stops for a specific train (cached in client memory)
 */
export async function getTrainDetail(trainNumber) {
  const cleanNo = String(trainNumber).trim().replace(/^0+/, '');
  if (_CLIENT_CACHE.has(`train:${cleanNo}`)) {
    return _CLIENT_CACHE.get(`train:${cleanNo}`);
  }
  const data = await fetchJson(`/trains/${encodeURIComponent(cleanNo)}`);
  if (data && data.train_number) {
    _CLIENT_CACHE.set(`train:${cleanNo}`, data);
  }
  return data;
}

/**
 * Single-station ML delay prediction
 */
export async function predictDelay(trainNumber, stationCode, currentDelay = 0.0, departureHour = null) {
  return await fetchJson('/predict-delay', {
    method: 'POST',
    body: JSON.stringify({
      train_number: trainNumber,
      station_code: stationCode,
      current_delay_minutes: Number(currentDelay) || 0.0,
      departure_hour: departureHour
    })
  });
}

/**
 * Multi-stop Dynamic ETA
 */
export async function getDynamicEta(trainNumber, currentStation, currentDelay = 0.0) {
  return await fetchJson('/eta', {
    method: 'POST',
    body: JSON.stringify({
      train_number: trainNumber,
      current_station: currentStation,
      current_delay_minutes: Number(currentDelay) || 0.0
    })
  });
}

/**
 * Station weather & meteorological risk
 */
export async function getWeather(stationCode) {
  return await fetchJson(`/weather/${encodeURIComponent(stationCode)}`);
}

/**
 * Prototype crowd density
 */
export async function getCrowd(trainNumber, stationCode) {
  return await fetchJson('/crowd', {
    method: 'POST',
    body: JSON.stringify({
      train_number: trainNumber,
      station_code: stationCode
    })
  });
}

/**
 * Smart least-crowded compartment recommendation
 */
export async function getCompartmentRecommendation(trainNumber, stationCode, budgetFilter = 'ALL') {
  return await fetchJson('/recommend-compartment', {
    method: 'POST',
    body: JSON.stringify({
      train_number: trainNumber,
      station_code: stationCode,
      budget_filter: budgetFilter
    })
  });
}

/**
 * Unified Master Intelligence Analysis (POST /predict)
 */
export async function analyzeTrain(trainNumber, currentStation, currentDelay = 0.0, budgetFilter = 'ALL') {
  return await fetchJson('/predict', {
    method: 'POST',
    body: JSON.stringify({
      train_number: trainNumber,
      current_station: currentStation,
      current_delay_minutes: Number(currentDelay) || 0.0,
      budget_filter: budgetFilter
    })
  });
}

/**
 * Real-time Live Train Running Status & Telemetry (RailRadar)
 */
export async function getLiveTrainStatus(trainNumber, date = null, authoritative = false) {
  const params = new URLSearchParams();
  if (date) params.append('date', date);
  if (authoritative) params.append('authoritative', 'true');
  const queryStr = params.toString() ? `?${params.toString()}` : '';
  return await fetchJson(`/trains/${encodeURIComponent(trainNumber)}/live${queryStr}`);
}

