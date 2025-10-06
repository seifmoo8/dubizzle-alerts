import requests
from bs4 import BeautifulSoup
import time
import os
import telegram

# ==============================
# إعداداتك
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.dubizzle.com.eg/mobile-phones-tablets-accessories-numbers/mobile-phones/apple-iphone/alexandria/"
CHECK_INTERVAL = 60 * 5  # كل 5 دقايق
LIST_FILE = "last_ads.txt"
# ==============================

bot = telegram.Bot(token=BOT_TOKEN)

def send_telegram(message: str):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print("❌ خطأ أثناء الإرسال:", e)

def fetch_listing_titles():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.select('a[data-testid="listing-link"]')
    titles = [a.get_text(strip=True) for a in links if a.get_text(strip=True)]
    return titles

def read_last():
    if os.path.exists(LIST_FILE):
        with open(LIST_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def write_last(ads):
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ads))

def main():
    print("✅ تشغيل البوت...")
    send_telegram("✅ تم تشغيل بوت Dubizzle Alerts بنجاح.")

    last_ads = read_last()

    while True:
        print("🔍 فحص الإعلانات...")
        try:
            current_ads = set(fetch_listing_titles())

            if not current_ads:
                print("⚠️ مفيش إعلانات جديدة.")
            else:
                new_ads = current_ads - last_ads
                if new_ads:
                    msg = "📢 إعلانات جديدة على Dubizzle:\n" + "\n".join(new_ads)
                    send_telegram(msg)
                    write_last(current_ads)
                    print("✨ تم العثور على إعلانات جديدة.")
                else:
                    print("😴 مفيش جديد حالياً.")
        except Exception as e:
            print("❌ خطأ:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
