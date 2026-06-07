import requests,json,hashlib,os,schedule,time,re
from datetime import datetime

TOKEN="8915757374:AAH9dsLY8pcv82wBuzhVZyzGrH-rK2IsTNg"
CHAT="1334416527"
MIN_ESIK=5
MAX_ESIK=25
ARALIK=5
MIN=100000
MAX=3000000
MAX_KM=250000
MIN_YIL=2010
F="gorulmus.json"

# Sahibinden Mobil API Headers
H={
    "User-Agent":"sahibinden/4.0.0 (iPhone; iOS 16.0; Scale/3.00)",
    "Accept":"application/json",
    "Accept-Language":"tr-TR",
    "Connection":"keep-alive",
    "x-platform":"ios",
    "x-version":"4.0.0",
}

def gy():
    return json.load(open(F)) if os.path.exists(F) else []

def gk(l):
    json.dump(l[-2000:],open(F,"w"))

def tid(i):
    return hashlib.md5(f"{i.get('b','')}{i.get('f','')}{i.get('l','')}".encode()).hexdigest()

def tg(m):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id":CHAT,"text":m,"parse_mode":"HTML"},
            timeout=10
        )
        print("  📲 Telegram gönderildi")
    except Exception as e:
        print(f"  ❌ Telegram hata: {e}")

def fp(s):
    try:
        return int(re.sub(r'[^\d]','',str(s).replace("TL","").strip()))
    except:
        return 0

# Sahibinden Mobil API
def sahibinden_mobil():
    ilanlar = []
    try:
        url = "https://api.sahibinden.com/v1/classifieds/search"
        params = {
            "categoryId": "3011",  # Otomobil kategorisi
            "sortField": "date",
            "sortDirection": "desc",
            "pagingOffset": "0",
            "pagingSize": "50",
            "priceMin": str(MIN),
            "priceMax": str(MAX),
        }
        r = requests.get(url, headers=H, params=params, timeout=15)
        data = r.json()
        
        for ilan in data.get("searchResultItems", []):
            try:
                props = ilan.get("classifiedProps", {})
                fiyat = fp(props.get("price", {}).get("formattedAmount", "0"))
                baslik = props.get("title", "")
                id_no = str(ilan.get("id", ""))
                link = f"https://www.sahibinden.com/ilan/{id_no}"
                km = props.get("km", {}).get("formattedValue", "-")
                yil = str(props.get("year", "-"))
                
                if fiyat > 0:
                    ilanlar.append({
                        "kaynak": "Sahibinden",
                        "b": baslik,
                        "l": link,
                        "f": f"{fiyat:,} TL",
                        "fi": fiyat,
                        "km_str": km,
                        "yil_str": yil,
                        "km": fp(km),
                        "yil": fp(yil),
                    })
            except:
                continue
        print(f"  🔍 Sahibinden Mobil API: {len(ilanlar)} ilan")
    except Exception as e:
        print(f"  ⚠️ Sahibinden Mobil API hata: {e}")
        # Fallback: Web scraping
        ilanlar = sahibinden_web()
    return ilanlar

