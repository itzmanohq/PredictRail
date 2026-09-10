import React from 'react';

export default function Sidebar({ activeNav = 'home', onNavChange }) {
  const navItems = [
    {
      id: 'home',
      label: 'Home',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
      )
    },
    {
      id: 'journey',
      label: 'Journey',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
          <line x1="8" y1="2" x2="8" y2="18"></line>
          <line x1="16" y1="6" x2="16" y2="22"></line>
        </svg>
      )
    },
    {
      id: 'insights',
      label: 'Journey Insights',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          <circle cx="12" cy="12" r="10" strokeWidth="2"></circle>
        </svg>
      )
    }
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="16" height="16" x="4" y="3" rx="3"></rect>
            <path d="M4 11h16"></path>
            <path d="M12 3v8"></path>
            <path d="m8 19-2 3"></path>
            <path d="m18 22-2-3"></path>
            <circle cx="8" cy="15" r="1.5" fill="currentColor"></circle>
            <circle cx="16" cy="15" r="1.5" fill="currentColor"></circle>
          </svg>
        </div>
        <div className="sidebar-brand-text">
          <span className="brand-name">PredictRail</span>
          <span className="brand-tag">AI Rail</span>
        </div>
      </div>

      {/* Navigation List - Only 3 Items (Home, Journey, Journey Insights) */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = activeNav === item.id;
          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item-btn ${isActive ? 'active' : ''}`}
              onClick={() => onNavChange && onNavChange(item.id)}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
              {isActive && <span className="nav-active-pill" />}
            </button>
          );
        })}
      </nav>

      {/* Clean Footer Status */}
      <div className="sidebar-footer">
        <div className="network-status-badge">
          <span className="pulse-dot"></span>
          <span>Indian Railways Active</span>
        </div>
      </div>
    </aside>
  );
}
