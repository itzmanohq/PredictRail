import urllib.request
import io

headers = {'User-Agent': 'Mozilla/5.0'}

def print_csv_sample(url, name):
    print(f"\n=== Sample from {name} ===")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            lines = content.strip().split('\n')
            for i, line in enumerate(lines[:10]):
                print(f"{i}: {line}")
            print(f"Total lines: {len(lines)}")
    except Exception as e:
        print(f"Error fetching {name}: {e}")

print_csv_sample('https://raw.githubusercontent.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets/main/Dataset/Train_List.csv', 'Train_List.csv')
print_csv_sample('https://raw.githubusercontent.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets/main/Dataset/Train_Route/02501.csv', '02501.csv')
print_csv_sample('https://raw.githubusercontent.com/hanna-sliash/UK-Train-Delay-Data-Analysis/main/railway.csv', 'UK railway.csv')
