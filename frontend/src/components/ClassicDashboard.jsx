import React from 'react';
import TrainSelector from './TrainSelector';
import DelayCard from './DelayCard';
import EtaCard from './EtaCard';
import WeatherCard from './WeatherCard';
import CrowdCard from './CrowdCard';
import RecommendationCard from './RecommendationCard';
import RoutePanel from './RoutePanel';
import LiveRailwayMap from './LiveRailwayMap';

export default function ClassicDashboard({
  data,
  loading,
  error,
  currentParams,
  activeBudgetFilter,
  onAnalyze,
  onBudgetFilterChange,
  onLiveTelemetryUpdate
}) {
  return (
    <main className="dashboard-grid">
      {/* Left Column: Parameter Selection */}
      <TrainSelector
        onAnalyze={onAnalyze}
        loading={loading}
      />

      {/* Right Column: AI Analytics & Recommendations */}
      <section className="main-content">
        {loading && !data && (
          <div className="card loading-overlay">
            <div className="spinner"></div>
            <p>Simulating ML delay regression, railway graph propagation, and weather risk...</p>
          </div>
        )}

        {data && (
          <>
            {/* Row 1: Delay, Dynamic ETA, Weather */}
            <div className="metrics-row">
              <DelayCard
                delayData={data.delay_prediction}
                currentDelay={currentParams.currentDelay}
              />
              <EtaCard
                etaData={data.dynamic_eta}
                trainData={data.train}
              />
              <WeatherCard
                weatherData={data.weather}
              />
            </div>

            {/* Row 2: Live Railway Route & GPS Telemetry Map */}
            <LiveRailwayMap
              trainNumber={currentParams.trainNumber}
              stationCode={currentParams.stationCode}
              trainInfo={data.train}
              bottlenecks={data.network_bottlenecks || []}
              itinerary={data.dynamic_eta?.upcoming_itinerary || []}
              nearbyRadiusKm={150}
              onLiveTelemetryUpdate={onLiveTelemetryUpdate}
            />

            {/* Row 3: Smart Compartment Recommendation & Crowd Density */}
            <div className="metrics-row">
              <RecommendationCard
                recData={data.compartment_recommendation}
                crowdData={data.crowd}
                activeFilter={activeBudgetFilter}
                onFilterChange={onBudgetFilterChange}
              />
              <CrowdCard
                crowdData={data.crowd}
              />
            </div>

            {/* Row 4: Timetable & Route Progression */}
            <RoutePanel
              itinerary={data.dynamic_eta?.upcoming_itinerary}
              currentStation={currentParams.stationCode}
              trainInfo={data.train}
            />
          </>
        )}

        {!loading && !data && !error && (
          <div className="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ margin: '0 auto 1rem', opacity: 0.5 }}>
              <path d="M4 15.5C4 17.43 5.57 19 7.5 19L6 20.5v.5h12v-.5L16.5 19c1.93 0 3.5-1.57 3.5-3.5V5c0-3.5-3.58-4-8-4s-8 .5-8 4v10.5z"></path>
            </svg>
            <h3>Ready to Forecast Indian Railways Delay</h3>
            <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Select a train number and observation station on the left to begin analytics.</p>
          </div>
        )}
      </section>
    </main>
  );
}
