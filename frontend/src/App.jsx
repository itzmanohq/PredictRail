import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import HomeView from './components/HomeView';
import JourneyView from './components/JourneyView';
import JourneyInsightsView from './components/JourneyInsightsView';
import { analyzeTrain, getCompartmentRecommendation, getDynamicEta } from './services/api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [activeBudgetFilter, setActiveBudgetFilter] = useState('ALL');
  
  // UI State Machine: 'LOADING' | 'LIVE_DATA_FOUND' | 'PREDICTION_UPDATED' | 'LIVE_DATA_STALE' | 'ARRIVED' | 'DATA_UNAVAILABLE' | 'ERROR'
  const [uiState, setUiState] = useState('LOADING');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  // Navigation tab: 'home' | 'journey' | 'insights'
  const [activeNav, setActiveNav] = useState(() => {
    if (typeof window !== 'undefined') {
      if (window.location.hash === '#journey') return 'journey';
      if (window.location.hash === '#insights') return 'insights';
    }
    return 'home';
  });

  // Stale request guard token
  const latestRequestIdRef = useRef(0);
  const currentParamsRef = useRef({
    trainNumber: '12423',
    stationCode: 'GHY',
    currentDelay: 0.0
  });

  const [currentParams, setCurrentParams] = useState({
    trainNumber: '12423',
    stationCode: 'GHY',
    currentDelay: 0.0
  });

  // Keep currentParamsRef in sync
  useEffect(() => {
    currentParamsRef.current = currentParams;
  }, [currentParams]);

  // Sync hash routing
  useEffect(() => {
    function handleHashChange() {
      if (window.location.hash === '#journey') {
        setActiveNav('journey');
      } else if (window.location.hash === '#insights') {
        setActiveNav('insights');
      } else {
        setActiveNav('home');
      }
    }
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  function handleNavChange(navId) {
    setActiveNav(navId);
    if (typeof window !== 'undefined') {
      window.location.hash = navId === 'home' ? '' : `#${navId}`;
    }
  }

  // Initial load for Train 12423 Rajdhani Express at Guwahati
  useEffect(() => {
    handleAnalyze('12423', 'GHY');
  }, []);

  const handleAnalyze = useCallback(async (trainNumber, stationCode, isBackgroundPoll = false) => {
    const isTrainSwitch = currentParamsRef.current.trainNumber !== trainNumber;
    const reqId = ++latestRequestIdRef.current;

    if (!isBackgroundPoll) {
      setLoading(true);
      setUiState('LOADING');
      setError(null);
    }

    // If switching train, immediately clear old train's data
    if (isTrainSwitch) {
      setData(null);
    }

    const updatedParams = {
      trainNumber,
      stationCode,
      currentDelay: 0.0 // Internal delay resolved automatically
    };
    setCurrentParams(updatedParams);
    currentParamsRef.current = updatedParams;

    try {
      const res = await analyzeTrain(trainNumber, stationCode, 0.0, activeBudgetFilter);
      if (reqId !== latestRequestIdRef.current) {
        return;
      }
      setData(res);
      setLastUpdated(res.last_updated || new Date().toLocaleTimeString());

      if (res.is_arrived || res.train_status === 'ARRIVED') {
        setUiState('ARRIVED');
      } else if (res.live_telemetry && res.live_telemetry.source) {
        setUiState('PREDICTION_UPDATED');
      } else {
        setUiState('LIVE_DATA_FOUND');
      }
    } catch (err) {
      if (reqId !== latestRequestIdRef.current) return;
      console.error("Analysis error:", err);
      if (data) {
        // Keep last valid state and mark as stale
        setUiState('LIVE_DATA_STALE');
      } else {
        setUiState('ERROR');
        setError(err.message || "Failed to analyze train journey.");
      }
    } finally {
      if (reqId === latestRequestIdRef.current && !isBackgroundPoll) {
        setLoading(false);
      }
    }
  }, [activeBudgetFilter, data]);

  // Periodic Auto-Polling for Live Railway Updates (every 35 seconds with tab visibility guard)
  useEffect(() => {
    if (!autoRefreshEnabled) return;

    const pollInterval = setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;
      if (currentParamsRef.current.trainNumber && currentParamsRef.current.stationCode) {
        handleAnalyze(
          currentParamsRef.current.trainNumber,
          currentParamsRef.current.stationCode,
          true
        );
      }
    }, 35000);

    return () => clearInterval(pollInterval);
  }, [autoRefreshEnabled, handleAnalyze]);

  // Real-time Dynamic ETA Recalculation on Live Telemetry Update
  const handleLiveTelemetryUpdate = useCallback(async (liveTelemetry, trainNum) => {
    if (!liveTelemetry || String(trainNum).trim() !== String(currentParamsRef.current.trainNumber).trim()) {
      return;
    }

    const liveLoc = liveTelemetry.currentLocation || {};
    const liveStation = liveLoc.stationCode || liveTelemetry.nextHalt?.stationCode;
    const liveDelay = liveLoc.delayMinutes ?? liveTelemetry.delayMinutes ?? 0.0;
    const isArrived = Boolean(liveTelemetry.is_arrived || liveTelemetry.trainStatus === 'ARRIVED');

    if (isArrived) {
      setUiState('ARRIVED');
      setData(prev => prev ? {
        ...prev,
        is_arrived: true,
        train_status: 'ARRIVED',
        arrival_time_remaining_min: 0.0,
        dynamic_eta: {
          ...prev.dynamic_eta,
          is_arrived: true,
          train_status: 'ARRIVED',
          destination_dynamic_eta: 'Arrived (0 min remaining)',
          arrival_time_remaining_min: 0.0
        }
      } : prev);
      return;
    }

    if (!liveStation) return;

    const reqId = ++latestRequestIdRef.current;
    try {
      const etaRes = await getDynamicEta(trainNum, liveStation, Number(liveDelay) || 0.0);
      if (reqId !== latestRequestIdRef.current) return;

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
            dynamic_eta: etaRes,
            last_updated: new Date().toLocaleTimeString()
          };
        });

        setCurrentParams(prev => ({
          ...prev,
          stationCode: liveStation,
          currentDelay: Number(liveDelay)
        }));

        setUiState('PREDICTION_UPDATED');
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (err) {
      console.warn("Live ETA recalculation background sync failed:", err);
      setUiState('LIVE_DATA_STALE');
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

  function handleManualRefresh() {
    if (currentParams.trainNumber && currentParams.stationCode) {
      handleAnalyze(currentParams.trainNumber, currentParams.stationCode, false);
    }
  }

  return (
    <div className="app-layout">
      {/* 1. Sidebar Navigation (Home, Journey, Journey Insights) */}
      <Sidebar
        activeNav={activeNav}
        onNavChange={handleNavChange}
      />

      {/* 2. Main Application Flow */}
      <div className="app-main-viewport">
        {/* Top Header Bar */}
        <Header
          activeNav={activeNav}
          onNavChange={handleNavChange}
          uiState={uiState}
          lastUpdated={lastUpdated}
          onRefresh={handleManualRefresh}
        />

        {/* Global Stale Data or Error Notification */}
        {uiState === 'LIVE_DATA_STALE' && (
          <div className="stale-banner card">
            <div className="stale-banner-content">
              <span className="dot-stale"></span>
              <span><strong>Notice:</strong> Live API update delayed. Showing latest available telemetry ({lastUpdated || 'recently'}).</span>
            </div>
            <button type="button" className="btn-stale-retry" onClick={handleManualRefresh}>
              ↻ Retry Live Feed
            </button>
          </div>
        )}

        {error && (
          <div className="error-banner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <div>
              <strong>Notice:</strong> {error}
            </div>
          </div>
        )}

        {/* View Switcher based on activeNav */}
        <main className="content-container">
          {activeNav === 'home' && (
            <HomeView
              data={data}
              loading={loading}
              error={error}
              uiState={uiState}
              lastUpdated={lastUpdated}
              currentParams={currentParams}
              onAnalyze={handleAnalyze}
              onNavChange={handleNavChange}
              onRefresh={handleManualRefresh}
            />
          )}

          {activeNav === 'journey' && (
            <JourneyView
              data={data}
              loading={loading}
              uiState={uiState}
              lastUpdated={lastUpdated}
              currentParams={currentParams}
              onLiveTelemetryUpdate={handleLiveTelemetryUpdate}
              onRefresh={handleManualRefresh}
            />
          )}

          {activeNav === 'insights' && (
            <JourneyInsightsView
              data={data}
              loading={loading}
              uiState={uiState}
              lastUpdated={lastUpdated}
              activeBudgetFilter={activeBudgetFilter}
              onBudgetFilterChange={handleBudgetFilterChange}
              onRefresh={handleManualRefresh}
            />
          )}
        </main>
      </div>
    </div>
  );
}
