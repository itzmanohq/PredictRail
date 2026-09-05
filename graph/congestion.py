import os
import json
import joblib
import networkx as nx
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(BASE_DIR, "graph", "railway_network_graph.joblib")
BOTTLENECKS_PATH = os.path.join(BASE_DIR, "graph", "bottlenecks.json")

_CACHED_GRAPH = None
_CACHED_BOTTLENECKS = None

def get_graph() -> nx.DiGraph:
    """Lazy loader for the serialized NetworkX railway graph."""
    global _CACHED_GRAPH
    if _CACHED_GRAPH is None:
        if not os.path.exists(GRAPH_PATH):
            raise FileNotFoundError(
                f"Graph artifact not found at {GRAPH_PATH}. Please run 'python graph/build_graph.py' first."
            )
        _CACHED_GRAPH = joblib.load(GRAPH_PATH)
    return _CACHED_GRAPH

def get_bottlenecks() -> List[Dict[str, Any]]:
    """Loads the precomputed bottlenecks ranking."""
    global _CACHED_BOTTLENECKS
    if _CACHED_BOTTLENECKS is None:
        if not os.path.exists(BOTTLENECKS_PATH):
            raise FileNotFoundError(f"Bottlenecks file not found at {BOTTLENECKS_PATH}.")
        with open(BOTTLENECKS_PATH, 'r', encoding='utf-8') as f:
            _CACHED_BOTTLENECKS = json.load(f)
    return _CACHED_BOTTLENECKS

def get_station_congestion(station_code: str) -> Dict[str, Any]:
    """
    Retrieves static topology congestion metrics for an Indian Railways station.
    Strictly uses timetable volume and network connectivity (No future delay leakage).
    """
    G = get_graph()
    code = str(station_code).strip().upper()
    
    if code not in G.nodes:
        return {
            "station_code": code,
            "station_name": code,
            "found": False,
            "train_count": 0,
            "total_degree": 0,
            "bottleneck_score": 0.0,
            "congestion_level": "Unknown",
            "is_major_junction": False
        }
        
    node = G.nodes[code]
    b_score = node.get('bottleneck_score', 0.0)
    train_count = node.get('train_count', 0)
    total_deg = node.get('total_degree', 0)
    
    if b_score >= 55.0 or train_count >= 500:
        cong_level = "Severe Congestion Hub"
        is_major = True
    elif b_score >= 35.0 or train_count >= 200 or total_deg >= 25:
        cong_level = "High Congestion Junction"
        is_major = True
    elif b_score >= 15.0 or train_count >= 50 or total_deg >= 8:
        cong_level = "Moderate Junction"
        is_major = True
    else:
        cong_level = "Low Congestion Wayside"
        is_major = False
        
    return {
        "station_code": code,
        "station_name": node.get('name', code),
        "found": True,
        "train_count": train_count,
        "total_degree": total_deg,
        "in_degree": node.get('in_degree', 0),
        "out_degree": node.get('out_degree', 0),
        "bottleneck_score": b_score,
        "congestion_level": cong_level,
        "is_major_junction": is_major,
        "zone": node.get('zone', 'UNKNOWN'),
        "state": node.get('state', 'UNKNOWN')
    }

def get_corridor_congestion(source_code: str, dest_code: str) -> Dict[str, Any]:
    """
    Evaluates direct track segment density between two stations.
    """
    G = get_graph()
    u = str(source_code).strip().upper()
    v = str(dest_code).strip().upper()
    
    if G.has_edge(u, v):
        edge = G[u][v]
        t_count = edge.get('train_count', 1)
        dist = edge.get('avg_distance_km', 0.0)
        
        if t_count >= 50:
            density_status = "Very High Track Utilization"
        elif t_count >= 20:
            density_status = "High Track Utilization"
        elif t_count >= 5:
            density_status = "Moderate Track Utilization"
        else:
            density_status = "Light Track Utilization"
            
        return {
            "source": u,
            "destination": v,
            "direct_connection": True,
            "trains_per_day": t_count,
            "segment_distance_km": dist,
            "track_utilization_level": density_status
        }
    else:
        return {
            "source": u,
            "destination": v,
            "direct_connection": False,
            "trains_per_day": 0,
            "segment_distance_km": None,
            "track_utilization_level": "No Direct Segment"
        }

if __name__ == "__main__":
    print("Testing Station Congestion Lookups...")
    test_stations = ["NDLS", "CNB", "MGS", "HWH", "GHY", "SWV"]
    for s in test_stations:
        info = get_station_congestion(s)
        print(f"[{s}] {info['station_name']} -> Score: {info['bottleneck_score']}, Level: {info['congestion_level']}, Trains: {info['train_count']}")
