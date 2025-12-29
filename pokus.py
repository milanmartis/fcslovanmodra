import os
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


BASE = "https://www.fcslovanmodra.sk"
LIST_URL = f"{BASE}/clanky"

DATABASE_URL = os.environ["DATABASE_URL"]

USER_ID = 1
CATEGORY_ID = 1

TITLE_MAX = 100
SLUG_MAX = 255


@dataclass
class ListItem:
    title: str
    slug: str
    date_posted: datetime
    detail_url: str


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")  # blog/oznam
    parts = path.split("/")
    slug = parts[1] if len(parts) >= 2 and parts[0] == "blog" else path.replace("/", "-")
    return slug[:SLUG_MAX]


def parse_sk_date(s: str) -> datetime:
    """
    Vstup: '7.10.2025' alebo '23.6.2025'
    Výstup: datetime(2025, 10, 7, 0, 0, 0)
    """
    s = s.strip()
    # povolíme aj medzery, napr. '23.6.2025 '
    m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$", s)
    if not m:
        raise ValueError(f"Neviem naparsovať dátum: {s!r}")
    d, mo, y = map(int, m.groups())
    return datetime(y, mo, d, 0, 0, 0)


def parse_list_page() -> list[ListItem]:
    """
    Z /clanky vytiahne title + date + detail link.
    Na stránke sú posty v blokoch: ### TITLE ... DATE ... link 'Zobraziť viac'
    """
    soup = BeautifulSoup(fetch_html(LIST_URL), "html.parser")

    items: list[ListItem] = []

    # podľa toho čo je vidno na /clanky, title je v h3 (###)
    for h3 in soup.find_all(["h3"]):
        title = h3.get_text(strip=True)
        if not title:
            continue

        # v tom istom "sekčnom" bloku je vždy aj link na detail (/blog/slug)
        block_text = []
        # zoberieme pár nasledujúcich súrodencov (texty + dátum)
        n = h3
        for _ in range(20):
            n = n.find_next()
            if n is None:
                break
            # stop, keď narazíme na ďalší h3 (ďalší článok)
            if n.name == "h3":
                break
            # zbierame texty kvôli dátumu
            t = n.get_text(" ", strip=True) if hasattr(n, "get_text") else ""
            if t:
                block_text.append(t)

        joined = "\n".join(block_text)

        # dátum býva samostatne ako '7.10.2025'
        date_match = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", joined)
        if not date_match:
            # ak sa nepodarí dátum, preskočíme
            continue
        date_posted = parse_sk_date(date_match.group(1))

        # detail link - prvý <a href="/blog/..."> po h3
        a = h3.find_next("a", href=re.compile(r"^/blog/"))
        if not a:
            continue
        detail_url = urljoin(BASE, a["href"].split("?")[0])
        slug = slug_from_url(detail_url)

        # limity title
        if len(title) > TITLE_MAX:
            title = title[: TITLE_MAX - 1] + "…"

        items.append(ListItem(title=title, slug=slug, date_posted=date_posted, detail_url=detail_url))

    # dedupe podľa slug (ak by sa niečo opakovalo)
    uniq = {}
    for it in items:
        uniq[it.slug] = it
    return list(uniq.values())


def extract_article_content(detail_url: str) -> str:
    """
    Z detailu vyberieme len obsah článku (nie menu/footer).
    Heuristika:
    - nájdi h1
    - zober najbližší kontajner okolo h1
    - odstráň elementy, ktoré patria do navigácie/footeru
    - vytiahni text
    """
    soup = BeautifulSoup(fetch_html(detail_url), "html.parser")

    # vyhoď nav / footer ak existujú
    for tag in soup.find_all(["nav", "footer", "header"]):
        tag.decompose()

    # vyhoď časti, ktoré obsahujú typický footer text (ak je to v div/span)
    footer_phrase = "Sme najstarší športový klub"
    for el in soup.find_all(string=lambda s: isinstance(s, str) and footer_phrase in s):
        # zmaž rodičovský blok, nie len text
        parent = el.parent
        if parent:
            parent.decompose()

    h1 = soup.find("h1")
    if not h1:
        # fallback: zober main/article
        container = soup.find("main") or soup.find("article") or soup.body
    else:
        # najbližší rozumný kontajner (parent)
        container = h1.parent

    if not container:
        return ""

    # odstráň samotný h1 z contentu (title ukladáš zvlášť)
    h1_in = container.find("h1")
    if h1_in:
        h1_in.decompose()

    text_content = container.get_text("\n", strip=True)
    text_content = re.sub(r"\n{3,}", "\n\n", text_content).strip()
    return text_content


def ensure_utf8(engine):
    with engine.connect() as conn:
        conn.execute(text("SET client_encoding TO 'UTF8'"))


def post_exists(session, slug: str) -> bool:
    row = session.execute(text("SELECT id FROM post WHERE slug=:s LIMIT 1"), {"s": slug}).fetchone()
    return bool(row)


def insert_post(session, title: str, slug: str, content: str, date_posted: datetime, source_url: str):
    # voliteľne nechaj zdroj na konci contentu, aby si vedela odkiaľ to prišlo
    content_with_src = f"{content}\n\n---\nZdroj: {source_url}"

    session.execute(
        text("""
            INSERT INTO post (title, slug, content, date_posted, user_id, category_id)
            VALUES (:title, :slug, :content, :date_posted, :user_id, :category_id)
        """),
        {
            "title": title,
            "slug": slug,
            "content": content_with_src,
            "date_posted": date_posted,
            "user_id": USER_ID,
            "category_id": CATEGORY_ID,
        },
    )


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    ensure_utf8(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    items = parse_list_page()
    print(f"Found {len(items)} posts on list page")

    inserted = 0
    try:
        for it in items:
            if post_exists(session, it.slug):
                print("EXISTS:", it.slug)
                continue

            content = extract_article_content(it.detail_url)
            if not content:
                print("SKIP empty content:", it.detail_url)
                continue

            insert_post(session, it.title, it.slug, content, it.date_posted, it.detail_url)
            inserted += 1
            print("INSERT:", it.date_posted.date(), it.slug, "|", it.title)

        session.commit()
        print(f"Done. Inserted: {inserted}")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
