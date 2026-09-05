/**
 * PredictRail API Client
 * Connects to the FastAPI backend at http://localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    });

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
    console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, error);
    throw error;
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
 * Get detailed itinerary and stops for a specific train
 */
export async function getTrainDetail(trainNumber) {
  return await fetchJson(`/trains/${encodeURIComponent(trainNumber)}`);
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