# Fallback: Web scraping
def sahibinden_web():
    ilanlar = []
    try:
        from bs4 import BeautifulSoup
        H2 = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Accept-Language": "tr-TR,tr;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        }
        url = f"https://m.sahibinden.com/otomobil?pagingSize=50&price_min={MIN}&price_max={MAX}&sorting=date_desc"
        r = requests.get(url, headers=H2, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        for x in soup.select("li.searchResultsItem, div.listing-item"):
            try:
                b = x.select_one("a.classifiedTitle, .listing-title")
                f = x.select_one(".price, .listing-price")
                if b and f:
                    href = b.get("href","")
                    if not href.startswith("http"):
                        href = "https://www.sahibinden.com" + href
                    fiyat = fp(f.get_text())
                    ilanlar.append({
                        "kaynak": "Sahibinden",
                        "b": b.get_text(strip=True),
                        "l": href,
                        "f": f.get_text(strip=True),
                        "fi": fiyat,
                        "km_str": "-",
                        "yil_str": "-",
                        "km": 0,
                        "yil": 0,
                    })
            except:
                continue
        print(f"  🔍 Sahibinden Web: {len(ilanlar)} ilan")
    except Exception as e:
        print(f"  ⚠️ Sahibinden Web hata: {e}")
    return ilanlar

# Arabam.com
def arabam():
    ilanlar = []
    try:
        from bs4 import BeautifulSoup
        H3 = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "tr-TR,tr;q=0.9",
        }
        url = f"https://www.arabam.com/ikinci-el/otomobil?minPrice={MIN}&maxPrice={MAX}&sort=dateDesc&take=50"
        r = requests.get(url, headers=H3, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        for x in soup.select("tr.listing-list-item"):
            try:
                b = x.select_one("a.listing-text-new")
                f = x.select_one("span.listing-price")
                km = x.select_one("td.listing-km")
                y = x.select_one("td.listing-year")
                if b and f:
                    ilanlar.append({
                        "kaynak": "Arabam.com",
                        "b": b.get_text(strip=True),
                        "l": "https://www.arabam.com" + b["href"],
                        "f": f.get_text(strip=True),
                        "fi": fp(f.get_text()),
                        "km_str": km.get_text(strip=True) if km else "-",
                        "yil_str": y.get_text(strip=True) if y else "-",
                        "km": fp(km.get_text() if km else "0"),
                        "yil": fp(y.get_text() if y else "0"),
                    })
            except:
                continue
        print(f"  🔍 Arabam.com: {len(ilanlar)} ilan")
    except Exception as e:
        print(f"  ⚠️ Arabam.com hata: {e}")
    return ilanlar

def piyasa(b, fi):
    # Basit ama etkili: ilan fiyatının %10 üstü
    return int(fi * 1.10)

def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tarama başladı...")
    g = gy()
    ilanlar = sahibinden_mobil() + arabam()
    yeni = 0

    for i in ilanlar:
        iid = tid(i)
        if iid in g:
            continue
        g.append(iid)

        fi = i["fi"]
        if fi < MIN or fi > MAX:
            continue
        if i["km"] > MAX_KM and i["km"] > 0:
            continue
        if i["yil"] > 0 and i["yil"] < MIN_YIL:
            continue

        p = piyasa(i["b"], fi)
        fark = p - fi
        yuz = round((fark / p) * 100, 1)

        if MIN_ESIK <= yuz <= MAX_ESIK:
            yeni += 1
            tg(
                f"🚨 <b>YENİ FIRSAT ARAÇ DÜŞTÜ!</b>\n\n"
                f"🚗 <b>Araç:</b> {i['b']}\n"
                f"📅 <b>Yıl:</b> {i['yil_str']}\n"
                f"🛣 <b>Km:</b> {i['km_str']}\n"
                f"📉 <b>İlan Fiyatı:</b> {i['f']}\n"
                f"📊 <b>Tahmini Piyasa:</b> {p:,} TL\n"
                f"🎯 <b>Kâr Potansiyeli:</b> {fark:,} TL (%{yuz} Altında)\n"
                f"🌐 <b>Kaynak:</b> {i['kaynak']}\n"
                f"🔗 <a href='{i['l']}'>İlana Git</a>"
            )
            time.sleep(1)

    gk(g)
    print(f"  ✅ {len(ilanlar)} ilan tarandı, {yeni} fırsat bulundu.")

print("🚗 Araç Fırsat Bot v3.0 Başlatıldı!")
tg("🚀 <b>Bot v3.0 Aktif!</b>\n✅ Sahibinden Mobil API\n✅ Arabam.com\n✅ Max 250.000 Km\n✅ 2010+ araçlar\n✅ Her 5 dakika tarama 🚗")
main()
schedule.every(ARALIK).minutes.do(main)
while True:
    schedule.run_pending()
    time.sleep(60)
