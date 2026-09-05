# PredictRail Indian Railways Network Topology & Delay Propagation Report

**Document Version:** 1.0.0  
**Project:** PredictRail (Railway Graph & Congestion Engine)  
**Graph Artifact:** [graph/railway_network_graph.joblib](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/graph/railway_network_graph.joblib)  
**Bottlenecks Artifact:** [graph/bottlenecks.json](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/graph/bottlenecks.json)  

---

## 1. Graph Construction & Architecture

The Indian Railways network was modeled as a high-density, directed multivariable graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ using **NetworkX**:

- **Nodes ($\mathcal{V}$):** Represent physical railway stations across the Indian subcontinent.
  - Node Attributes: `station_code`, `station_name`, `train_count` (daily train volume), `zone`, `state`, `latitude`, `longitude`, `in_degree`, `out_degree`, `total_degree`, `degree_centrality`, `bottleneck_score`.
- **Edges ($\mathcal{E}$):** Represent direct, consecutive track segments traversed by scheduled Indian trains.
  - Edge Attributes: `train_count` (concurrent train density on the segment), `avg_distance_km` (track length between stops), `trains` (active train IDs).

### Graph Scale Statistics:
- **Total Station Nodes:** **8,151 stations**
- **Total Track Edges:** **28,194 directed segments**
- **Graph Density:** $0.000424$
- **Total Bottleneck Junctions Flagged:** **2,378 stations**

---

## 2. Bottleneck Detection & Centrality Formulation

Railway bottlenecks in the Indian Railways network arise where high passenger train traffic converges with multi-line track junctions. A composite **Bottleneck Score** ($0.0 \le B_i \le 100.0$) was calculated for every station node:

$$B_i = \left( 0.60 \times \frac{T_i}{\max(T)} + 0.40 \times \frac{D_i}{\max(D)} \right) \times 100.0$$

Where:
- $T_i$ = Total distinct scheduled trains passing through station $i$.
- $D_i$ = Total network degree (in-degree + out-degree track connections) at station $i$.
- $\max(T)$ = Maximum train throughput in the network ($1,027$ trains at `CSMT`).
- $\max(D)$ = Maximum junction line connectivity ($79$ connections at `MGS`).

### Top 15 Major Indian Railway Bottlenecks Identified:

| Rank | Station Code | Station Name | Trains Servicing | Junction Degree | Bottleneck Score | Congestion Level |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | `CSMT` | CST-MUMBAI | 1,027 | 26 | **73.16** | Severe Congestion Hub |
| **2** | `KYN` | KALYAN JN | 828 | 44 | **70.65** | Severe Congestion Hub |
| **3** | `HWH` | HOWRAH JN | 699 | 52 | **67.17** | Severe Congestion Hub |
| **4** | `BZA` | VIJAYAWADA JN | 416 | 77 | **63.29** | Severe Congestion Hub |
| **5** | `TNA` | THANE | 796 | 33 | **63.21** | Severe Congestion Hub |
| **6** | `CNB` | KANPUR CENTRAL | 382 | 70 | **57.76** | Severe Congestion Hub |
| **7** | `SDAH` | KOLKATA SEALDAH | 745 | 27 | **57.20** | Severe Congestion Hub |
| **8** | `MGS` | MUGHAL SARAI JN (DDU) | 291 | 79 | **57.00** | Severe Congestion Hub |
| **9** | `MSB` | CHENNAI BEACH | 738 | 22 | **54.26** | High Congestion Junction |
| **10**| `NDLS` | NEW DELHI | 355 | 61 | **51.63** | High Congestion Junction |
| **11**| `SC` | SECUNDERABAD JN | 288 | 66 | **50.24** | High Congestion Junction |
| **12**| `LKO` | LUCKNOW | 295 | 61 | **48.12** | High Congestion Junction |
| **13**| `KGP` | KHARAGPUR JN | 309 | 59 | **47.93** | High Congestion Junction |
| **14**| `BSB` | VARANASI JN | 230 | 67 | **47.36** | High Congestion Junction |
| **15**| `BRC` | VADODARA JN | 378 | 47 | **45.88** | High Congestion Junction |

---

## 3. Dynamic Delay Propagation Model

When a train experiences an upstream delay, the delay does not simply remain constant—it dynamically propagates downstream subject to two opposing physical forces:

1. **Timetable Slack Recovery ($R_i$):** Long scheduled halts ($h_i$) and conservative inter-station buffer times allow locomotive drivers to recover lost time:
   $$R_i = \min\left(0.20 \times h_i,\ 0.06 \times D_{i-1}\right)$$

2. **Junction Queue Amplification ($A_i$):** When an already-delayed train arrives at a congested junction ($B_i \ge 20$), dispatchers prioritize on-time or premium express trains, causing platform waiting and signal holding:
   $$A_i = \left(\frac{B_i}{100.0}\right) \times 2.2 \times \log_e\left(1.0 + 0.08 \times D_{i-1}\right)$$

3. **Step-by-Step Propagated Delay ($D_i$):**
   $$D_i = \max\left(0.0,\ D_{i-1} - R_i + A_i\right)$$

---

## 4. Anti-Leakage Compliance

> [!IMPORTANT]
> **Strict Forward-Only Propagation:**  
> - Upstream propagation uses only static timetable topology and the **currently observed/predicted initial delay**.
> - Downstream actual delays are **never** queried or passed backward to compute current-station metrics.
> - Station bottleneck scores are strictly based on published timetable schedules and track network connections.

---

## 5. Propagation Demonstration Examples

### Case 1: Train 13009 (Doon Express) departing Howrah with 45.0m initial delay:
```
Train #13009 -> Current Station: [HWH] HOWRAH JN. -> Current Delay: 45.0m
  |
  v
Next Station (Seq 02): [SRP] SHRIRAMPUR     -> Est Propagated Delay: 44.4m (-0.6m) [BOTTLENECK: High Congestion (23.6)]
  |
  v
Next Station (Seq 04): [BDC] BANDEL JN.     -> Est Propagated Delay: 44.3m (+0.2m) [BOTTLENECK: High Congestion (34.7)]
  |
  v
Next Station (Seq 77): [DDN] DEHRA DUN      -> Est Propagated Delay: 16.5m (-0.4m) [Recovers 28.5m over 1,558 km]
```

### Case 2: Train 12423 (Dibrugarh-New Delhi Rajdhani) departing Guwahati with 60.0m delay:
```
Train #12423 -> Current Station: [GHY] GUWAHATI -> Current Delay: 60.0m
  |
  v
Next Station (Seq 09): [NBQ] NEW BONGAIGAON -> Est Propagated Delay: 60.7m (+0.7m) [BOTTLENECK: High Congestion (27.3)]
  |
  v
Next Station (Seq 11): [NCB] NEW COOCH BEHAR-> Est Propagated Delay: 60.8m (+0.6m) [BOTTLENECK: High Congestion (24.9)]
  |
  v
Next Station (Seq 22): [NDLS] NEW DELHI     -> Est Propagated Delay: 56.8m (+1.5m) [BOTTLENECK: Severe Hub (51.6)]
```

---

## 6. Assumptions & Limitations

1. **Static Timetable Schedule:** Track edges are derived from scheduled railway operational routes; emergency single-line blocks or ad-hoc train diversions are not captured in static GeoJSON.
2. **Deterministic Slack Modeling:** Propagation assumes standard locomotive acceleration and timetable buffer recovery curves without live telemetry transponders.
