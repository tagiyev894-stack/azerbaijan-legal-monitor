import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz  # Python 3.9+ olduqda zoneinfo ilə də əvəz edə bilərsən

# ---------- Telegram settings ----------
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BAKU_TZ = pytz.timezone("Asia/Baku")

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
    """Bugünkü tarixi AZ formatında qaytarır (10.06.2026)."""
    return datetime.now(BAKU_TZ).strftime("%d.%m.%Y")

# ---------- Köməkçi: səhifədəki bugünkü sənədləri tap ----------
def find_today_docs(url, link_prefix="", date_format="%d.%m.%Y"):
    """
    Verilən url‑dən bütün <a> elementlərini gəzir.
    Hər bir keçidin valideyn elementində bugünkü tarix varsa,
    onu nəticəyə əlavə edir.
    """
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

            # Tam keçid düzəlt
            if not href.startswith("http"):
                href = link_prefix + href

            # Valideyn blokun bütün mətnini yoxla
            parent_text = a.find_parent().get_text(separator=" ", strip=True) if a.find_parent() else ""
            if today in parent_text:
                items.append((title, href))
    except Exception as e:
        print(f"{url} - xəta: {e}")
    return items

# ---------- Mənbələr ----------
def get_president_today():
    """Prezident saytından bugünkü fərman və sərəncamlar."""
    docs = []
    for cat in ["decrees", "orders"]:
        url = f"https://president.az/az/documents/category/{cat}"
        docs += find_today_docs(url, link_prefix="https://president.az")
    return docs

def get_nk_today():
    """Nazirlər Kabinetindən bugünkü sənədlər."""
    url = "https://nk.gov.az/az/senedler/hamisi"
    docs = find_today_docs(url, link_prefix="https://nk.gov.az")
    # Əlavə filtr: yalnız hüquqi sənədlər
    filtered = []
    for title, link in docs:
        low = title.lower()
        if any(k in low for k in ["qərar", "sərəncam", "fərman", "qanun", "qayda", "təsdiq"]):
            filtered.append((title, link))
    return filtered

def get_eqanun_today():
    """E-qanun.az saytından bugünkü yeni sənədlər."""
    # Əsas səhifədəki "Yeni sənədlər" bölməsi
    url = "https://www.e-qanun.az/"
    docs = find_today_docs(url, link_prefix="https://www.e-qanun.az")
    # E‑qanun bəzən gün.ay.il formatında verir, ona görə yoxladıq
    if not docs:
        # Alternativ: print/change səhifəsi (tarix çox vaxt dd.mm.yy olur)
        url2 = "https://www.e-qanun.az/print/change"
        docs2 = find_today_docs(url2, link_prefix="https://www.e-qanun.az")
        docs += docs2
    return docs

# ---------- Qısa məzmun etiketi ----------
def summary_tag(title, link):
    """1‑2 sözlük qısa təsvir."""
    t = title.lower()
    if "fərman" in t or "/decrees" in link:
        return "📜 Fərman"
    if "sərəncam" in t or "/orders" in link:
        return "📋 Sərəncam"
    if "qanun" in t:
        return "⚖️ Qanun"
    if "qərar" in t:
        return "📌 Qərar"
    if "dəyişiklik" in t:
        return "🔄 Dəyişiklik"
    if "əsasnamə" in t or "nizamnamə" in t:
        return "📑 Əsasnamə"
    return "📄 Sənəd"

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
                tag = summary_tag(title, link)
                msg += f"  {tag}\n"
                msg += f"  {title}\n"
                msg += f"  🔗 {link}\n\n"
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
