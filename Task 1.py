import random, re
import requests
import pandas as pd
from bs4 import BeautifulSoup

LIVE = False   # Set to True to scrape the real website (needs internet)

RATING = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
CATS = ["Fiction","Mystery","Science","History","Travel","Poetry","Romance","Business"]

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        title  = card.h3.a["title"]
        price  = float(re.sub(r"[^\d.]", "", card.select_one("p.price_color").text))
        rating = RATING[card.select_one("p.star-rating")["class"][1]]
        stock  = "In stock" in card.select_one("p.instock").text
        cat    = card.get("data-cat", "Unknown")   # category exists only in the sample HTML
        rows.append([title, price, rating, stock, cat])
    return rows

def sample_html(n=120):
    """Builds site-like HTML for an offline demo"""
    random.seed(42)
    words = ["Silent","River","Hidden","Garden","Night","Empire","Code","Moon","Last","Winter","Secret","Journey"]
    names = ["One","Two","Three","Four","Five"]
    out = ["<html><body>"]
    for i in range(n):
        cat = random.choice(CATS)
        t = f"{random.choice(words)} {random.choice(words)} {i+1}"
        price = round(random.gauss(35, 14), 2); price = max(10, min(price, 60))
        out.append(f'''<article class="product_pod" data-cat="{cat}"><h3><a title="{t}">{t[:20]}</a></h3>
        <p class="price_color">£{price}</p><p class="star-rating {random.choice(names)}"></p>
        <p class="instock availability">{random.choice(["In stock","Out of stock"])}</p></article>''')
    return "".join(out) + "</body></html>"

if LIVE:
    data = []
    for p in range(1, 51):
        r = requests.get(f"https://books.toscrape.com/catalogue/page-{p}.html", timeout=10)
        data += parse_page(r.text)
else:
    data = parse_page(sample_html())

df = pd.DataFrame(data, columns=["title","price","rating","in_stock","category"])
df.to_csv("books.csv", index=False)
print("Total books scraped:", len(df))
print(df.head())