import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from graph.delay_propagation import simulate_delay_propagation

def display_propagation_tree(train_no, current_station, delay_min, sample_steps=7):
    res = simulate_delay_propagation(train_no, current_station, delay_min)
    print(f"\n{'='*75}")
    print(f" [TRAIN] DELAY PROPAGATION TRAJECTORY: {res['train_name']} (Train #{res['train_number']})")
    print(f"{'='*75}")
    print(f"Origin Observed: [{res['observation_station']}] with Delay = {res['initial_delay_min']} minutes")
    print(f"Destination:     [{res['destination_station']}] {res['destination_station_name']}")
    print(f"Route Stops:     {res['total_downstream_stops']} downstream stops | Bottlenecks: {res['bottleneck_junctions_encountered']}")
    print("-" * 75)
    
    traj = res['trajectory']
    total_stops = len(traj)
    
    if total_stops <= sample_steps:
        display_indices = list(range(total_stops))
    else:
        display_indices = list(range(min(4, total_stops))) + [total_stops//2] + [total_stops-1]
        display_indices = sorted(list(set(display_indices)))

    for i, idx in enumerate(display_indices):
        step = traj[idx]
        seq = step['sequence']
        stn = step['station_code']
        name = step['station_name']
        d_est = step['estimated_delay_min']
        d_delta = step['delay_delta_min']
        is_bot = step['is_bottleneck']
        bot_lvl = step['congestion_level']
        
        if i == 0:
            print(f"Train #{train_no} -> Current Station: [{stn}] {name} -> Current Delay: {d_est:.1f}m")
        else:
            bot_tag = f" [BOTTLENECK: {bot_lvl} (Score: {step['bottleneck_score']})]" if is_bot else ""
            delta_str = f"({d_delta:+.1f}m)" if d_delta != 0 else "(+0.0m)"
            print("  |")
            print("  v")
            print(f"Next Station (Seq {seq:02d}): [{stn}] {name:<22} -> Est Propagated Delay: {d_est:>5.1f}m {delta_str}{bot_tag}")

def run_demonstration():
    print("=== PREDICTRAIL INDIAN RAILWAYS DELAY PROPAGATION DEMO ===")
    
    # Route 1: Train 13009 (Doon Express) starting at Howrah with 45m delay
    display_propagation_tree("13009", "HWH", 45.0)
    
    # Route 2: Train 12423 (Dibrugarh - New Delhi Rajdhani) starting at Guwahati with 60m delay
    display_propagation_tree("12423", "GHY", 60.0)

    # Route 3: Train 12345 (Saraighat Express) starting at Howrah with 20m delay
    display_propagation_tree("12345", "HWH", 20.0)

if __name__ == "__main__":
    run_demonstration()
