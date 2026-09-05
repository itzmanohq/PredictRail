# PredictRail 🚆 — Jury Demo Script & Presentation Flow
**College Hackathon Presentation Guide (3–5 Minutes)**

---

## 🕒 Demonstration Overview & Timeline

| Time | Section | Key Focus / Action |
| :--- | :--- | :--- |
| **0:00 – 0:30** | 1. Problem Introduction | The Indian Railways punctuality & passenger uncertainty challenge |
| **0:30 – 1:00** | 2. Dashboard & Train Selection | Select Train 12423 (Dibrugarh Rajdhani), Station GHY, Delay 30 min |
| **1:00 – 1:45** | 3. ML Prediction & Dynamic ETA | Explain gradient boosting prediction & calendar-aware destination ETA |
| **1:45 – 2:30** | 4. Graph Bottlenecks & Weather Risk | Show junction congestion modeling & Open-Meteo live weather layer |
| **2:30 – 3:30** | 5. Crowd Density & Smart Class Advisory | Explain synthetic coach distribution & class recommendation |
| **3:30 – 4:00** | 6. Core Innovation & Conclusion | Unified multi-layer decision intelligence & prototype honesty |

---

## 🎙️ Step-by-Step Jury Script

### Step 1: Introduce the Problem (0:00 – 0:30)
> *"Respected jury members, Indian Railways is the lifeline of the nation, transporting over 23 million passengers daily across 8,000+ stations. However, when a train gets delayed, passengers face major uncertainty: Will the delay recover down the line? When will I reach my final destination across multi-day journeys? Which upcoming junction will cause further compounding delays? And which coach is least congested?*
> 
> *Standard railway apps only tell you what has ALREADY happened. **PredictRail** is an intelligent decision-support system that predicts what will happen next by combining local Machine Learning, NetworkX railway graph topology, live meteorological risk, and passenger density modeling."*

---

### Step 2: Select Train & Observation Scenario (0:30 – 1:00)
> *(Action: In the Dashboard search box, type `12423` or select Dibrugarh Rajdhani Express from the dropdown. Select `Guwahati (GHY)` as the current station, and enter `30` minutes current observed delay.)*
> 
> *"Let's take a real-world scenario: Train **12423 Dibrugarh–New Delhi Rajdhani Express**, currently departing **Guwahati (GHY)** with an observed delay of **30 minutes**. We click **ANALYZE TRAIN**."*

---

### Step 3: Explain the ML Delay Prediction (1:00 – 1:30)
> *(Action: Point to the ML Delay Forecast Card)*
> 
> *"Within milliseconds, our locally-trained **HistGradientBoostingRegressor** ML model evaluates historical delay momentum, route distance, scheduled halt slack, and time of day. It predicts that at the next critical junction, the train will experience a delay of **~53.7 minutes**—accounting for the fact that delays on this corridor historically compound during morning transit."*

---

### Step 4: Explain Dynamic Multi-Day ETA (1:30 – 2:00)
> *(Action: Point to the Dynamic ETA Card and Route Progression panel)*
> 
> *"Rather than a naive flat addition, our **Dynamic ETA Engine** calculates station-by-station arrival progression all the way to **New Delhi (NDLS)**. It accounts for midnight day rollovers across 3 calendar days, showing a scheduled arrival of `10:20 AM (Day 3)` shifting to a dynamic ETA of `11:29 AM (Day 3)` with +69 minutes total destination delay."*

---

### Step 5: Show Network Graph Bottlenecks & Propagation (2:00 – 2:30)
> *(Action: Scroll down to the Route Timeline and show the JUNCTION BOTTLENECK badges)*
> 
> *"Under the hood, PredictRail models the entire Indian Railways network as a directed graph of **8,151 stations and 28,194 track segments**. The route timeline highlights major junction bottlenecks like `KIR (Katihar)`, `PNBE (Patna)`, and `DDU (Pt. Deen Dayal Upadhyaya Junction)`, calculating topological slack absorption and junction congestion factors."*

---

### Step 6: Show Real-Time Weather Risk Layering (2:30 – 3:00)
> *(Action: Point to the Station Meteorological Risk Card)*
> 
> *"Next is our **Weather Risk Layer**. Using the 100% free, keyless **Open-Meteo API**, PredictRail fetches live temperature, humidity, precipitation, wind speed, and track visibility for Guwahati. It computes a 0–100 meteorological risk score and isolates weather impact as a separate safety buffer (+0.0 min for Clear weather, up to +35 min for Heavy Fog) without corrupting the core ML model."*

---

### Step 7: Show Prototype Crowd Estimation & Smart Compartment Recommendation (3:00 – 3:30)
> *(Action: Point to the Crowd Card and Recommendation Card. Click the 'AC' and 'NON-AC / BUDGET' filter buttons)*
> 
> *"For passenger comfort, we provide **Prototype Crowd Estimation** and a **Smart Compartment Recommendation**. 
> - The Crowd Card displays simulated coach-by-coach occupancy (e.g., 60.5% overall train load).
> - The Recommendation engine automatically recommends the least crowded coach class—in this case, coach **A1 (AC 2-Tier)**.
> - When a budget passenger toggles **'NON-AC / BUDGET'**, the system dynamically recalculates and recommends coach **S3 (Sleeper)** with transparent domain reasoning."*

---

### Step 8: Data Honesty & Key Innovation Summary (3:30 – 4:00)
> *"A crucial point of engineering honesty: **Our crowd estimation is synthetic prototype data**, modeled to demonstrate how real coach sensors or PNR statistics will integrate in production. We do not claim fake live camera feeds or guaranteed predictions.
> 
> The core innovation of PredictRail is **multi-layer situational awareness**: merging historical tabular ML, network graph topology, live meteorological APIs, and coach occupancy into a unified, high-performance dashboard.
> 
> Thank you! We are now open for technical questions from the jury."*

---

## 💡 Quick Tips for the Presenter
- Keep the FastAPI backend running on port 8000 and Vite frontend on port 5173 before presenting.
- When clicking filter buttons (ALL, AC, NON-AC), highlight the instant reactivity.
- Emphasize that all ML inference and graph calculations run locally without paid cloud services or paid APIs.
