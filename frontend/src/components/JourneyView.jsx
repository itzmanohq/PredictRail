import React from 'react';
import LiveRailwayMap from './LiveRailwayMap';
import JourneyOverview from './JourneyOverview';

export default function JourneyView({
  data,
  loading,
  currentParams,
  onLiveTelemetryUpdate
}) {
  if (!data && !loading) {
    return (
      <div className="empty-journey-state card">
        <div className="empty-icon-circle">🗺</div>
        <h3>No Journey Selected</h3>
        <p>Please select a train and observation station on the Home tab to view the interactive map and route timeline.</p>
      </div>
    );
  }

  return (
    <div className="journey-view-container">
      {/* 1. Interactive Real Geographic Map */}
      <LiveRailwayMap
        trainNumber={currentParams?.trainNumber}
        stationCode={currentParams?.stationCode}
        trainInfo={data?.train}
        bottlenecks={data?.network_bottlenecks || []}
        itinerary={data?.dynamic_eta?.upcoming_itinerary || []}
        nearbyRadiusKm={150}
        onLiveTelemetryUpdate={onLiveTelemetryUpdate}
      />

      {/* 2. Compact Milestone Timeline Overview */}
      <JourneyOverview
        data={data}
        currentStationCode={currentParams?.stationCode}
      />
    </div>
  );
}
