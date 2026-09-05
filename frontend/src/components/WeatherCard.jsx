import React from 'react';

export default function WeatherCard({ weatherData }) {
  if (!weatherData) return null;

  const temp = weatherData.temperature_c != null ? `${weatherData.temperature_c}°C` : '--';
  const humidity = weatherData.relative_humidity_pct != null ? `${weatherData.relative_humidity_pct}%` : '--';
  const precip = weatherData.precipitation_mm != null ? `${weatherData.precipitation_mm} mm` : '0 mm';
  const wind = weatherData.wind_speed_kmh != null ? `${weatherData.wind_speed_kmh} km/h` : '0 km/h';
  const vis = weatherData.visibility_m != null ? `${(weatherData.visibility_m / 1000).toFixed(1)} km` : '--';

  const category = weatherData.weather_category || 'CLEAR';
  const description = weatherData.weather_description || 'Clear sky';
  const riskScore = weatherData.weather_risk_score != null ? weatherData.weather_risk_score : 5.0;
  const badgeColor = weatherData.badge_color || 'green';
  const delayAdj = weatherData.weather_delay_adjustment_min || 0.0;
  const isOffline = weatherData.offline_fallback || false;

  return (
    <div className="card weather-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
          </svg>
          Station Meteorological Risk
        </h3>
        <span className={`badge-status ${badgeColor}`}>
          {category}
        </span>
      </div>

      <div className="stat-highlight" style={{ marginBottom: '0.25rem' }}>
        <span className="stat-value">{riskScore.toFixed(0)}</span>
        <span className="stat-unit">/ 100 Risk Score</span>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
        {description} at <strong>{weatherData.station_name || weatherData.station_code}</strong>
      </p>

      {/* Weather Metrics Grid */}
      <div className="weather-metrics-grid">
        <div className="weather-metric-item">
          <div className="weather-metric-label">TEMPERATURE</div>
          <div className="weather-metric-val">{temp}</div>
        </div>
        <div className="weather-metric-item">
          <div className="weather-metric-label">HUMIDITY</div>
          <div className="weather-metric-val">{humidity}</div>
        </div>
        <div className="weather-metric-item">
          <div className="weather-metric-label">PRECIPITATION</div>
          <div className="weather-metric-val">{precip}</div>
        </div>
        <div className="weather-metric-item">
          <div className="weather-metric-label">WIND SPEED</div>
          <div className="weather-metric-val">{wind}</div>
        </div>
      </div>

      <div className="stat-meta" style={{ marginTop: '0.75rem' }}>
        <span>Weather Delay Impact: <strong>+{delayAdj} min</strong></span>
        <span>Visibility: <strong>{vis}</strong></span>
      </div>

      {isOffline && (
        <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--accent-amber)' }}>
          &#9888; Weather data unavailable — using offline safety fallback
        </div>
      )}
    </div>
  );
}
