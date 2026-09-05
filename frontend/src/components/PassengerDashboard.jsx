import React from 'react';
import PassengerHeroSearch from './PassengerHeroSearch';
import PassengerJourneyHero from './PassengerJourneyHero';
import LiveRailwayMap from './LiveRailwayMap';
import PassengerCards from './PassengerCards';
import PassengerRouteTimeline from './PassengerRouteTimeline';
import TechnicalAccordion from './TechnicalAccordion';

export default function PassengerDashboard({
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
    <div className="passenger-dashboard-container">
      {/* 1. Large "Where is my train?" Hero Search Bar */}
      <PassengerHeroSearch
        onAnalyze={onAnalyze}
        loading={loading}
        currentTrainNumber={currentParams?.trainNumber}
        currentStationCode={currentParams?.stationCode}
      />

      {/* Loading Overlay State */}
      {loading && !data && (
        <div className="card loading-overlay">
          <div className="spinner"></div>
          <p>Finding your train, live location, and schedule...</p>
        </div>
      )}

      {/* Main Passenger Results View */}
      {data && (
        <div className="passenger-main-flow">
          {/* 2. Top "Your Journey" 5-Second Highlights Banner */}
          <PassengerJourneyHero
            trainData={data.train}
            delayData={data.delay_prediction}
            etaData={data.dynamic_eta}
            recData={data.compartment_recommendation}
            weatherData={data.weather}
            currentParams={currentParams}
          />

          {/* 3. Live Railway Map */}
          <LiveRailwayMap
            trainNumber={currentParams.trainNumber}
            stationCode={currentParams.stationCode}
            trainInfo={data.train}
            bottlenecks={data.network_bottlenecks || []}
            itinerary={data.dynamic_eta?.upcoming_itinerary || []}
            nearbyRadiusKm={150}
            onLiveTelemetryUpdate={onLiveTelemetryUpdate}
          />

          {/* 4. Simple Weather & Less Crowded Coach Cards */}
          <PassengerCards
            weatherData={data.weather}
            crowdData={data.crowd}
            recData={data.compartment_recommendation}
            activeBudgetFilter={activeBudgetFilter}
            onBudgetFilterChange={onBudgetFilterChange}
            stationCode={currentParams.stationCode}
          />

          {/* 5. Stops Ahead & Busy Junctions Timeline */}
          <PassengerRouteTimeline
            itinerary={data.dynamic_eta?.upcoming_itinerary}
            currentStation={currentParams.stationCode}
            trainInfo={data.train}
          />

          {/* 6. Expandable "How PredictRail works" Technical Explanation */}
          <TechnicalAccordion
            data={data}
            currentParams={currentParams}
          />
        </div>
      )}

      {/* Empty State */}
      {!loading && !data && !error && (
        <div className="empty-state" style={{ marginTop: '1.5rem' }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ margin: '0 auto 1rem', opacity: 0.5 }}>
            <rect width="16" height="16" x="4" y="3" rx="2"></rect>
            <path d="M4 11h16"></path>
            <path d="M12 3v8"></path>
            <circle cx="8" cy="15" r="1"></circle>
            <circle cx="16" cy="15" r="1"></circle>
          </svg>
          <h3>Ready to Track Your Train</h3>
          <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Enter your train number above or pick an example to get started.</p>
        </div>
      )}
    </div>
  );
}
