import React, { useState, useEffect, useRef } from 'react';
import { getTrains, getTrainDetail, getLiveTrainStatus } from '../services/api';

const POPULAR_EXAMPLES = [
  { number: '12423', name: 'Rajdhani Express', station: 'GHY', label: '12423 Rajdhani · GHY' },
  { number: '12637', name: 'Pandian Express', station: 'TBM', label: '12637 Pandian · TBM' },
  { number: '13009', name: 'Doon Express', station: 'HWH', label: '13009 Doon Exp · HWH' },
  { number: '12002', name: 'Bhopal Shatabdi', station: 'NDLS', label: '12002 Shatabdi · NDLS' }
];

export default function JourneyInputCard({
  onAnalyze,
  loading,
  currentTrainNumber,
  currentStationCode,
  liveStatus
}) {
  const [trainQuery, setTrainQuery] = useState(currentTrainNumber || '12423');
  const [trainSuggestions, setTrainSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTrainDetail, setSelectedTrainDetail] = useState(null);
  const [selectedStation, setSelectedStation] = useState(currentStationCode || 'GHY');
  const [passedStationsList, setPassedStationsList] = useState([]);
  const [isTrainArrived, setIsTrainArrived] = useState(false);
  const dropdownRef = useRef(null);

  // Sync state if external selection changes
  useEffect(() => {
    if (currentTrainNumber && currentTrainNumber !== trainQuery) {
      setTrainQuery(currentTrainNumber);
      loadTrainStopsAndLive(currentTrainNumber, false);
    }
  }, [currentTrainNumber]);

  useEffect(() => {
    if (currentStationCode && currentStationCode !== selectedStation) {
      setSelectedStation(currentStationCode);
    }
  }, [currentStationCode]);

  // Load initial train detail and live position
  useEffect(() => {
    loadTrainStopsAndLive(trainQuery || '12423', false);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Autocomplete search
  useEffect(() => {
    let active = true;
    async function search() {
      if (!trainQuery || trainQuery.length < 2) {
        setTrainSuggestions([]);
        return;
      }
      try {
        const res = await getTrains(trainQuery, 8);
        if (active && res && res.trains) {
          setTrainSuggestions(res.trains);
        }
      } catch (err) {
        // quiet fallback
      }
    }
    const timer = setTimeout(search, 180);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [trainQuery]);

  async function loadTrainStopsAndLive(tNo, autoAnalyze = false) {
    try {
      const [detail, liveRes] = await Promise.all([
        getTrainDetail(tNo).catch(() => null),
        getLiveTrainStatus(tNo).catch(() => null)
      ]);

      if (detail && detail.stops && detail.stops.length > 0) {
        setSelectedTrainDetail(detail);

        const liveData = liveRes?.data || {};
        const passed = liveData.passed_stations || [];
        const isArrived = Boolean(liveData.is_arrived || liveData.trainStatus === 'ARRIVED');
        const liveCurrentStn = liveData.current_station_code || liveData.currentLocation?.stationCode;

        setPassedStationsList(passed);
        setIsTrainArrived(isArrived);

        // Filter valid selectable stops (not already departed)
        const validStops = detail.stops.filter(s => !passed.includes(s.station_code));
        
        let targetStation = selectedStation;

        if (isArrived) {
          // If already at destination, target the destination stop
          targetStation = detail.stops[detail.stops.length - 1].station_code;
        } else if (liveCurrentStn && validStops.some(s => s.station_code === liveCurrentStn)) {
          // Prefer current live observation station
          targetStation = liveCurrentStn;
        } else if (!validStops.some(s => s.station_code === selectedStation)) {
          // Fallback to first remaining valid stop
          targetStation = validStops.length > 0 ? validStops[0].station_code : detail.stops[0].station_code;
        }

        setSelectedStation(targetStation);

        if (autoAnalyze) {
          onAnalyze(tNo, targetStation);
        }
      }
    } catch (err) {
      console.warn("Could not load stops for train:", tNo);
    }
  }

  function handleSelectSuggestion(train) {
    setTrainQuery(train.train_number);
    setShowDropdown(false);
    loadTrainStopsAndLive(train.train_number, true);
  }

  function handleExampleClick(example) {
    setTrainQuery(example.number);
    setSelectedStation(example.station);
    loadTrainStopsAndLive(example.number, false);
    onAnalyze(example.number, example.station);
  }

  function handleStationSelect(stnCode) {
    setSelectedStation(stnCode);
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!trainQuery.trim()) return;
    onAnalyze(trainQuery.trim(), selectedStation || 'GHY');
  }

  // Filtered stops for dropdown (only valid remaining stops)
  const availableStops = (selectedTrainDetail?.stops || []).filter(
    s => !passedStationsList.includes(s.station_code)
  );

  return (
    <div className="journey-input-card card">
      <div className="input-card-header">
        <div>
          <h3 className="input-card-title">Select Your Journey</h3>
          <span className="input-card-subtitle">Live route & observation point for real-time delay forecasts</span>
        </div>
        {isTrainArrived && (
          <span className="status-pill green">
            ✓ Journey Completed · ARRIVED
          </span>
        )}
      </div>

      <form className="journey-search-form" onSubmit={handleSubmit}>
        {/* Field 1: Train Number / Name */}
        <div className="form-field-group" ref={dropdownRef}>
          <label className="field-label" htmlFor="train-search-input">Train</label>
          <div className="field-input-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="field-icon">
              <rect width="16" height="16" x="4" y="3" rx="2"></rect>
              <path d="M4 11h16"></path>
              <path d="M12 3v8"></path>
              <circle cx="8" cy="15" r="1"></circle>
              <circle cx="16" cy="15" r="1"></circle>
            </svg>
            <input
              id="train-search-input"
              type="text"
              className="field-input"
              placeholder="e.g. 12423 or Rajdhani Express"
              value={trainQuery}
              onChange={(e) => {
                setTrainQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              autoComplete="off"
            />
          </div>

          {/* Autocomplete Dropdown */}
          {showDropdown && trainSuggestions.length > 0 && (
            <div className="autocomplete-flyout">
              {trainSuggestions.map((t) => (
                <button
                  key={t.train_number}
                  type="button"
                  className="flyout-item"
                  onClick={() => handleSelectSuggestion(t)}
                >
                  <span className="flyout-num">{t.train_number}</span>
                  <span className="flyout-name">{t.train_name}</span>
                  <span className="flyout-route">{t.source_station} → {t.destination_station}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Field 2: Observation Station (Passed stations strictly excluded) */}
        <div className="form-field-group">
          <label className="field-label" htmlFor="station-select-input">
            Observation Station {passedStationsList.length > 0 && <span className="text-muted">({passedStationsList.length} passed stations hidden)</span>}
          </label>
          <div className="field-input-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="field-icon">
              <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <select
              id="station-select-input"
              className="field-select"
              value={selectedStation}
              onChange={(e) => handleStationSelect(e.target.value)}
              disabled={isTrainArrived}
            >
              {isTrainArrived ? (
                <option value={selectedStation}>
                  {selectedTrainDetail?.destination_name || 'Terminus'} ({selectedStation}) · Arrived
                </option>
              ) : availableStops.length > 0 ? (
                availableStops.map((s) => (
                  <option key={s.station_code} value={s.station_code}>
                    {s.station_name} ({s.station_code}) {s.departure_time ? `· Dep ${s.departure_time}` : ''}
                  </option>
                ))
              ) : (
                <>
                  <option value="GHY">Guwahati (GHY)</option>
                  <option value="HWH">Howrah (HWH)</option>
                  <option value="NDLS">New Delhi (NDLS)</option>
                </>
              )}
            </select>
          </div>
        </div>

        {/* Field 3: Submit Action Button */}
        <div className="form-submit-group">
          <button
            type="submit"
            className="btn-primary-action"
            disabled={loading}
            id="btn-analyse-journey"
          >
            {loading ? (
              <>
                <span className="spinner-mint"></span>
                <span>Analysing...</span>
              </>
            ) : isTrainArrived ? (
              <>
                <span>✓ View Completed Journey</span>
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Analyse Journey</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Quick Example Chips */}
      <div className="quick-examples-strip">
        <span className="examples-tag">Popular Trains:</span>
        <div className="examples-chips">
          {POPULAR_EXAMPLES.map((ex) => (
            <button
              key={ex.number}
              type="button"
              className={`chip-btn ${trainQuery === ex.number ? 'active' : ''}`}
              onClick={() => handleExampleClick(ex)}
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
