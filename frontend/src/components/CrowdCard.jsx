import React from 'react';

export default function CrowdCard({ crowdData }) {
  if (!crowdData) return null;

  const occupancyPct = crowdData.overall_occupancy_percent ?? 0.0;
  const crowdLevel = crowdData.overall_crowd_level || 'UNKNOWN';
  const totalPax = crowdData.total_estimated_passengers ?? 0;
  const totalCap = crowdData.total_estimated_capacity ?? 0;
  const classBreakdown = crowdData.class_breakdown || [];

  let levelColor = 'green';
  if (crowdLevel === 'HIGH') {
    levelColor = 'red';
  } else if (crowdLevel === 'MEDIUM') {
    levelColor = 'orange';
  }

  return (
    <div className="card crowd-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          Prototype Crowd Estimation
        </h3>
        <span className={`badge-status ${levelColor}`}>
          {crowdLevel} DENSITY
        </span>
      </div>

      <div style={{ display: 'inline-block', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '0.15rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.68rem', fontWeight: '700', marginBottom: '0.5rem', letterSpacing: '0.04em' }}>
        SYNTHETIC PROTOTYPE DATA
      </div>

      <div className="stat-highlight" style={{ marginBottom: '0.25rem' }}>
        <span className="stat-value">{occupancyPct.toFixed(1)}%</span>
        <span className="stat-unit">Overall Train Load</span>
      </div>

      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
        Simulated passenger volume: <strong>{totalPax.toLocaleString()}</strong> / {totalCap.toLocaleString()} nominal seats
      </p>

      {/* Coach Class Breakdown Bars */}
      <div className="crowd-breakdown-list">
        {classBreakdown.map((cls) => {
          const pct = cls.average_occupancy_percent || 0.0;
          let barColor = 'green';
          if (pct > 80.0) barColor = 'red';
          else if (pct > 50.0) barColor = 'orange';

          return (
            <div key={cls.coach_class} className="crowd-bar-row">
              <div className="crowd-bar-header">
                <span>Class {cls.coach_class}</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>
                  {cls.total_passengers}/{cls.total_capacity} pax ({pct.toFixed(1)}%)
                </span>
              </div>
              <div className="progress-track">
                <div
                  className={`progress-fill ${barColor}`}
                  style={{ width: `${Math.min(100, pct)}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: '0.75rem', fontSize: '0.68rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
        * Note: Based on empirical Indian Railways rake density heuristics. Not live IoT/camera sensor feeds.
      </div>
    </div>
  );
}
