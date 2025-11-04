import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def _safe_get(url):
    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        r.raise_for_status()
        return r.text
    except Exception:
        return ""

def get_category_from_url(url):
    if not url: return "General"
    match = re.search(r"/(world|politics|business|tech|technology|sports|india|entertainment|health|science|economy|business-news)/", url, re.I)
    if match:
        return match.group(1).capitalize()
    if "sport" in url.lower(): return "Sports"
    return "General"

def scrape_bbc():
    html = _safe_get("https://www.bbc.com/news")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("a.gs-c-promo-heading"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = ("https://www.bbc.com" + href) if href.startswith("/") else href
        if title and link:
            items.append({"Source":"BBC","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_cnn():
    html = _safe_get("https://edition.cnn.com/")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("h3.cd__headline a, span.container__headline-text"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = ("https://edition.cnn.com" + href) if href.startswith("/") else href
        if title and link:
            items.append({"Source":"CNN","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_toi():
    html = _safe_get("https://timesofindia.indiatimes.com/home/headlines")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("span.w_tle a, .tabLeadHeadline a"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = ("https://timesofindia.indiatimes.com" + href) if href.startswith("/") else href
        if title and link:
            items.append({"Source":"Times of India","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_ndtv():
    html = _safe_get("https://www.ndtv.com/latest")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("div.news_Itm a"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = href if href.startswith("http") else "https://www.ndtv.com" + href
        if title and link:
            items.append({"Source":"NDTV","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_the_hindu():
    html = _safe_get("https://www.thehindu.com/")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("a.title, h3 a"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = href if href.startswith("http") else "https://www.thehindu.com" + href
        if title and link:
            items.append({"Source":"The Hindu","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_aljazeera():
    html = _safe_get("https://www.aljazeera.com/")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for h in soup.select("a.u-clickable-card__link, h3 a"):
        title = h.get_text(strip=True)
        href = h.get('href') or ""
        link = href if href.startswith("http") else "https://www.aljazeera.com" + href
        if title and link:
            items.append({"Source":"Al Jazeera","Category":get_category_from_url(link),"Title":title,"Link":link,"Scraped_At":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return items

def scrape_all(selected=None):
    selected = selected or ["BBC","CNN","Times of India","NDTV","The Hindu","Al Jazeera"]
    data = []
    if "BBC" in selected: data += scrape_bbc()
    if "CNN" in selected: data += scrape_cnn()
    if "Times of India" in selected: data += scrape_toi()
    if "NDTV" in selected: data += scrape_ndtv()
    if "The Hindu" in selected: data += scrape_the_hindu()
    if "Al Jazeera" in selected: data += scrape_aljazeera()
    return data
