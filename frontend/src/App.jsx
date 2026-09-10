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

  const handleAnalyze = useCallback(async (trainNumber, stationCode) => {
    const isTrainSwitch = currentParamsRef.current.trainNumber !== trainNumber;
    const reqId = ++latestRequestIdRef.current;

    setLoading(true);
    setError(null);

    // If switching train, immediately clear old train's data
    if (isTrainSwitch) {
      setData(null);
    }

    const updatedParams = {
      trainNumber,
      stationCode,
      currentDelay: 0.0 // Internal delay obtained from backend
    };
    setCurrentParams(updatedParams);
    currentParamsRef.current = updatedParams;

    try {
      // Analyze with internal delay
      const res = await analyzeTrain(trainNumber, stationCode, 0.0, activeBudgetFilter);
      if (reqId !== latestRequestIdRef.current) {
        return;
      }
      setData(res);
    } catch (err) {
      if (reqId !== latestRequestIdRef.current) return;
      console.error("Analysis error:", err);
      setError(err.message || "Failed to analyze train journey.");
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
    const liveDelay = liveLoc.delayMinutes ?? liveTelemetry.delayMinutes ?? 0.0;

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
    <div className="app-layout">
      {/* 1. Sidebar Navigation (Home, Journey, Journey Insights) */}
      <Sidebar
        activeNav={activeNav}
        onNavChange={handleNavChange}
      />

      {/* 2. Main Application Flow */}
      <div className="app-main-viewport">
        {/* Top Header Bar (No user avatar, No settings) */}
        <Header
          activeNav={activeNav}
          onNavChange={handleNavChange}
        />

        {/* Global Error Banner */}
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
              currentParams={currentParams}
              onAnalyze={handleAnalyze}
              onNavChange={handleNavChange}
            />
          )}

          {activeNav === 'journey' && (
            <JourneyView
              data={data}
              loading={loading}
              currentParams={currentParams}
              onLiveTelemetryUpdate={handleLiveTelemetryUpdate}
            />
          )}

          {activeNav === 'insights' && (
            <JourneyInsightsView
              data={data}
              loading={loading}
              activeBudgetFilter={activeBudgetFilter}
              onBudgetFilterChange={handleBudgetFilterChange}
            />
          )}
        </main>
      </div>
    </div>
  );
}
