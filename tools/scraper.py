import requests
from bs4 import BeautifulSoup


def scrape_url(url: str) -> str:
    """
    Takes a URL and returns the clean text content of that page.
    Strips all HTML tags, scripts, and styling.
    """
    print(f"[Scraper] Scraping: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags — we only want readable text
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        # Collapse extra whitespace
        clean_text = " ".join(text.split())

        print(f"[Scraper] Extracted {len(clean_text)} characters.")
        return clean_text[:5000]  # Cap at 5000 chars to avoid token overflow

    except Exception as e:
        print(f"[Scraper] Failed to scrape {url}: {e}")
        return ""


def scrape_multiple(urls: list) -> list:
    """
    Scrapes multiple URLs and returns a list of text content.
    Skips any URL that fails.
    """
    results = []
    for url in urls:
        content = scrape_url(url)
        if content:
            results.append({"url": url, "content": content})
    return results