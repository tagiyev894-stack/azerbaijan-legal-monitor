import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # pytz əvəzinə

# ---------- Telegram settings ----------
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BAKU_TZ = ZoneInfo("Asia/Baku")

def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("Token və ya Chat ID tapılmadı.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except Exception as e:
        print("Telegram göndərmə xətası:", e)

# ---------- Bugünkü tarix ----------
def today_str():
    return datetime.now(BAKU_TZ).strftime("%d.%m.%Y")

# ---------- Köməkçi ----------
def find_today_docs(url, link_prefix=""):
    items = []
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        today = today_str()

        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            href = a["href"]
            if not title or len(title) < 5:
                continue
            if not href.startswith("http"):
                href = link_prefix + href
            parent_text = a.find_parent().get_text(separator=" ", strip=True) if a.find_parent() else ""
            if today in parent_text:
                items.append((title, href))
    except Exception as e:
        print(f"{url} - xəta: {e}")
    return items

# ---------- Mənbələr ----------
def get_president_today():
    docs = []
    for cat in ["decrees", "orders"]:
        url = f"https://president.az/az/documents/category/{cat}"
        docs += find_today_docs(url, link_prefix="https://president.az")
    return docs

def get_nk_today():
    url = "https://nk.gov.az/az/senedler/hamisi"
    docs = find_today_docs(url, link_prefix="https://nk.gov.az")
    filtered = []
    for title, link in docs:
        low = title.lower()
        if any(k in low for k in ["qərar", "sərəncam", "fərman", "qanun", "qayda", "təsdiq"]):
            filtered.append((title, link))
    return filtered

def get_eqanun_today():
    url = "https://www.e-qanun.az/"
    docs = find_today_docs(url, link_prefix="https://www.e-qanun.az")
    if not docs:
        url2 = "https://www.e-qanun.az/print/change"
        docs += find_today_docs(url2, link_prefix="https://www.e-qanun.az")
    return docs

# ---------- Qısa analiz ----------
def one_line_summary(title):
    t = title.lower()
    if "dəyişiklik" in t:
        if "vergi" in t: return "Vergi Məcəlləsinə dəyişiklik edilir."
        if "əmək" in t: return "Əmək Məcəlləsinə dəyişiklik edilir."
        if "inzibati" in t or "xətalar" in t: return "İnzibati Xətalar Məcəlləsinə dəyişiklik edilir."
        if "cinayət" in t: return "Cinayət Məcəlləsinə dəyişiklik edilir."
        if "mülki" in t: return "Mülki Məcəlləyə dəyişiklik edilir."
        if "təhsil" in t: return "Təhsil sahəsində normativ dəyişiklik."
        return "Müxtəlif normativ hüquqi aktlara dəyişiklik edilir."
    if "təsdiq" in t:
        if "qayda" in t: return "Yeni qaydalar təsdiq edilir."
        if "proqram" in t or "strategiya" in t: return "Dövlət proqramı/strategiyası təsdiq edilir."
        if "əsasnamə" in t or "nizamnamə" in t: return "Əsasnamə/Nizamnamə təsdiq edilir."
        return "Sənəd təsdiq edilir."
    if "ləğv" in t: return "Mövcud normativ akt ləğv edilir."
    if "yaradılması" in t or "təşkil" in t:
        if "komissiya" in t: return "Yeni komissiya yaradılır."
        if "idarə" in t or "agentlik" in t: return "Yeni dövlət qurumu yaradılır."
        return "Yeni qurum/struktur yaradılır."
    if "müavinət" in t or "pensiya" in t: return "Sosial ödənişlərlə bağlı tənzimləmə."
    if "güzəşt" in t: return "Güzəşt/vergi azadolmaları ilə bağlı qərar."
    if "qərar" in t: return "Nazirlər Kabineti tərəfindən qərar qəbul edilmişdir."
    if "sərəncam" in t: return "Prezident sərəncamı imzalanmışdır."
    if "fərman" in t: return "Prezident fərmanı imzalanmışdır."
    if "qanun" in t: return "Yeni qanun qəbul edilmişdir."
    return "Yeni normativ akt."

# ---------- Mesaj qur ----------
def build_message():
    msg = f"📅 Bugünkü hüquqi aktlar ({today_str()})\n\n"
    sources = {
        "🇦🇿 PREZİDENT": get_president_today,
        "🏛 NAZİRLƏR KABİNETİ": get_nk_today,
        "📚 E-QANUN": get_eqanun_today,
    }
    total = 0
    for name, func in sources.items():
        docs = func()
        if docs:
            msg += f"📌 {name}\n"
            for title, link in docs:
                summary = one_line_summary(title)
                msg += f"📄 {title}\n"
                msg += f"🔍 {summary}\n"
                msg += f"🔗 {link}\n\n"
            total += len(docs)
        else:
            msg += f"📌 {name}\n  Yeni sənəd yoxdur\n\n"
        msg += "----------------------\n\n"
    if total == 0:
        msg = "📭 Bugün heç bir yeni sənəd yoxdur."
    return msg

# ---------- Əsas ----------
if __name__ == "__main__":
    send_message(build_message())
