import React from 'react';

export default function Header({
  activeNav = 'home',
  onNavChange,
  uiState = 'LIVE_DATA_FOUND',
  lastUpdated,
  onRefresh
}) {
  const titles = {
    home: 'Journey Planner',
    journey: 'Journey Map & Route',
    insights: 'Journey Insights & Predictions'
  };

  const getStatusDisplay = () => {
    switch (uiState) {
      case 'LOADING':
        return { label: 'Updating...', dotClass: 'dot-loading', pillClass: 'loading' };
      case 'ARRIVED':
        return { label: 'Journey Completed', dotClass: 'dot-arrived', pillClass: 'arrived' };
      case 'LIVE_DATA_STALE':
        return { label: 'Stale Telemetry', dotClass: 'dot-stale', pillClass: 'stale' };
      case 'PREDICTION_UPDATED':
      case 'LIVE_DATA_FOUND':
      default:
        return { label: 'Live Corridor Feed', dotClass: 'dot-live', pillClass: 'live' };
    }
  };

  const status = getStatusDisplay();

  return (
    <header className="app-header-bar">
      <div className="header-left">
        <h2 className="header-page-title">{titles[activeNav] || 'PredictRail'}</h2>
      </div>

      <div className="header-right">
        <div className={`header-status-pill ${status.pillClass}`}>
          <span className={`status-indicator-dot ${status.dotClass}`}></span>
          <span>{status.label}</span>
          {lastUpdated && <span className="header-timestamp">· {lastUpdated}</span>}
        </div>

        {onRefresh && (
          <button
            type="button"
            className="btn-header-refresh"
            onClick={onRefresh}
            title="Refresh Live Telemetry & Predictions"
            aria-label="Refresh Live Predictions"
          >
            ↻
          </button>
        )}
      </div>
    </header>
  );
}
