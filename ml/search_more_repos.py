import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

repos = [
    'areenakhan07/Indian_Railways',
    'shwetankg07/railpull',
    'DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning',
    'jsroa15/Train-delay-prediction',
    'naijilaji/indian-railways-train-delays-dataset-2025'
]

for repo in repos:
    print(f"\n=== Checking Repo: {repo} ===")
    url = f"https://api.github.com/repos/{repo}/contents"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list):
                for item in data:
                    print(f"[{item.get('type')}] {item.get('name')} ({item.get('size')} bytes)")
                    if item.get('type') == 'file' and item.get('name').endswith('.csv'):
                        print(f"   -> CSV Download: {item.get('download_url')}")
            else:
                print(data)
    except Exception as e:
        print(f"Status for {repo}: {e}")
