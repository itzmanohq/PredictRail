import os
import json
import joblib
import pandas as pd
import numpy as np
import networkx as nx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
GRAPH_DIR = os.path.join(BASE_DIR, "graph")
os.makedirs(GRAPH_DIR, exist_ok=True)

GRAPH_SAVE_PATH = os.path.join(GRAPH_DIR, "railway_network_graph.joblib")
BOTTLENECKS_SAVE_PATH = os.path.join(GRAPH_DIR, "bottlenecks.json")

def build_railway_graph():
    print("=" * 75)
    print(" BUILDING INDIAN RAILWAYS NETWORK TOPOLOGY GRAPH")
    print("=" * 75)

    sched_file = os.path.join(RAW_DIR, "indian_railway_schedules.csv")
    stations_file = os.path.join(RAW_DIR, "stations.json")

    if not os.path.exists(sched_file):
        raise FileNotFoundError(f"Missing {sched_file}")

    # 1. Load Station GeoJSON Metadata
    station_geo = {}
    if os.path.exists(stations_file):
        print(f"Loading station geographical coordinates from {stations_file}...")
        with open(stations_file, 'r', encoding='utf-8') as f:
            stn_data = json.load(f)
            for feat in stn_data.get('features', []):
                props = feat.get('properties', {})
                geom = feat.get('geometry', {})
                code = props.get('code', '').strip().upper()
                if code:
                    coords = geom.get('coordinates', [None, None]) if isinstance(geom, dict) else [None, None]
                    station_geo[code] = {
                        "name": props.get('name', ''),
                        "zone": props.get('zone', ''),
                        "state": props.get('state', ''),
                        "lon": coords[0] if coords and len(coords) > 0 else None,
                        "lat": coords[1] if coords and len(coords) > 1 else None
                    }
        print(f"Loaded geographical attributes for {len(station_geo):,} stations.")

    # 2. Load and Clean Schedule Data
    print(f"Loading Indian Railways timetable schedules from {sched_file}...")
    df_sched = pd.read_csv(sched_file, low_memory=False)
    
    df_sched['Train_No'] = df_sched['Train No'].astype(str).str.strip().str.lstrip('0')
    df_sched['Station_Code'] = df_sched['Station Code'].astype(str).str.strip().str.upper()
    df_sched['Station_Name'] = df_sched['Station Name'].astype(str).str.strip()
    df_sched['SEQ'] = pd.to_numeric(df_sched['SEQ'], errors='coerce').fillna(1).astype(int)
    df_sched['Distance'] = pd.to_numeric(df_sched['Distance'], errors='coerce').fillna(0.0).astype(float)
    
    # Sort strictly by Train and Sequence
    df_sched = df_sched.sort_values(by=['Train_No', 'SEQ']).reset_index(drop=True)

    # 3. Construct NetworkX Graph
    G = nx.DiGraph()
    print("Instantiating directed railway network graph (Nodes = Stations, Edges = Consecutive Track Segments)...")

    # Add Nodes
    station_train_map = df_sched.groupby('Station_Code')['Train_No'].nunique().to_dict()
    station_names_map = df_sched.groupby('Station_Code')['Station_Name'].first().to_dict()

    for stn_code, t_count in station_train_map.items():
        geo_info = station_geo.get(stn_code, {})
        G.add_node(
            stn_code,
            station_code=stn_code,
            name=geo_info.get("name") or station_names_map.get(stn_code, stn_code),
            train_count=t_count,
            zone=geo_info.get("zone", "UNKNOWN"),
            state=geo_info.get("state", "UNKNOWN"),
            lat=geo_info.get("lat"),
            lon=geo_info.get("lon")
        )

    # Add Edges (consecutive stops in train routes)
    grouped = df_sched.groupby('Train_No')
    edge_train_tracker = {}

    for t_no, route_df in grouped:
        stns = route_df['Station_Code'].tolist()
        dists = route_df['Distance'].tolist()
        
        for i in range(len(stns) - 1):
            u, v = stns[i], stns[i+1]
            if u == v:
                continue
            seg_dist = max(1.0, dists[i+1] - dists[i])
            
            edge_key = (u, v)
            if edge_key not in edge_train_tracker:
                edge_train_tracker[edge_key] = {
                    "trains": set(),
                    "distances": []
                }
            edge_train_tracker[edge_key]["trains"].add(t_no)
            edge_train_tracker[edge_key]["distances"].append(seg_dist)

    for (u, v), info in edge_train_tracker.items():
        avg_dist = float(np.mean(info["distances"]))
        G.add_edge(
            u, v,
            train_count=len(info["trains"]),
            avg_distance_km=round(avg_dist, 1),
            trains=list(info["trains"])[:50]  # Store sample trains
        )

    print(f"\n--- Railway Graph Construction Summary ---")
    print(f"Total Station Nodes: {G.number_of_nodes():,}")
    print(f"Total Track Edges (Directed): {G.number_of_edges():,}")
    print(f"Graph Density: {nx.density(G):.6f}")

    # 4. Bottleneck Detection & Centrality Analysis
    print("\nCalculating junction centrality & identifying network bottlenecks...")
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    degree_centrality = nx.degree_centrality(G)

    # Bottleneck Composite Score:
    # Combines Total Trains Passing Through (Throughput Load) + Direct Junction Degree Connections
    # Normalized between 0.0 and 100.0
    max_trains = max(station_train_map.values()) if station_train_map else 1
    max_degree = max([in_degrees[n] + out_degrees[n] for n in G.nodes()]) if G.nodes() else 1

    bottlenecks = []
    for node in G.nodes():
        t_cnt = G.nodes[node].get('train_count', 0)
        tot_deg = in_degrees[node] + out_degrees[node]
        deg_cent = degree_centrality[node]
        
        # Weighted composite score: 60% train traffic volume + 40% physical junction line degree
        score = (0.60 * (t_cnt / max_trains) + 0.40 * (tot_deg / max_degree)) * 100.0
        score = round(float(score), 2)
        
        G.nodes[node]['in_degree'] = in_degrees[node]
        G.nodes[node]['out_degree'] = out_degrees[node]
        G.nodes[node]['total_degree'] = tot_deg
        G.nodes[node]['degree_centrality'] = round(deg_cent, 5)
        G.nodes[node]['bottleneck_score'] = score
        
        if score >= 15.0 or tot_deg >= 8 or t_cnt >= 150:
            bottlenecks.append({
                "station_code": node,
                "station_name": G.nodes[node].get('name', ''),
                "train_count": t_cnt,
                "total_degree": tot_deg,
                "in_degree": in_degrees[node],
                "out_degree": out_degrees[node],
                "bottleneck_score": score,
                "zone": G.nodes[node].get('zone', ''),
                "state": G.nodes[node].get('state', '')
            })

    bottlenecks.sort(key=lambda x: x['bottleneck_score'], reverse=True)
    print(f"Identified {len(bottlenecks)} high-impact railway junction bottlenecks.")

    print("\n--- Top 15 Major Indian Railway Junction Bottlenecks ---")
    print(f"{'Rank':<5} {'Code':<7} {'Station Name':<28} {'Trains':<8} {'Degree':<8} {'Score':<7} {'Zone'}")
    print("-" * 75)
    for i, b in enumerate(bottlenecks[:15], 1):
        print(f"{i:<5} {b['station_code']:<7} {b['station_name'][:26]:<28} {b['train_count']:<8} {b['total_degree']:<8} {b['bottleneck_score']:<7} {b['zone']}")

    # 5. Save Artifacts
    print(f"\nSaving serialized NetworkX graph to: {GRAPH_SAVE_PATH}")
    joblib.dump(G, GRAPH_SAVE_PATH)

    print(f"Saving identified bottlenecks list to: {BOTTLENECKS_SAVE_PATH}")
    with open(BOTTLENECKS_SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(bottlenecks, f, indent=2)

    return G, bottlenecks

if __name__ == "__main__":
    build_railway_graph()
