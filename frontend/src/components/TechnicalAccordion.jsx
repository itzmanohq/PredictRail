import React, { useState } from 'react';

export default function TechnicalAccordion({ data, currentParams }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="card technical-accordion-card">
      <button
        type="button"
        className="technical-accordion-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span style={{ fontWeight: '700', fontSize: '0.88rem' }}>How PredictRail works (Technical Details & AI Models)</span>
        </div>

        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      {isOpen && (
        <div className="technical-accordion-content">
          <div className="tech-grid">
            {/* ML Delay Engine */}
            <div className="tech-box">
              <h5>1. Machine Learning Delay Model</h5>
              <p>
                Uses a <strong>Histogram-based Gradient Boosting Regressor (HistGradientBoostingRegressor)</strong> trained on Indian Railways historical train movements. It predicts downstream arrival delay based on train category, departure hour, scheduled transit duration, and current station offset.
              </p>
              <div className="tech-metrics">
                <span>Model: <code>HistGradientBoostingRegressor</code></span>
                <span>Base Forecast: <strong>{data?.delay_prediction?.predicted_delay_minutes?.toFixed(1) || '0.0'} min</strong></span>
              </div>
            </div>

            {/* Railway Network Graph */}
            <div className="tech-box">
              <h5>2. Railway Graph & Bottlenecks</h5>
              <p>
                Models the entire Indian Railways rail topology as a directed spatial multigraph with <strong>NetworkX</strong>. Tracks cascade delays across heavily congested multi-track junction nodes (bottlenecks).
              </p>
              <div className="tech-metrics">
                <span>Active Bottlenecks: <strong>{data?.network_bottlenecks?.length || 0}</strong></span>
                <span>Propagation Delta: <strong>{(data?.delay_prediction?.predicted_delay_minutes - currentParams?.currentDelay)?.toFixed(1) || '0.0'} min</strong></span>
              </div>
            </div>

            {/* Weather Risk Layer */}
            <div className="tech-box">
              <h5>3. Meteorological Risk Engine</h5>
              <p>
                Integrates real-time weather data from <strong>Open-Meteo</strong> (temperature, precipitation, fog visibility, wind speed) to add dynamic safety buffers to the ETA.
              </p>
              <div className="tech-metrics">
                <span>Weather Buffer: <strong>+{data?.weather?.weather_delay_adjustment_min || 0} min</strong></span>
                <span>Risk Index: <strong>{data?.weather?.weather_risk_score?.toFixed(0) || 0}/100</strong></span>
              </div>
            </div>

            {/* RailRadar Live Telemetry */}
            <div className="tech-box">
              <h5>4. Live GPS Telemetry (RailRadar)</h5>
              <p>
                Connects to the official <strong>RailRadar REST API</strong> with Bearer token authentication to stream live train GPS coordinates, speed, segment progress, and actual departure times.
              </p>
              <div className="tech-metrics">
                <span>Telemetry: <strong>RailRadar Live REST API</strong></span>
                <span>Cache Window: <strong>60s TTL Memory Buffer</strong></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
