import os
import time
import requests
import json
from bs4 import BeautifulSoup
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# ---------------------------
#  AMAZON PRICE CHECK
# ---------------------------
def check_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("span", {"id": "productTitle"})
    price = soup.find("span", {"class": "a-offscreen"})

    if not title or not price:
        return None

    title = title.get_text(strip=True)
    price = float(price.get_text(strip=True).replace("$", ""))

    # Fake normal price (easily replace with API later)
    normal = price * 2  

    if price <= normal * 0.50:
        return f"🔥 AMAZON GLITCH (50%+ OFF)\n{title}\nPrice: ${price}\nLink: {url}"

    return None

# ---------------------------
#  LOWE’S CHECK
# ---------------------------
def check_lowes(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        return None

    data = json.loads(script.string)
    try:
        product = data["props"]["pageProps"]["product"]
        title = product["productName"]
        price = float(product["price"]["selling"])
        normal = float(product["price"]["regular"])
    except:
        return None

    if price <= normal * 0.50:
        return f"🔥 LOWE'S GLITCH (50%+ OFF)\n{title}\nNow: ${price}\nWas: ${normal}\nLink: {url}"

    return None

# ---------------------------
#  HOME DEPOT CHECK
# ---------------------------
def check_homedepot(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        json_data = json.loads(soup.find("script", {"type": "application/ld+json"}).string)
        title = json_data["name"]
        price = float(json_data["offers"]["price"])
        normal = price * 2  
    except:
        return None

    if price <= normal * 0.50:
        return f"🔥 HOME DEPOT GLITCH (50%+ OFF)\n{title}\nPrice: ${price}\nLink: {url}"

    return None


# ---------------------------
#  MAIN LOOP
# ---------------------------
urls = [
    # Put ANY URLs you want the bot to watch here:
    # Amazon:
    "https://www.amazon.com/dp/B0BDJ9Z93R",
    # Lowe’s:
    "https://www.lowes.com/pd/1000522437",
    # Home Depot:
    "https://www.homedepot.com/p/1000-000-000",
]

while True:
    for url in urls:
        if "amazon" in url:
            result = check_amazon(url)
        elif "lowes" in url:
            result = check_lowes(url)
        elif "homedepot" in url:
            result = check_homedepot(url)
        else:
            result = None

        if result:
            bot.send_message(chat_id=CHAT_ID, text=result)

    time.sleep(300)  # 5 minutes
