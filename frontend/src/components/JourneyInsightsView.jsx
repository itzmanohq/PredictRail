import React from 'react';
import JourneyInsights from './JourneyInsights';

export default function JourneyInsightsView({
  data,
  loading,
  activeBudgetFilter,
  onBudgetFilterChange
}) {
  if (!data && !loading) {
    return (
      <div className="empty-journey-state card">
        <div className="empty-icon-circle">✨</div>
        <h3>No Insights Available</h3>
        <p>Please select a train on the Home tab and click "Analyse Journey" to generate AI delay forecasts, weather risk, and coach recommendations.</p>
      </div>
    );
  }

  return (
    <div className="insights-view-container">
      <div className="insights-header-banner">
        <div>
          <span className="insights-tag">AI PREDICTION SUITE</span>
          <h2 className="insights-title">Journey Insights & Recommendations</h2>
        </div>
        <div className="insights-meta">
          <span>{data?.train?.train_number} · {data?.train?.train_name}</span>
        </div>
      </div>

      {/* 6 Clean Compact Cards + Coach Density Breakdown */}
      <JourneyInsights
        data={data}
        activeBudgetFilter={activeBudgetFilter}
        onBudgetFilterChange={onBudgetFilterChange}
      />
    </div>
  );
}
