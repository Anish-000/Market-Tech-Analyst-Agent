from tools.scraper import scrape_url

content = scrape_url("https://technical.city/en/video/GeForce-RTX-5090-vs-Radeon-RX-9070")

print(f"Total characters extracted: {len(content)}")
print("\nFirst 500 characters:")
print(content[:500])