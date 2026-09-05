# PredictRail Frontend Dashboard Report

## 1. Executive Summary & Architecture Overview

The **PredictRail Frontend Dashboard** (`frontend/`) is a modern web application built using **React 18** and **Vite**, styled with a custom high-contrast dark theme inspired by Indian Railways operations and railway control systems.

It provides real-time train delay forecasting, dynamic multi-stop ETA computation, railway junction bottleneck visualization, Open-Meteo meteorological risk assessment, and prototype crowd estimation with smart compartment recommendations.

```mermaid
graph TD
    User[Railway Passenger / Hackathon Jury] --> UI[PredictRail Dashboard - React 18 + Vite]
    UI --> TrainSelector[Train Search & Station Selector]
    UI --> DelayCard[AI ML Delay Forecast Card]
    UI --> EtaCard[Dynamic Destination ETA Card]
    UI --> WeatherCard[Station Weather & Risk Card]
    UI --> CrowdCard[Prototype Crowd Density Card]
    UI --> RecCard[Smart Compartment Recommender]
    UI --> RoutePanel[Delay Propagation & Bottleneck Timeline]
    UI --> SystemStatus[Live System Status Poller]
    
    UI -->|HTTP / JSON (REST API)| Backend[FastAPI Gateway - http://localhost:8000]
```

---

## 2. Component Architecture & Hierarchy

| Component | File Path | Responsibilities & Capabilities |
|---|---|---|
| **App Shell** | `src/App.jsx` | Coordinates state, asynchronous polling, budget filtering, and master `/predict` payload orchestration. |
| **Header** | `src/components/Header.jsx` | Brand identity banner, subtitle, and live system status bar. |
| **System Status** | `src/components/SystemStatus.jsx` | Real-time health polling (`GET /health`) monitoring ML Model, Graph, ETA, Weather, Crowd, and API Gateway connectivity. |
| **Train Selector** | `src/components/TrainSelector.jsx` | Auto-completing train search (`GET /trains`), dynamic stop dropdown (`GET /trains/{train_number}`), observed delay input, and `ANALYZE TRAIN` trigger. |
| **Delay Card** | `src/components/DelayCard.jsx` | Displays AI predicted delay in minutes, color-coded severity badges (On Time, Minor, Moderate, Severe), and model metadata. |
| **Dynamic ETA Card** | `src/components/EtaCard.jsx` | Displays destination dynamic arrival ETA with midnight rollover annotations, scheduled vs predicted times, and separate weather buffer. |
| **Weather Card** | `src/components/WeatherCard.jsx` | Station weather metrics (temp, humidity, rain, wind, visibility), WMO category badge, risk score (0–100), and offline fallback alert. |
| **Crowd Card** | `src/components/CrowdCard.jsx` | Prominently tagged with `SYNTHETIC PROTOTYPE DATA`, displaying overall train load %, estimated pax vs capacity, and coach class breakdown bars. |
| **Recommendation Card**| `src/components/RecommendationCard.jsx` | Recommends the least-crowded travel class & coach ID, domain justification, budget filters (`ALL`, `AC`, `NON-AC`), and ranked alternatives table. |
| **Route Panel** | `src/components/RoutePanel.jsx` | Schematic itinerary timeline displaying station codes, names, dynamic ETAs, delay accumulation, and highlighted bottleneck junctions. |

---

## 3. UI Theme & Visual Design Tokens

- **Color Palette:**
  - Background: Cyber-slate dark `#070a12` with subtle radial lighting
  - Surfaces: `#0e1626` / `#152035` with glassmorphic border accents
  - Accent Primary: Indian Railways Crimson Red (`#e11d48` / `#ef4444`)
  - Status Indicators: Emerald `#10b981` (On Time / Low Risk), Amber `#f59e0b` (Moderate / Bottlenecks), Crimson `#e11d48` (Severe / High Density)
- **Typography:**
  - Display: *Outfit* (headings, badges, primary brand title)
  - Body: *Inter* (data labels, descriptions, cards)
  - Monospace: *JetBrains Mono* (train numbers, station codes, timestamps, delays)
- **Responsive Layout:** 12-column grid layout adapting seamlessly across laptop screens (1366x768), desktop displays (1920x1080), and mobile viewports.

---

## 4. API Integration & Error Resilience

All UI components communicate exclusively with the FastAPI backend at `http://localhost:8000`:
- `GET /health` — Verifies live server connectivity every 15 seconds.
- `GET /trains` — Powers real-time search autocomplete.
- `GET /trains/{train_number}` — Fetches route stops on train selection.
- `POST /predict` — Executes unified master intelligence analysis.
- `POST /recommend-compartment` — Dynamically switches budget filter (`ALL`, `AC`, `NON-AC`) without re-running the entire itinerary analysis.

### Fault Tolerance & Edge Cases
- **Loading Overlay:** Clean animated spinner prevents UI freezes during intensive graph propagation.
- **Empty / Error States:** Invalid train numbers or network connection losses display clear error banners without exposing unformatted JSON or `undefined`/`NaN` text.
- **Offline Weather Indicator:** If Open-Meteo is unreachable, an amber notice informs the user that safety fallback values ($0.0$m buffer) are in effect.

---

## 5. Quickstart & Build Instructions

### Development Server
```bash
# In PredictRail root:
cd frontend
npm run dev
```
The dashboard will start on `http://localhost:5173`.

### Production Build
```bash
cd frontend
npm run build
```
Generates a static bundle inside `frontend/dist/`.

---

## 6. Limitations & Academic Disclaimers

1. **Synthetic Crowd Estimation:** Passenger counts and coach occupancies are synthetic prototype estimates modeled from empirical Indian Railways rake configurations. They are clearly labeled as `SYNTHETIC PROTOTYPE DATA` throughout the interface.
2. **Keyless Open-Meteo Weather:** Weather data queries Open-Meteo's free public forecast API. Cached locally for 30 minutes to respect public rate limits.
