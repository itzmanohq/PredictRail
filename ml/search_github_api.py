import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Search GitHub repositories with query "Indian Railways" delay
url = "https://api.github.com/search/repositories?q=Indian+Railways+delay+dataset+in:readme+in:description&sort=stars&order=desc"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total Repos Found: {data.get('total_count')}")
        for item in data.get('items', [])[:10]:
            print(f"- {item.get('full_name')} ({item.get('stargazers_count')} stars): {item.get('description')}")
            print(f"  URL: {item.get('html_url')}")
except Exception as e:
    print(f"Error: {e}")
