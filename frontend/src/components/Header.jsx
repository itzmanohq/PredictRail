import React from 'react';
import SystemStatus from './SystemStatus';

export default function Header({ viewMode = 'passenger', onViewModeChange }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo" aria-label="PredictRail Logo">
          <svg viewBox="0 0 24 24">
            <path d="M4 15.5C4 17.43 5.57 19 7.5 19L6 20.5v.5h12v-.5L16.5 19c1.93 0 3.5-1.57 3.5-3.5V5c0-3.5-3.58-4-8-4s-8 .5-8 4v10.5zm8-12.5c4.76 0 6 1.04 6 2v2H6V5c0-.96 1.24-2 6-2zm-4.5 13c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" />
          </svg>
        </div>
        <div>
          <h1 className="brand-title">
            PREDICTRAIL
            <span className="brand-badge">PASSENGER ASSISTANT</span>
          </h1>
          <p className="brand-subtitle">
            Live Train Tracker, Delay Forecast & Smart Coach Guide
          </p>
        </div>
      </div>

      <div className="header-right-group" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* View Mode Switcher: Passenger vs Classic */}
        <div className="view-mode-toggle-group">
          <button
            type="button"
            className={`btn-mode-tab ${viewMode === 'passenger' ? 'active' : ''}`}
            onClick={() => onViewModeChange && onViewModeChange('passenger')}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Passenger View
          </button>

          <button
            type="button"
            className={`btn-mode-tab ${viewMode === 'classic' ? 'active' : ''}`}
            onClick={() => onViewModeChange && onViewModeChange('classic')}
            title="Open original advanced ML and graph telemetry dashboard"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            Classic / Expert
          </button>
        </div>

        <SystemStatus />
      </div>
    </header>
  );
}

