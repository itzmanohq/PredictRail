import React, { useState, useEffect, useRef } from 'react';
import { getTrains, getTrainDetail } from '../services/api';

const POPULAR_EXAMPLES = [
  { number: '12637', name: 'Pandian Express', station: 'TBM', delay: 15.0, label: '12637 Pandian Exp (Tambaram)' },
  { number: '12423', name: 'Rajdhani Express', station: 'GHY', delay: 30.0, label: '12423 Rajdhani (Guwahati)' },
  { number: '13009', name: 'Doon Express', station: 'HWH', delay: 15.0, label: '13009 Doon Exp (Howrah)' },
  { number: '12002', name: 'Bhopal Shatabdi', station: 'NDLS', delay: 0.0, label: '12002 Shatabdi (New Delhi)' }
];

export default function PassengerHeroSearch({
  onAnalyze,
  loading,
  currentTrainNumber,
  currentStationCode
}) {
  const [trainQuery, setTrainQuery] = useState(currentTrainNumber || '12423');
  const [trainSuggestions, setTrainSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTrainDetail, setSelectedTrainDetail] = useState(null);
  const [selectedStation, setSelectedStation] = useState(currentStationCode || 'GHY');
  const [observedDelay, setObservedDelay] = useState(30.0);
  const dropdownRef = useRef(null);

  // Sync state if external selection changes
  useEffect(() => {
    if (currentTrainNumber && currentTrainNumber !== trainQuery) {
      setTrainQuery(currentTrainNumber);
      loadTrainStops(currentTrainNumber, false);
    }
  }, [currentTrainNumber]);

  useEffect(() => {
    if (currentStationCode && currentStationCode !== selectedStation) {
      setSelectedStation(currentStationCode);
    }
  }, [currentStationCode]);

  // Load initial train detail
  useEffect(() => {
    loadTrainStops(trainQuery || '12423', false);
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
    const timer = setTimeout(search, 200);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [trainQuery]);

  async function loadTrainStops(tNo, autoAnalyze = false) {
    try {
      const detail = await getTrainDetail(tNo);
      if (detail && detail.stops && detail.stops.length > 0) {
        setSelectedTrainDetail(detail);
        let targetStation = selectedStation;
        const hasStation = detail.stops.some(s => s.station_code === selectedStation);
        if (!hasStation) {
          targetStation = detail.stops[0].station_code;
          setSelectedStation(targetStation);
        }
        if (autoAnalyze) {
          onAnalyze(tNo, targetStation, Number(observedDelay) || 0.0);
        }
      }
    } catch (err) {
      console.warn("Could not load stops for train:", tNo);
    }
  }

  function handleSelectSuggestion(train) {
    setTrainQuery(train.train_number);
    setShowDropdown(false);
    loadTrainStops(train.train_number, true);
  }

  function handleExampleClick(example) {
    setTrainQuery(example.number);
    setSelectedStation(example.station);
    setObservedDelay(example.delay);
    loadTrainStops(example.number, false);
    onAnalyze(example.number, example.station, example.delay);
  }

  function handleStationSelect(stnCode) {
    setSelectedStation(stnCode);
    if (trainQuery.trim()) {
      onAnalyze(trainQuery.trim(), stnCode, Number(observedDelay) || 0.0);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!trainQuery.trim()) return;
    onAnalyze(trainQuery.trim(), selectedStation || 'GHY', Number(observedDelay) || 0.0);
  }

  return (
    <section className="passenger-hero-search card">
      <div className="passenger-hero-header">
        <div className="passenger-hero-badge">
          <span className="pulse-circle"></span>
          INDIAN RAILWAYS PASSENGER ASSISTANT
        </div>
        <h2 className="passenger-hero-title">Where is my train?</h2>
        <p className="passenger-hero-subtitle">
          Find your train's live location, expected arrival time, delays, and less crowded coaches in 5 seconds.
        </p>
      </div>

      <form className="passenger-search-form" onSubmit={handleSubmit}>
        {/* Train Number Input & Dropdown */}
        <div className="search-field-group" ref={dropdownRef}>
          <label className="search-field-label">Train Number or Name</label>
          <div className="search-input-wrapper">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="input-icon">
              <rect width="16" height="16" x="4" y="3" rx="2"></rect>
              <path d="M4 11h16"></path>
              <path d="M12 3v8"></path>
              <circle cx="8" cy="15" r="1"></circle>
              <circle cx="16" cy="15" r="1"></circle>
            </svg>
            <input
              type="text"
              className="passenger-search-input"
              placeholder="Enter 5-digit number (e.g. 12637, 12423, 13009)"
              value={trainQuery}
              onChange={(e) => {
                setTrainQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
            />
          </div>

          {showDropdown && trainSuggestions.length > 0 && (
            <div className="passenger-autocomplete-dropdown">
              {trainSuggestions.map((t) => (
                <button
                  key={t.train_number}
                  type="button"
                  className="dropdown-item"
                  onClick={() => handleSelectSuggestion(t)}
                >
                  <span className="dropdown-item-num">{t.train_number}</span>
                  <span className="dropdown-item-name">{t.train_name}</span>
                  <span className="dropdown-item-route">{t.source_station} → {t.destination_station}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Station Selector Dropdown */}
        <div className="search-field-group">
          <label className="search-field-label">Your Station</label>
          <div className="search-input-wrapper">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="input-icon">
              <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <select
              className="passenger-select-input"
              value={selectedStation}
              onChange={(e) => handleStationSelect(e.target.value)}
            >
              {selectedTrainDetail?.stops && selectedTrainDetail.stops.length > 0 ? (
                selectedTrainDetail.stops.map((s) => (
                  <option key={s.station_code} value={s.station_code}>
                    {s.station_name} ({s.station_code})
                  </option>
                ))
              ) : (
                <option value="TBM">Tambaram (TBM)</option>
              )}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <div className="search-submit-group">
          <button
            type="submit"
            className="btn-passenger-find"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="mini-spinner"></span>
                <span>Finding Train...</span>
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <span>Find My Train</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Try an Example Quick Badges */}
      <div className="passenger-examples-strip">
        <span className="examples-label">Try an Example:</span>
        <div className="examples-badges-list">
          {POPULAR_EXAMPLES.map((ex) => (
            <button
              key={ex.number}
              type="button"
              className={`btn-example-chip ${trainQuery === ex.number ? 'active' : ''}`}
              onClick={() => handleExampleClick(ex)}
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
