import React from 'react';
import JourneyInputCard from './JourneyInputCard';

export default function HomeView({
  data,
  loading,
  error,
  currentParams,
  onAnalyze,
  onNavChange
}) {
  const train = data?.train;
  const predictedDelay = data?.delay_prediction?.predicted_delay_minutes ?? 0;
  const arrivalEta = data?.dynamic_eta?.destination_dynamic_eta || '--:--';
  const recData = data?.compartment_recommendation;

  return (
    <div className="home-view-container">
      {/* Hero Section */}
      <section className="hero-clean-section">
        <div className="hero-text-content">
          <div className="hero-mini-pill">
            <span className="sparkle-icon">✨</span>
            <span>AI-Powered Rail Assistant</span>
          </div>
          <h1 className="hero-headline">
            Plan your journey<br />
            with confidence
          </h1>
          <p className="hero-tagline">
            Accurate delay predictions, live geographic route maps, and smart coach guidance.
          </p>
        </div>

        {/* Clean Modern Flat SVG Train Graphic */}
        <div className="hero-graphic-box">
          <svg viewBox="0 0 320 180" className="hero-train-svg" aria-label="Modern Train Illustration">
            {/* Soft background pastel hill */}
            <path d="M0 160 Q 80 120, 180 145 T 320 150 L 320 180 L 0 180 Z" fill="#ecfdf5" />
            <path d="M0 168 L 320 168" stroke="#d1fae5" strokeWidth="4" strokeDasharray="12 8" />
            
            {/* Speed tracks */}
            <line x1="20" y1="172" x2="300" y2="172" stroke="#10b981" strokeWidth="3" strokeLinecap="round" />
            
            {/* Modern Train Body */}
            <g transform="translate(45, 60)">
              {/* Shadow */}
              <rect x="10" y="96" width="210" height="10" rx="5" fill="#d1fae5" />
              
              {/* Train Locomotive / Lead Coach */}
              <path d="M 0 30 Q 0 15, 15 15 L 170 15 Q 215 15, 230 65 Q 235 85, 225 95 L 0 95 Z" fill="#ffffff" stroke="#10b981" strokeWidth="3.5" />
              
              {/* Mint Green Stripe */}
              <path d="M 0 65 L 230 65 Q 233 75, 228 80 L 0 80 Z" fill="#10b981" />
              <rect x="0" y="82" width="225" height="4" fill="#047857" />
              
              {/* Front Windshield Glass */}
              <path d="M 175 25 L 210 55 L 175 55 Z" fill="#06b6d4" opacity="0.85" />
              
              {/* Passenger Windows */}
              <rect x="20" y="32" width="30" height="22" rx="6" fill="#0f172a" />
              <rect x="60" y="32" width="30" height="22" rx="6" fill="#0f172a" />
              <rect x="100" y="32" width="30" height="22" rx="6" fill="#0f172a" />
              <rect x="140" y="32" width="24" height="22" rx="6" fill="#0f172a" />
              
              {/* Window glass highlights */}
              <line x1="26" y1="36" x2="44" y2="50" stroke="#06b6d4" strokeWidth="2" strokeLinecap="round" />
              <line x1="66" y1="36" x2="84" y2="50" stroke="#06b6d4" strokeWidth="2" strokeLinecap="round" />
              <line x1="106" y1="36" x2="124" y2="50" stroke="#06b6d4" strokeWidth="2" strokeLinecap="round" />

              {/* Headlight */}
              <circle cx="225" cy="85" r="5" fill="#f59e0b" />
              
              {/* Wheels */}
              <circle cx="35" cy="100" r="10" fill="#334155" stroke="#ffffff" strokeWidth="2" />
              <circle cx="65" cy="100" r="10" fill="#334155" stroke="#ffffff" strokeWidth="2" />
              <circle cx="165" cy="100" r="10" fill="#334155" stroke="#ffffff" strokeWidth="2" />
              <circle cx="195" cy="100" r="10" fill="#334155" stroke="#ffffff" strokeWidth="2" />
            </g>
          </svg>
        </div>
      </section>

      {/* Journey Selection Form Card */}
      <JourneyInputCard
        onAnalyze={onAnalyze}
        loading={loading}
        currentTrainNumber={currentParams?.trainNumber}
        currentStationCode={currentParams?.stationCode}
      />

      {/* Loading State Overlay */}
      {loading && !data && (
        <div className="card loading-card">
          <div className="spinner-mint large"></div>
          <p className="loading-text">Calculating ML delay forecasts & railway graph progression...</p>
        </div>
      )}

      {/* Quick Summary Results (When Data Available) */}
      {data && train && (
        <div className="home-results-section">
          {/* Main Trip Status Strip */}
          <div className="home-trip-banner card">
            <div className="trip-banner-left">
              <span className="trip-badge">ANALYSED JOURNEY</span>
              <h3 className="trip-name">
                <span className="trip-num-pill">{train.train_number}</span> {train.train_name}
              </h3>
              <p className="trip-corridor-text">
                {train.source_name || train.source_station} &rarr; {train.destination_name || train.destination_station}
              </p>
            </div>

            <div className="trip-banner-right">
              {predictedDelay <= 10 ? (
                <div className="status-chip-hero green">
                  <span className="dot-pulse"></span>
                  <span>RUNNING ON TIME</span>
                </div>
              ) : (
                <div className="status-chip-hero amber">
                  <span>⏱ +{Math.round(predictedDelay)} MIN DELAY</span>
                </div>
              )}
              <span className="telemetry-source-tag">Latest available data</span>
            </div>
          </div>

          {/* Quick Jump 3-Cards Row */}
          <div className="home-quick-cards-grid">
            {/* 1. Delay & Arrival Preview */}
            <div className="quick-summary-card card" onClick={() => onNavChange('insights')}>
              <div className="quick-card-top">
                <span className="quick-card-icon green">⏱</span>
                <span className="quick-card-label">Arrival Forecast</span>
              </div>
              <div className="quick-main-stat text-blue">{arrivalEta}</div>
              <p className="quick-card-desc">
                {predictedDelay <= 10 ? 'No major delay expected' : `+${Math.round(predictedDelay)}m late at destination`}
              </p>
              <button type="button" className="quick-card-link">
                View Journey Insights &rarr;
              </button>
            </div>

            {/* 2. Live Route Map Preview */}
            <div className="quick-summary-card card" onClick={() => onNavChange('journey')}>
              <div className="quick-card-top">
                <span className="quick-card-icon blue">🗺</span>
                <span className="quick-card-label">Interactive Map</span>
              </div>
              <div className="quick-main-stat text-primary" style={{ fontSize: '1.25rem' }}>
                {data.dynamic_eta?.current_station_name || currentParams.stationCode}
              </div>
              <p className="quick-card-desc">
                Observed station · {train.stations_count || 20} corridor halts
              </p>
              <button type="button" className="quick-card-link">
                View Geographic Map &rarr;
              </button>
            </div>

            {/* 3. Coach Recommendation Preview */}
            <div className="quick-summary-card card" onClick={() => onNavChange('insights')}>
              <div className="quick-card-top">
                <span className="quick-card-icon lime">★</span>
                <span className="quick-card-label">Smart Coach</span>
              </div>
              <div className="quick-main-stat text-brand">
                {recData?.recommended_coach_or_class || '2A'} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>({recData?.recommended_coach_id || 'A1'})</span>
              </div>
              <p className="quick-card-desc">
                Least crowded coach for this journey
              </p>
              <button type="button" className="quick-card-link">
                View Coach Breakdown &rarr;
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
