# PredictRail Dynamic ETA Engine Technical Report

**Document Version:** 1.0.0  
**Project:** PredictRail (Dynamic Arrival ETA Architecture)  
**Module:** [eta/dynamic_eta.py](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/eta/dynamic_eta.py)  
**Calculator:** [eta/eta_calculator.py](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/eta/eta_calculator.py)  
**Test Suite:** [tests/test_eta.py](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/tests/test_eta.py) (10/10 tests passing)  

---

## 1. Overview & Operational Problem

Static railway timetables display planned scheduled arrival times ($T_{\text{sched}}$) that quickly become invalid when upstream disruptions, signal holds, or junction queues occur. The **PredictRail Dynamic ETA Engine** computes real-time expected arrival timestamps ($\text{ETA}$) for all remaining downstream stations along an active train route by unifying:

1. **Static Scheduled Timetable Timestamps** ($T_{\text{sched}}$) from official Indian Railways data.
2. **Physical Upstream Delay Momentum & Slack Recovery** ($D_{\text{prop}}$) computed via NetworkX topology.
3. **Machine Learning Statistical Corridor Risk** ($D_{\text{ML}}$) evaluated by PredictRail's custom-trained `HistGradientBoosting` model.
4. **Calendar Day & Midnight Rollover Management** for multi-day Indian Railways intercity corridors.

---

## 2. Mathematical Formulation & Architecture

```
[ Train Number + Current Station + Observed Delay (D0) ]
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Physical Propagation Engine ]   [ ML Model Expected Risk ]
• NetworkX Junction Friction      • Station Sequence & Distance
• Timetable Dwell Recovery        • Corridor Density & Train Type
• Bottleneck Congestion Factor    • Diurnal Departure Window
       │                               │
       └───────────────┬───────────────┘
                       ▼
         [ Adaptive Distance Blending ]
         D_hat_i = alpha_i * D_prop + (1 - alpha_i) * D_ml
                       │
                       ▼
        [ Timestamp & Midnight Calculator ]
      ETA_i = Sched_Timestamp_i + D_hat_i
```

### Dynamic Delay Blending ($\hat{D}_i$):
For every upcoming station stop $i$ located $k = i - i_{\text{current}}$ hops ahead:
$$\hat{D}_i = \alpha_k \cdot D_{\text{prop}, i} + (1 - \alpha_k) \cdot D_{\text{ML}, i}$$

Where:
- $\alpha_k = \max(0.60,\ 0.90 - 0.02 \times k)$: Smoothly transitions from **$90\%$ physical momentum** for immediate near-term stops ($1-3$ hops ahead) to **$60\%$ physical / $40\%$ statistical corridor expectation** for distant stations hundreds of kilometers down the track.

### Timestamp Addition & Day Tracking:
- Total scheduled minutes from journey origin:
  $$M_{\text{sched, total}} = (d_{\text{sched}} - 1) \times 1440.0 + M_{\text{sched}}$$
- Total dynamic arrival minute:
  $$M_{\text{eta, total}} = M_{\text{sched, total}} + \hat{D}_i$$
- Arrival day index and time:
  $$d_{\text{eta}} = \left\lfloor \frac{M_{\text{eta, total}}}{1440.0} \right\rfloor + 1, \quad m_{\text{day}} = M_{\text{eta, total}} \pmod{1440.0}$$
  $$H_{\text{eta}} = \left\lfloor \frac{m_{\text{day}}}{60} \right\rfloor, \quad M_{\text{eta}} = \lfloor m_{\text{day}} \pmod{60} \rfloor$$

---

## 3. Midnight & Multi-Day Rollover Handling

Indian Railways trains frequently operate across multiple calendar days (e.g. 24–48 hour long-haul routes). The engine handles three distinct rollover scenarios:

1. **Scheduled Timetable Rollover:**  
   When a train's scheduled arrival drops backwards (e.g. from `23:47:00` at Raniganj to `00:06:00` at Asansol), the scheduled day index increments from **Day 1 to Day 2**.
2. **Delay-Induced Midnight Crossing:**  
   When a train scheduled on Day 1 at `23:27:00` incurs a $41.8\text{ min}$ delay, the dynamic arrival pushes past midnight to `00:08:48 (+1 Day / Day 2)`.
3. **Multi-Day Compounded Delay:**  
   For a Day 2 night stop scheduled at `21:23:00` with $162.9\text{ min}$ delay, arrival pushes into Day 3 (`00:05:54 (+1 Day / Day 3)`).

---

## 4. Anti-Leakage Compliance

> [!IMPORTANT]
> **Strict Forward-Only Inference:**  
> - Future actual historical delays from the database are **never** queried or accessed during ETA generation.  
> - Only the current station's observed delay ($D_0$) and static timetable schedules are passed into the engine.

---

## 5. Real Indian Railways Examples

### Example 1: Train 13009 (Doon Express) from Howrah (HWH) with 45m initial delay (Crosses Midnight)
- **Origin Observed:** `HWH` (Howrah Jn) at `20:25:00 (Day 1)` with `45.0m` delay.
- **Durgapur (`DGR`):** Scheduled `23:27:00 (Day 1)` $\to$ **Dynamic ETA: `00:08:48 (+1 Day / Day 2)`** *(Midnight crossed due to delay)*.
- **Asansol (`ASN`):** Scheduled `00:06:00 (Day 2)` $\to$ **Dynamic ETA: `00:47:24 (Day 2)`**.
- **Final Terminus (`DDN` Dehra Dun):** Scheduled `07:35:00 (Day 3)` $\to$ **Dynamic ETA: `10:18:12 (Day 3)`** *(Predicted delay: `163.2m`)*.

### Example 2: Train 12423 (Dibrugarh-New Delhi Rajdhani) from Guwahati (GHY) with 30m delay
- **Origin Observed:** `GHY` (Guwahati) at `06:30:00 (Day 1)` with `30.0m` delay.
- **New Bongaigaon (`NBQ`):** Scheduled `09:18:00 (Day 1)` $\to$ **Dynamic ETA: `09:48:30 (Day 1)`**.
- **New Delhi (`NDLS`):** Scheduled `10:30:00 (Day 2)` $\to$ **Dynamic ETA: `11:06:30 (Day 2)`** *(Predicted delay: `36.5m`)*.

---

## 6. Assumptions & Limitations

1. **Locomotive Acceleration Curves:** Delay absorption assumes standard locomotive operational slack without emergency single-line speed restrictions.
2. **Punctuality Threshold:** Follows Indian Railways standard: $\le 15\text{ min}$ is categorized as **On-Time**, $15-60\text{ min}$ as **Moderate Delay**, and $>60\text{ min}$ as **Severe Delay**.
