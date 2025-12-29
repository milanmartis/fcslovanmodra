import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.fcslovanmodra.sk"

def get_article_links():
    html = requests.get(f"{BASE}/clanky", timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select('a[href^="/blog/"]'):
        href = a.get("href")
        links.append(urljoin(BASE, href))
    # unikátne
    return sorted(set(links))

def parse_article(url):
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1")
    title = title.get_text(strip=True) if title else None

    # text článku – je to jednoduchá stránka, takže často stačí zobrať hlavný obsah
    # (podľa reálnej štruktúry možno upravíš selector)
    content = soup.get_text("\n", strip=True)

    return {"url": url, "title": title, "content": content}

links = get_article_links()
print("found", len(links), "articles")

first = parse_article(links[0]) if links else None
print(first["title"], first["url"])