import React from 'react';

export default function Header({ activeNav = 'home', onNavChange }) {
  const titles = {
    home: 'Journey Planner',
    journey: 'Journey Map & Route',
    insights: 'Journey Insights & Predictions'
  };

  return (
    <header className="app-header-bar">
      <div className="header-left">
        <h2 className="header-page-title">{titles[activeNav] || 'PredictRail'}</h2>
      </div>

      <div className="header-right">
        <div className="header-status-pill">
          <span className="status-indicator-dot"></span>
          <span>Live Corridor Feed</span>
        </div>
      </div>
    </header>
  );
}
