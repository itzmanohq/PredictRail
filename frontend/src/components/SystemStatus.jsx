import React, { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';

export default function SystemStatus() {
  const [apiOnline, setApiOnline] = useState(false);
  const [version, setVersion] = useState('1.0.0');

  useEffect(() => {
    async function verifyBackend() {
      try {
        const res = await checkHealth();
        if (res && res.status === 'ok') {
          setApiOnline(true);
          setVersion(res.version || '1.0.0');
        } else {
          setApiOnline(false);
        }
      } catch (err) {
        setApiOnline(false);
      }
    }
    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="system-status-bar" title="System Operational Status">
      <div className="status-item">
        <span className="status-dot"></span>
        <span>ML MODEL: READY</span>
      </div>
      <div className="status-item">
        <span className="status-dot"></span>
        <span>GRAPH: 8,151 NODES</span>
      </div>
      <div className="status-item">
        <span className="status-dot"></span>
        <span>ETA: DYNAMIC</span>
      </div>
      <div className="status-item">
        <span className="status-dot"></span>
        <span>WEATHER: OPEN-METEO</span>
      </div>
      <div className="status-item">
        <span className="status-dot warning"></span>
        <span>CROWD: PROTOTYPE</span>
      </div>
      <div className="status-item">
        <span className={`status-dot ${apiOnline ? '' : 'error'}`}></span>
        <span>API: {apiOnline ? `ONLINE (v${version})` : 'OFFLINE'}</span>
      </div>
    </div>
  );
}
