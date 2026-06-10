import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# ----------------------------
# REAL PARSERS
# ----------------------------

def get_president():
    url = "https://president.az/az/news"
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select("div.news-inner h3 a")

    results = []
    for i in items[:5]:
        title = i.text.strip()
        link = "https://president.az" + i.get("href", "")
        results.append((title, link))

    return results


def get_nk():
    url = "https://nk.gov.az/az/documents"
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select("a")

    results = []
    for i in items[:10]:
        title = i.text.strip()
        link = i.get("href")

        if title and link and "http" not in link:
            link = "https://nk.gov.az" + link
            results.append((title, link))

    return results[:5]


def get_eqanun():
    url = "https://e-qanun.az/framework"
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select("a")

    results = []
    for i in items[:15]:
        title = i.text.strip()
        link = i.get("href")

        if title and link and "javascript" not in link:
            if "http" not in link:
                link = "https://e-qanun.az" + link
            results.append((title, link))

    return results[:5]


# ----------------------------
# SIMPLE SUMMARY ENGINE
# ----------------------------

def summary(title):
    t = title.lower()

    if "qanun" in t:
        return "Qanunvericilik bazasında yeni hüquqi tənzimləmə."
    if "fərman" in t:
        return "Prezident tərəfindən yeni idarəetmə və hüquqi tənzimləmə."
    if "qərar" in t:
        return "İnzibati və icraedici qaydalarda yenilənmə."
    if "deyisiklik" in t or "dəyişiklik" in t:
        return "Mövcud hüquqi aktlara dəyişikliklər edilib."
    return "Yeni hüquqi sənəd dərc olunub."


# ----------------------------
# MESSAGE BUILDER
# ----------------------------

def build():
    msg = "📅 GÜNDƏLİK HÜQUQİ AKTLAR\n\n"

    sources = {
        "PREZİDENT": get_president(),
        "NAZİRLƏR KABİNETİ": get_nk(),
        "E-QANUN": get_eqanun()
    }

    for name, items in sources.items():
        msg += f"📌 {name}\n\n"

        for title, link in items:
            msg += f"🏷 {title}\n🧾 {summary(title)}\n🔗 {link}\n\n"

        msg += "----------------------\n\n"

    return msg


def main():
    message = build()
    send(message)


main()
