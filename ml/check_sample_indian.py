import urllib.request

url = "https://raw.githubusercontent.com/areenakhan07/Indian_Railways/main/Indian_railway1.csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    # Read first 4KB
    chunk = resp.read(4096).decode('utf-8', errors='ignore')
    lines = chunk.split('\n')
    print(f"Total sample lines received: {len(lines)}")
    for i, line in enumerate(lines[:10]):
        print(f"[{i}] {line}")
