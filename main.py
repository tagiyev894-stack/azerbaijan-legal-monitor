import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


SOURCES = {
    "PREZİDENT": "https://president.az",
    "NAZİRLƏR KABİNETİ": "https://nk.gov.az",
    "E-QANUN": "https://e-qanun.az"
}


def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_title(url):
    try:
        html = requests.get(url, timeout=20).text
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.text if soup.title else "Yeni akt"
        return title
    except:
        return "Məlumat alınmadı"


def generate_summary(title, source):
    title_lower = title.lower()

    if "vergi" in title_lower:
        return "Vergi qanunvericiliyində tənzimləmə və inzibati dəyişikliklər nəzərdə tutulur."
    elif "əmək" in title_lower:
        return "Əmək münasibətləri və əmək hüquqları üzrə tənzimləmələr yenilənir."
    elif "təhsil" in title_lower:
        return "Təhsil sistemində normativ və inzibati dəyişikliklər edilir."
    elif "məcəllə" in title_lower:
        return "Müvafiq məcəllədə hüquqi və struktur dəyişikliklər həyata keçirilir."
    else:
        return f"{source} üzrə yeni normativ hüquqi akt dərc olunmuşdur."


def main():
    message = "📅 GÜNDƏLİK HÜQUQİ AKTLAR\n\n"

    for name, url in SOURCES.items():
        title = get_title(url)
        summary = generate_summary(title, name)

        message += f"""📌 {name}
🏷 {title}
🧾 {summary}
🔗 {url}

----------------------

"""

    send(message)


main()
