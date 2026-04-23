from tools.search import search_web

results = search_web("Nvidia RTX 5090 vs AMD RX 9070 deep learning performance")

for i, r in enumerate(results):
    print(f"\nResult {i+1}: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Preview: {r['content'][:150]}")