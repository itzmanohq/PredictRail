import React from 'react';

export default function DelayCard({ delayData, currentDelay = 0.0 }) {
  if (!delayData) return null;

  const predictedDelay = delayData.predicted_delay_minutes ?? 0.0;
  const severity = delayData.delay_severity || 'Unknown';
  const stationName = delayData.station_name || delayData.station || 'Station';
  const modelName = delayData.model || 'PredictRail delay prediction model';

  // Badge Color Determination
  let badgeColor = 'green';
  let severityLabel = 'On Time';

  if (predictedDelay <= 15.0) {
    badgeColor = 'green';
    severityLabel = 'On Time / Minor Delay';
  } else if (predictedDelay <= 45.0) {
    badgeColor = 'blue';
    severityLabel = 'Moderate Delay';
  } else if (predictedDelay <= 90.0) {
    badgeColor = 'orange';
    severityLabel = 'High Delay';
  } else {
    badgeColor = 'red';
    severityLabel = 'Severe Delay';
  }

  const deltaFromCurrent = (predictedDelay - currentDelay).toFixed(1);
  const deltaSign = (predictedDelay - currentDelay) >= 0 ? '+' : '';

  return (
    <div className="card delay-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          ML Delay Forecast
        </h3>
        <span className={`badge-status ${badgeColor}`}>
          {severityLabel}
        </span>
      </div>

      <div className="stat-highlight">
        <span className="stat-value">{predictedDelay.toFixed(1)}</span>
        <span className="stat-unit">min arrival delay</span>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        Expected arrival delay at <strong>{stationName}</strong> ({delayData.station})
      </p>

      <div className="stat-meta">
        <span>Current Observed: <strong>{currentDelay}m</strong></span>
        <span>Propagation Delta: <strong style={{ color: Number(deltaFromCurrent) > 0 ? 'var(--brand-red)' : 'var(--accent-emerald)' }}>{deltaSign}{deltaFromCurrent}m</strong></span>
      </div>
      <div className="stat-meta" style={{ borderTop: 'none', paddingTop: 0, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
        <span>Engine: HistGradientBoostingRegressor (Locally Fitted)</span>
      </div>
    </div>
  );
}
