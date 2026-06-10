import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

seen = set()


def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# -------------------------
# CLEAN TEXT
# -------------------------
def clean(t):
    return re.sub(r"\s+", " ", t).strip()


# -------------------------
# PRESIDENT (DECREES + ORDERS)
# -------------------------
def president(url):
    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("div.document-item, div.news-item, li")

    results = []

    for i in items:
        a = i.find("a")
        if not a:
            continue

        title = clean(a.text)
        link = a.get("href")

        if not title or len(title) < 10:
            continue

        if link and "http" not in link:
            link = "https://president.az" + link

        key = title + link
        if key in seen:
            continue
        seen.add(key)

        results.append(title + "||" + link)

    return results[:8]


# -------------------------
# NK ACTS (REAL PAGE)
# -------------------------
def nk():
    url = "https://nk.gov.az/az/senedler/hamisi"
    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.find_all("a")

    results = []

    for i in items:
        title = i.get_text(" ", strip=True)
        link = i.get("href")

        if not title or not link:
            continue

        title_lower = title.lower()

        # yalnız hüquqi aktları saxla
        if not any(x in title_lower for x in [
            "qərar", "sərəncam", "fərman",
            "qanun", "qaydası", "qayda", "təsdiq"
        ]):
            continue

        # boş və ya çox qısa şeyləri at
        if len(title) < 15:
            continue

        if "http" not in link:
            link = "https://nk.gov.az" + link

        results.append((title, link))

    return results[:10]


# -------------------------
# SIMPLE LEGAL SUMMARY ENGINE
# -------------------------
def summary(title):
    t = title.lower()

    if "fərman" in t:
        return "Normativ idarəetmə və icra mexanizmlərində dəyişikliklər."
    if "qərar" in t:
        return "İnzibati qaydaların və icra proseslərinin tənzimlənməsi."
    if "sərəncam" in t:
        return "Operativ idarəetmə və təşkilati tədbirlər."
    if "qanun" in t:
        return "Hüquqi normativ bazada dəyişiklik və ya yeni tənzimləmə."
    return "Yeni normativ hüquqi akt qəbul edilmişdir."


# -------------------------
# BUILD MESSAGE
# -------------------------
def build():
    msg = "📅 GÜNDƏLİK HÜQUQİ AKTLAR\n\n"

    sources = {
        "🇦🇿 PREZİDENT (FƏRMAN + SƏRƏNCAM)": president("https://president.az/az/documents/category/decrees") +
                                          president("https://president.az/az/documents/category/orders"),

        "🏛 NAZİRLƏR KABİNETİ": nk()
    }

    for name, items in sources.items():
        msg += f"📌 {name}\n\n"

        if not items:
            msg += "Məlumat yoxdur\n\n"

        title = item[0] if len(item) > 0 else ""
link = item[1] if len(item) > 1 else ""

            msg += f"""📄 {title}
🧾 {summary(title)}
🔗 {link}

"""

        msg += "----------------------\n\n"

    return msg


def main():
    send(build())


main()
