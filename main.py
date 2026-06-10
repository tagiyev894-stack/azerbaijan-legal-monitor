import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


# ---------------------------
# TELEGRAM SEND
# ---------------------------
def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# ---------------------------
# PRESIDENT (DECREES + ORDERS)
# ---------------------------
def get_president():
    urls = [
        "https://president.az/az/documents/category/decrees",
        "https://president.az/az/documents/category/orders"
    ]

    results = []

    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            items = soup.find_all("a")

            for i in items:
                title = i.get_text(strip=True)
                link = i.get("href")

                if not title or not link:
                    continue

                if len(title) < 10:
                    continue

                if "http" not in link:
                    link = "https://president.az" + link

                results.append((title, link))

        except:
            continue

    return results[:8]


# ---------------------------
# NK (FILTERED DOCUMENTS)
# ---------------------------
def get_nk():
    url = "https://nk.gov.az/az/senedler/hamisi"

    try:
        r = requests.get(url, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        results = []

        for a in soup.find_all("a"):
            title = a.get_text(" ", strip=True)
            link = a.get("href")

            if not title or not link:
                continue

            t = title.lower()

            # ❌ noise filter (ən vacib hissə)
            bad_words = [
                "haqqında", "struktur", "qayda", "əsasnamə",
                "fəaliyyət", "ümumi", "portal", "səhifə",
                "məlumat", "kontakt", "daxil ol"
            ]

            if any(x in t for x in bad_words):
                continue

            # ✔ only legal acts
            if not any(x in t for x in [
                "qərar", "sərəncam", "fərman", "təsdiq", "qanun"
            ]):
                continue

            # too short = noise
            if len(title) < 15:
                continue

            if "http" not in link:
                link = "https://nk.gov.az" + link

            results.append((title, link))

        return results[:8]

    except:
        return []


# ---------------------------
# SIMPLE SUMMARY
# ---------------------------
def summary(title):
    t = title.lower()

    if "vergi" in t:
        return "Vergi qanunvericiliyində tənzimləmə dəyişiklikləri."
    if "əmək" in t:
        return "Əmək münasibətlərində hüquqi tənzimləmə."
    if "təhsil" in t:
        return "Təhsil sahəsində normativ dəyişikliklər."
    if "qərar" in t:
        return "İnzibati qaydalarda dəyişiklik."
    if "fərman" in t:
        return "Prezident tərəfindən hüquqi tənzimləmə."
    if "sərəncam" in t:
        return "Operativ idarəetmə aktı."
    return "Yeni normativ hüquqi akt qəbul edilmişdir."


# ---------------------------
# BUILD MESSAGE (NO INDENT ERRORS EVER)
# ---------------------------
def build():
    msg = "📅 GÜNDƏLİK HÜQUQİ AKTLAR\n\n"

    sources = {
        "🇦🇿 PREZİDENT": get_president(),
        "🏛 NAZİRLƏR KABİNETİ": get_nk()
    }

    for name, items in sources.items():
        msg += "📌 " + name + "\n\n"

        if not items:
            msg += "Məlumat yoxdur\n\n"
        else:
            for item in items:
                title = item[0]
                link = item[1]

                msg += "📄 " + title + "\n"
                msg += "🧾 " + summary(title) + "\n"
                msg += "🔗 " + link + "\n\n"

        msg += "----------------------\n\n"

    return msg


# ---------------------------
# MAIN
# ---------------------------
def main():
    send(build())


main()
