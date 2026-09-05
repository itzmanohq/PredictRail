import React, { useState, useEffect, useRef } from 'react';
import { getTrains, getTrainDetail } from '../services/api';

export default function TrainSelector({ onAnalyze, loading }) {
  const [trainQuery, setTrainQuery] = useState('12423');
  const [trainSuggestions, setTrainSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [stations, setStations] = useState([]);
  const [currentStation, setCurrentStation] = useState('GHY');
  const [currentDelay, setCurrentDelay] = useState(30.0);
  const [errorMsg, setErrorMsg] = useState(null);

  const dropdownRef = useRef(null);

  // Search trains on query change
  useEffect(() => {
    let active = true;
    async function search() {
      if (!trainQuery || trainQuery.length < 2) {
        setTrainSuggestions([]);
        return;
      }
      try {
        const res = await getTrains(trainQuery, 10);
        if (active && res && res.trains) {
          setTrainSuggestions(res.trains);
        }
      } catch (err) {
        console.error("Error searching trains:", err);
      }
    }
    const timer = setTimeout(search, 200);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [trainQuery]);

  // Load initial train data on mount (Train 12423 Rajdhani)
  useEffect(() => {
    handleSelectTrainNumber('12423', false);
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

  async function handleSelectTrainNumber(tNo, autoAnalyze = false) {
    setShowDropdown(false);
    setErrorMsg(null);
    try {
      const detail = await getTrainDetail(tNo);
      if (detail) {
        setSelectedTrain(detail);
        setTrainQuery(detail.train_number);
        setStations(detail.stops || []);
        
        // Pick an intermediate station or first stop
        if (detail.stops && detail.stops.length > 0) {
          // If GHY is on route, select GHY, else select first stop
          const hasGhy = detail.stops.some(s => s.station_code === 'GHY');
          const defaultStn = hasGhy ? 'GHY' : detail.stops[0].station_code;
          setCurrentStation(defaultStn);
        }
      }
    } catch (err) {
      setErrorMsg(`Failed to load train ${tNo}: ${err.message}`);
    }
  }

  function handleFormSubmit(e) {
    e.preventDefault();
    if (!trainQuery.trim()) {
      setErrorMsg("Please enter a valid Indian Railways train number.");
      return;
    }
    if (!currentStation) {
      setErrorMsg("Please select an observation station.");
      return;
    }
    setErrorMsg(null);
    onAnalyze(trainQuery.trim(), currentStation, Number(currentDelay) || 0.0);
  }

  return (
    <aside className="card selector-panel">
      <div className="card-header">
        <h2 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path>
            <line x1="4" y1="22" x2="4" y2="15"></line>
          </svg>
          Train Parameter Controls
        </h2>
        <span className="card-badge">INPUT</span>
      </div>

      <form onSubmit={handleFormSubmit} className="selector-form">
        {/* Train Number / Name Search */}
        <div className="form-group" ref={dropdownRef}>
          <label className="form-label" htmlFor="train-input">Train Number / Name</label>
          <input
            id="train-input"
            type="text"
            className="input-field"
            placeholder="e.g. 12423 or Rajdhani"
            value={trainQuery}
            onChange={(e) => {
              setTrainQuery(e.target.value);
              setShowDropdown(true);
            }}
            onFocus={() => setShowDropdown(true)}
            autoComplete="off"
          />

          {showDropdown && trainSuggestions.length > 0 && (
            <div className="autocomplete-dropdown">
              {trainSuggestions.map((t) => (
                <div
                  key={t.train_number}
                  className="autocomplete-item"
                  onClick={() => handleSelectTrainNumber(t.train_number)}
                >
                  <div>
                    <span className="autocomplete-train-no">{t.train_number}</span>
                    <span className="autocomplete-train-name"> - {t.train_name}</span>
                  </div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {t.source_station} &rarr; {t.destination_station}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Train Metadata Card */}
        {selectedTrain && (
          <div className="train-summary-strip">
            <div className="train-summary-route">
              <span>{selectedTrain.train_name}</span>
            </div>
            <div className="train-summary-meta">
              <span>Origin: <strong>{selectedTrain.source_station}</strong></span>
              <span>&rarr;</span>
              <span>Terminus: <strong>{selectedTrain.destination_station}</strong></span>
            </div>
            <div className="train-summary-meta">
              <span>{selectedTrain.stations_count} Stations</span>
              <span>{selectedTrain.route_distance_km} km Corridor</span>
            </div>
          </div>
        )}

        {/* Current Station Selection */}
        <div className="form-group" style={{ marginTop: '0.75rem' }}>
          <label className="form-label" htmlFor="station-select">Current Observation Station</label>
          <select
            id="station-select"
            className="select-field"
            value={currentStation}
            onChange={(e) => setCurrentStation(e.target.value)}
          >
            {stations.map((stn) => (
              <option key={stn.station_code} value={stn.station_code}>
                [{stn.station_code}] {stn.station_name} {stn.departure_time ? `(Dep: ${stn.departure_time})` : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Observed Departure Delay */}
        <div className="form-group" style={{ marginTop: '0.75rem' }}>
          <label className="form-label" htmlFor="delay-input">Observed Departure Delay (Minutes)</label>
          <input
            id="delay-input"
            type="number"
            min="0"
            max="1440"
            step="1"
            className="input-field"
            value={currentDelay}
            onChange={(e) => setCurrentDelay(Math.max(0, parseFloat(e.target.value) || 0))}
          />
        </div>

        {errorMsg && (
          <div className="error-banner" style={{ marginTop: '0.75rem', fontSize: '0.8rem', padding: '0.5rem 0.75rem' }}>
            {errorMsg}
          </div>
        )}

        {/* Analyze Button */}
        <button
          type="submit"
          className="btn-analyze"
          disabled={loading}
          id="btn-analyze-train"
        >
          {loading ? (
            <>
              <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></div>
              <span>Processing ML & Graph...</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>ANALYZE TRAIN</span>
            </>
          )}
        </button>
      </form>
    </aside>
  );
}
