import pytest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from graph.congestion import get_graph, get_bottlenecks, get_station_congestion, get_corridor_congestion
from graph.delay_propagation import simulate_delay_propagation

def test_graph_loading():
    G = get_graph()
    assert G.number_of_nodes() > 8000, "Graph should have over 8,000 station nodes"
    assert G.number_of_edges() > 25000, "Graph should have over 25,000 track edges"
    assert "NDLS" in G.nodes, "New Delhi (NDLS) should be present in graph"
    assert "HWH" in G.nodes, "Howrah (HWH) should be present in graph"
    assert "CSMT" in G.nodes, "CST Mumbai (CSMT) should be present in graph"

def test_bottleneck_detection():
    bottlenecks = get_bottlenecks()
    assert len(bottlenecks) > 500, "Should have identified at least 500 bottleneck junctions"
    top_codes = [b['station_code'] for b in bottlenecks[:20]]
    # Major hubs should be in top bottlenecks
    assert any(c in top_codes for c in ["CSMT", "KYN", "HWH", "CNB", "BZA", "NDLS", "MGS"]), "Top railway hubs must be in bottleneck list"

def test_station_congestion():
    ndls = get_station_congestion("NDLS")
    assert ndls["found"] is True
    assert ndls["train_count"] > 200
    assert ndls["is_major_junction"] is True

    fake = get_station_congestion("ZZZZZ")
    assert fake["found"] is False

def test_delay_propagation():
    # Test on Doon Express (13009)
    res = simulate_delay_propagation("13009", "HWH", 45.0)
    assert res["train_number"] == "13009"
    assert res["observation_station"] == "HWH"
    assert res["initial_delay_min"] == 45.0
    assert len(res["trajectory"]) > 10
    
    # Delay at start should equal initial delay
    assert res["trajectory"][0]["estimated_delay_min"] == 45.0
    
    # All delays must be non-negative
    for stop in res["trajectory"]:
        assert stop["estimated_delay_min"] >= 0.0

def test_corridor_congestion():
    # Check HWH to BWN direct segment
    conn = get_corridor_congestion("HWH", "BWN")
    # Even if direct or multi-hop, returns status
    assert "track_utilization_level" in conn
