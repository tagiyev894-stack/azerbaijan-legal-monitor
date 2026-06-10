import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_page(url):
    try:
        r = requests.get(url, timeout=20)
        return r.text
    except:
        return ""

def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.title.text if soup.title else "Yeni akt"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def check_sources():
    sources = {
        "PREZİDENT": "https://president.az",
        "NAZİRLƏR KABİNETİ": "https://nk.gov.az",
        "E-QANUN": "https://e-qanun.az"
    }

    report = "📅 GÜNDƏLİK HÜQUQİ AKTLAR\n\n"

    for name, url in sources.items():
        html = get_page(url)
        title = extract_title(html)

        report += f"{name}\n• {title}\n• {url}\n\n"

    return report


if __name__ == "__main__":
    message = check_sources()
    send_message(message)
