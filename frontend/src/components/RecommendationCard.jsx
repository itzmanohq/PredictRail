import React, { useMemo } from 'react';

const CLASS_DISPLAY_NAMES = {
  '1A': 'AC First Class (1A)',
  '2A': 'AC 2-Tier (2A)',
  '3A': 'AC 3-Tier (3A)',
  '3E': 'AC 3 Economy (3E)',
  'SL': 'Sleeper Class (SL)',
  'GEN': 'General Unreserved (GEN/GS)',
  'GS': 'General Second Class (GS)',
  'CC': 'AC Chair Car (CC)',
  'EC': 'Executive Chair Car (EC)',
  '2S': 'Second Sitting (2S)'
};

const AC_CLASSES = ['1A', '2A', '3A', '3E', 'CC', 'EC'];
const NON_AC_CLASSES = ['SL', '2S', 'GEN', 'GS'];

export default function RecommendationCard({
  recData,
  crowdData,
  activeFilter = 'ALL',
  onFilterChange
}) {
  if (!recData && !crowdData) return null;

  // Derive all available coach class options for the current train
  const allOptions = useMemo(() => {
    if (crowdData?.class_breakdown && crowdData.class_breakdown.length > 0) {
      return crowdData.class_breakdown.map((cls) => {
        const pct = cls.average_occupancy_percent ?? (cls.average_occupancy_ratio ? cls.average_occupancy_ratio * 100 : 0);
        return {
          coach_class: cls.coach_class,
          class_display_name: CLASS_DISPLAY_NAMES[cls.coach_class] || `Class ${cls.coach_class}`,
          occupancy_ratio: cls.average_occupancy_ratio ?? (pct / 100),
          occupancy_percent: pct,
          crowd_level: cls.crowd_level || 'UNKNOWN',
          total_passengers: cls.total_passengers ?? 0,
          total_capacity: cls.total_capacity ?? 0
        };
      });
    }

    if (recData?.ranked_options && recData.ranked_options.length > 0) {
      return recData.ranked_options.map((opt) => ({
        ...opt,
        class_display_name: opt.class_display_name || CLASS_DISPLAY_NAMES[opt.coach_class] || `Class ${opt.coach_class}`
      }));
    }

    return [];
  }, [crowdData, recData]);

  // Filter options based on activeFilter: ALL, AC (1A, 2A, 3A, 3E, CC, EC), NON_AC (SL, 2S, GEN, GS)
  const filteredOptions = useMemo(() => {
    let list = [...allOptions];
    if (activeFilter === 'AC') {
      list = list.filter((opt) => AC_CLASSES.includes(opt.coach_class));
    } else if (activeFilter === 'NON_AC' || activeFilter === 'NON-AC' || activeFilter === 'BUDGET') {
      list = list.filter((opt) => NON_AC_CLASSES.includes(opt.coach_class));
    }
    return list.sort((a, b) => a.occupancy_percent - b.occupancy_percent);
  }, [allOptions, activeFilter]);

  const hasMatches = filteredOptions.length > 0;
  const bestOption = hasMatches ? filteredOptions[0] : null;
  const recClass = bestOption ? bestOption.coach_class : null;

  // Identify lowest-occupancy coach ID for recommended class
  const recCoachId = useMemo(() => {
    if (!bestOption) return null;
    if (crowdData?.coach_details && crowdData.coach_details.length > 0) {
      const matching = crowdData.coach_details
        .filter((c) => c.coach_class === bestOption.coach_class)
        .sort((a, b) => (a.occupancy_ratio ?? 0) - (b.occupancy_ratio ?? 0));
      if (matching.length > 0) {
        return matching[0].coach_id;
      }
    }
    if (recData?.recommended_coach_or_class === bestOption.coach_class && recData.recommended_coach_id) {
      return recData.recommended_coach_id;
    }
    return `${bestOption.coach_class}1`;
  }, [bestOption, crowdData, recData]);

  const recClassName = bestOption
    ? (bestOption.class_display_name || CLASS_DISPLAY_NAMES[bestOption.coach_class] || `Class ${bestOption.coach_class}`)
    : 'No Matching Classes';

  const occupancyPct = bestOption ? bestOption.occupancy_percent : 0.0;
  const crowdLevel = bestOption ? bestOption.crowd_level : 'N/A';

  // Dynamic domain reasoning text
  const reason = useMemo(() => {
    if (!hasMatches) {
      const filterLabel = activeFilter === 'AC' ? 'AC (1A, 2A, 3A, 3E, CC, EC)' : (activeFilter === 'NON_AC' ? 'NON-AC / BUDGET (SL, 2S, GEN, GS)' : 'selected');
      return `No ${filterLabel} coach classes are configured on this train route. Please switch filter to view available compartments.`;
    }

    let text = `Class ${bestOption.coach_class} (${bestOption.class_display_name}) has the lowest estimated occupancy at ${bestOption.occupancy_percent.toFixed(1)}% (${bestOption.crowd_level} crowd density).`;
    
    if (filteredOptions.length > 1) {
      const worstOption = filteredOptions[filteredOptions.length - 1];
      const diffPct = (worstOption.occupancy_percent - bestOption.occupancy_percent).toFixed(1);
      if (Number(diffPct) > 10.0) {
        text += ` Saves ~${diffPct}% congestion compared to ${worstOption.coach_class} (${worstOption.occupancy_percent.toFixed(1)}% - ${worstOption.crowd_level}).`;
      }
    }
    return text;
  }, [hasMatches, bestOption, filteredOptions, activeFilter]);

  const badgeColor = useMemo(() => {
    if (!hasMatches) return 'orange';
    if (crowdLevel === 'LOW') return 'green';
    if (crowdLevel === 'MEDIUM') return 'orange';
    return 'red';
  }, [hasMatches, crowdLevel]);

  return (
    <div className="card recommendation-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
          Less crowded coach
        </h3>
        <span className="badge-status green">
          RECOMMENDED
        </span>
      </div>

      {/* Budget Filter Toggle */}
      <div className="budget-filter-group">
        {['ALL', 'AC', 'NON_AC'].map((filter) => (
          <button
            key={filter}
            className={`btn-filter ${activeFilter === filter ? 'active' : ''}`}
            onClick={() => onFilterChange && onFilterChange(filter)}
            type="button"
          >
            {filter === 'NON_AC' ? 'NON-AC / BUDGET' : filter}
          </button>
        ))}
      </div>

      {/* Recommended Winner Banner */}
      <div className="recommendation-banner">
        <div className="recommendation-header">
          <div>
            <div className="recommendation-class">
              {hasMatches ? (
                <>
                  {recClass} <span style={{ fontSize: '1rem', color: 'var(--brand-red)', fontWeight: '600' }}>({recCoachId})</span>
                </>
              ) : (
                <span style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>No Matching Coaches</span>
              )}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{recClassName}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className={`badge-status ${badgeColor}`} style={{ fontSize: '0.8rem' }}>
              {hasMatches ? `${crowdLevel} (${occupancyPct.toFixed(1)}%)` : 'UNAVAILABLE'}
            </span>
          </div>
        </div>

        <p className="recommendation-reason">
          {reason}
        </p>
      </div>

      {/* Ranked Alternatives Table */}
      {filteredOptions.length > 1 && (
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
            Available Class Congestion Comparison:
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {filteredOptions.map((opt) => {
              const isRecommended = opt.coach_class === bestOption?.coach_class;
              return (
                <div
                  key={opt.coach_class}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: isRecommended ? 'rgba(225, 29, 72, 0.1)' : 'var(--bg-surface-elevated)',
                    border: isRecommended ? '1px solid rgba(225, 29, 72, 0.3)' : '1px solid var(--border-subtle)',
                    padding: '0.4rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem'
                  }}
                >
                  <div>
                    <strong>{opt.coach_class}</strong>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
                      ({opt.class_display_name})
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                    <span>{opt.occupancy_percent.toFixed(1)}%</span>
                    <span style={{
                      fontSize: '0.68rem',
                      color: opt.crowd_level === 'LOW' ? 'var(--accent-emerald)' : (opt.crowd_level === 'MEDIUM' ? 'var(--accent-amber)' : 'var(--brand-red)')
                    }}>
                      {opt.crowd_level}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
