import urllib.request

def check_csv_sample(url, name):
    print(f"\n=== Sample from {name} ===")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read(4096).decode('utf-8', errors='ignore')
            lines = content.strip().split('\n')
            for i, line in enumerate(lines[:10]):
                print(f"[{i}] {line}")
    except Exception as e:
        print(f"Error reading {name}: {e}")

check_csv_sample('https://raw.githubusercontent.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning/master/train_delays.csv', 'DeekshithRajBasa train_delays.csv')
check_csv_sample('https://raw.githubusercontent.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning/master/trains.csv', 'DeekshithRajBasa trains.csv')
check_csv_sample('https://raw.githubusercontent.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning/master/stations.csv', 'DeekshithRajBasa stations.csv')
