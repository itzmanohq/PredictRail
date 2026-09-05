import React, { useState, useEffect, useRef, useCallback } from 'react';
import Header from './components/Header';
import PassengerDashboard from './components/PassengerDashboard';
import ClassicDashboard from './components/ClassicDashboard';
import { analyzeTrain, getCompartmentRecommendation, getDynamicEta } from './services/api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [activeBudgetFilter, setActiveBudgetFilter] = useState('ALL');

  // Stale request guard token
  const latestRequestIdRef = useRef(0);
  const currentParamsRef = useRef({
    trainNumber: '12637',
    stationCode: 'TBM',
    currentDelay: 15.0
  });

  // Determine initial view mode from URL hash or path
  const [viewMode, setViewMode] = useState(() => {
    if (typeof window !== 'undefined') {
      if (window.location.hash === '#classic' || window.location.pathname === '/classic') {
        return 'classic';
      }
    }
    return 'passenger';
  });

  const [currentParams, setCurrentParams] = useState({
    trainNumber: '12637',
    stationCode: 'TBM',
    currentDelay: 15.0
  });

  // Keep currentParamsRef in sync
  useEffect(() => {
    currentParamsRef.current = currentParams;
  }, [currentParams]);

  // Listen to hash change for #classic / #passenger routing
  useEffect(() => {
    function handleHashChange() {
      if (window.location.hash === '#classic' || window.location.pathname === '/classic') {
        setViewMode('classic');
      } else if (window.location.hash === '#passenger' || window.location.pathname === '/') {
        setViewMode('passenger');
      }
    }
    window.addEventListener('hashchange', handleHashChange);
    window.addEventListener('popstate', handleHashChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
      window.removeEventListener('popstate', handleHashChange);
    };
  }, []);

  // Update URL hash when view mode changes
  function handleViewModeChange(mode) {
    setViewMode(mode);
    if (typeof window !== 'undefined') {
      window.location.hash = mode === 'classic' ? '#classic' : '#passenger';
    }
  }

  // Run initial analysis for Train 12637 Pandian Express at Tambaram
  useEffect(() => {
    handleAnalyze('12637', 'TBM', 15.0);
  }, []);

  const handleAnalyze = useCallback(async (trainNumber, stationCode, delay) => {
    const isTrainSwitch = currentParamsRef.current.trainNumber !== trainNumber;
    const reqId = ++latestRequestIdRef.current;

    setLoading(true);
    setError(null);

    // If switching train, immediately clear old train's data so stale ETA does not linger
    if (isTrainSwitch) {
      setData(null);
    }

    const updatedParams = { trainNumber, stationCode, currentDelay: delay };
    setCurrentParams(updatedParams);
    currentParamsRef.current = updatedParams;

    try {
      const res = await analyzeTrain(trainNumber, stationCode, delay, activeBudgetFilter);
      // Stale response protection: discard if superseded by a newer request
      if (reqId !== latestRequestIdRef.current) {
        return;
      }
      setData(res);
    } catch (err) {
      if (reqId !== latestRequestIdRef.current) return;
      console.error("Analysis error:", err);
      setError(err.message || "Failed to analyze train delay and route.");
    } finally {
      if (reqId === latestRequestIdRef.current) {
        setLoading(false);
      }
    }
  }, [activeBudgetFilter]);

  // Real-time Dynamic ETA Recalculation on Live Telemetry Update
  const handleLiveTelemetryUpdate = useCallback(async (liveTelemetry, trainNum) => {
    if (!liveTelemetry || String(trainNum).trim() !== String(currentParamsRef.current.trainNumber).trim()) {
      return;
    }

    const liveLoc = liveTelemetry.currentLocation || {};
    const liveStation = liveLoc.stationCode || liveTelemetry.nextHalt?.stationCode;
    const liveDelay = liveLoc.delayMinutes ?? liveTelemetry.delayMinutes ?? currentParamsRef.current.currentDelay ?? 0.0;

    if (!liveStation) return;

    const reqId = ++latestRequestIdRef.current;
    try {
      // Recalculate multi-stop Dynamic ETA and destination arrival time from latest live station and delay
      const etaRes = await getDynamicEta(trainNum, liveStation, Number(liveDelay) || 0.0);
      
      if (reqId !== latestRequestIdRef.current) {
        return;
      }

      if (etaRes && etaRes.success) {
        setData(prev => {
          if (!prev || String(prev.train?.train_number).trim() !== String(trainNum).trim()) {
            return prev;
          }
          return {
            ...prev,
            delay_prediction: {
              ...prev.delay_prediction,
              predicted_delay_minutes: Number(liveDelay) || prev.delay_prediction?.predicted_delay_minutes || 0.0,
              current_delay_minutes: Number(liveDelay)
            },
            dynamic_eta: etaRes
          };
        });

        setCurrentParams(prev => ({
          ...prev,
          stationCode: liveStation,
          currentDelay: Number(liveDelay)
        }));
      }
    } catch (err) {
      console.warn("Live ETA recalculation background sync failed:", err);
    }
  }, []);

  async function handleBudgetFilterChange(newFilter) {
    setActiveBudgetFilter(newFilter);
    if (!data || !currentParams.trainNumber || !currentParams.stationCode) return;
    try {
      const recRes = await getCompartmentRecommendation(
        currentParams.trainNumber,
        currentParams.stationCode,
        newFilter
      );
      if (recRes && recRes.success) {
        setData(prev => ({
          ...prev,
          compartment_recommendation: recRes
        }));
      }
    } catch (err) {
      console.error("Error updating compartment recommendation:", err);
    }
  }

  return (
    <div className="dashboard-container">
      <Header
        viewMode={viewMode}
        onViewModeChange={handleViewModeChange}
      />

      {error && (
        <div className="error-banner">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div>
            <strong>Analysis Warning:</strong> {error}
          </div>
        </div>
      )}

      {/* Render either Passenger View (Default) or Classic / Expert View */}
      {viewMode === 'classic' ? (
        <ClassicDashboard
          data={data}
          loading={loading}
          error={error}
          currentParams={currentParams}
          activeBudgetFilter={activeBudgetFilter}
          onAnalyze={handleAnalyze}
          onBudgetFilterChange={handleBudgetFilterChange}
          onLiveTelemetryUpdate={handleLiveTelemetryUpdate}
        />
      ) : (
        <PassengerDashboard
          data={data}
          loading={loading}
          error={error}
          currentParams={currentParams}
          activeBudgetFilter={activeBudgetFilter}
          onAnalyze={handleAnalyze}
          onBudgetFilterChange={handleBudgetFilterChange}
          onLiveTelemetryUpdate={handleLiveTelemetryUpdate}
        />
      )}
    </div>
  );
}
