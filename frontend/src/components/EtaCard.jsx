import React from 'react';

export default function EtaCard({ etaData, trainData }) {
  if (!etaData) return null;

  const destName = etaData.destination_name || (trainData ? trainData.destination_name : 'Destination');
  const destCode = etaData.destination_station || (trainData ? trainData.destination_station : '');
  const dynamicEta = etaData.destination_dynamic_eta || 'Calculating...';
  const baseDelay = etaData.destination_predicted_delay_min ?? 0.0;
  const weatherAdjustedDelay = etaData.destination_weather_adjusted_delay_min ?? baseDelay;
  const weatherBuffer = Math.max(0, weatherAdjustedDelay - baseDelay);

  let punctualityBadge = 'green';
  let punctualityText = etaData.destination_punctuality || 'On Time';
  if (baseDelay > 60.0) {
    punctualityBadge = 'red';
  } else if (baseDelay > 15.0) {
    punctualityBadge = 'orange';
  }

  return (
    <div className="card eta-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          Dynamic Destination ETA
        </h3>
        <span className={`badge-status ${punctualityBadge}`}>
          {punctualityText}
        </span>
      </div>

      <div className="stat-highlight">
        <span className="stat-value" style={{ fontSize: '1.85rem' }}>{dynamicEta}</span>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        Terminus: <strong>{destName}</strong> ({destCode})
      </p>

      <div className="stat-meta">
        <span>Base ML+Graph Delay: <strong>{baseDelay.toFixed(1)}m</strong></span>
        <span>Weather-Adjusted: <strong style={{ color: weatherBuffer > 0 ? 'var(--accent-amber)' : 'inherit' }}>{weatherAdjustedDelay.toFixed(1)}m</strong></span>
      </div>

      {weatherBuffer > 0 && (
        <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span>&#9888; Includes +{weatherBuffer.toFixed(1)}m meteorological risk buffer</span>
        </div>
      )}
    </div>
  );
}
