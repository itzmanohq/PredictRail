import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

def list_recursive(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list):
                for item in data:
                    print(f"{item.get('type')}: {item.get('path')} ({item.get('size')} bytes)")
                    if item.get('type') == 'dir' and path.count('/') < 2:
                        list_recursive(repo, item.get('path'))
    except Exception as e:
        print(f"Error: {e}")

list_recursive('ankitaanand28/DA323_IndianRailwayTrainDelayDatasets', 'Dataset')
