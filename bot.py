import requests,json,hashlib,os,schedule,time,re
from bs4 import BeautifulSoup
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
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept-Language":"tr-TR,tr;q=0.9"}
def gy():
 return json.load(open(F)) if os.path.exists(F) else []
def gk(l):
 json.dump(l[-2000:],open(F,"w"))
def tid(i):
 return hashlib.md5(f"{i.get('b','')}{i.get('f','')}{i.get('l','')}".encode()).hexdigest()
def tg(m):
 try:requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT,"text":m,"parse_mode":"HTML"},timeout=10)
 except:pass
def fp(s):
 try:return int(re.sub(r'[^\d]','',s.replace("TL","").strip()))
 except:return 0
def kmp(s):
 try:return int(re.sub(r'[^\d]','',s.strip()))
 except:return 0
def yp(s):
 try:
  m=re.search(r'20\d\d|19\d\d',s)
  return int(m.group()) if m else 0
 except:return 0
def piyasa(b):
 fiyatlar=[]
 try:
  s="+".join(b.split()[:3])
  r=requests.get(f"https://www.sahibinden.com/otomobil?query={s}&pagingSize=20&sorting=price_asc",headers=H,timeout=12)
  soup=BeautifulSoup(r.text,"html.parser")
  for x in soup.select("tr.searchResultsItem"):
   try:
    f=x.select_one("td.searchResultsPriceValue")
    if f:
     fi=fp(f.get_text())
     if MIN<fi<MAX:fiyatlar.append(fi)
   except:pass
 except:pass
 if len(fiyatlar)>=3:
  fiyatlar.sort()
  return fiyatlar[len(fiyatlar)//2]
 return 0
def sahibinden():
 il=[]
 try:
  r=requests.get(f"https://www.sahibinden.com/otomobil?pagingSize=50&price_min={MIN}&price_max={MAX}&sorting=date_desc",headers=H,timeout=15)
  soup=BeautifulSoup(r.text,"html.parser")
  for x in soup.select("tr.searchResultsItem"):
   try:
    b=x.select_one("td.searchResultsTitleValue a")
    f=x.select_one("td.searchResultsPriceValue")
    a=x.select("td.searchResultsAttributeValue")
    if b and f:
     il.append({"kaynak":"Sahibinden","b":b.get_text(strip=True),"l":"https://www.sahibinden.com"+b["href"],"f":f.get_text(strip=True),"fi":fp(f.get_text(strip=True)),"km":kmp(a[1].get_text() if len(a)>1 else "0"),"yil":yp(a[0].get_text() if len(a)>0 else "0"),"km_str":a[1].get_text(strip=True) if len(a)>1 else "-","yil_str":a[0].get_text(strip=True) if len(a)>0 else "-"})
   except:pass
 except:pass
 return il
def arabam():
 il=[]
 try:
  r=requests.get(f"https://www.arabam.com/ikinci-el/otomobil?minPrice={MIN}&maxPrice={MAX}&sort=dateDesc&take=50",headers=H,timeout=15)
  soup=BeautifulSoup(r.text,"html.parser")
  for x in soup.select("tr.listing-list-item"):
   try:
    b=x.select_one("a.listing-text-new")
    f=x.select_one("span.listing-price")
    km=x.select_one("td.listing-km")
    y=x.select_one("td.listing-year")
    if b and f:
     il.append({"kaynak":"Arabam.com","b":b.get_text(strip=True),"l":"https://www.arabam.com"+b["href"],"f":f.get_text(strip=True),"fi":fp(f.get_text(strip=True)),"km":kmp(km.get_text() if km else "0"),"yil":yp(y.get_text() if y else "0"),"km_str":km.get_text(strip=True) if km else "-","yil_str":y.get_text(strip=True) if y else "-"})
   except:pass
 except:pass
 return il
def main():
 print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tarama basladi...")
 g=gy()
 ilanlar=sahibinden()+arabam()
 yeni=0
 for i in ilanlar:
  iid=tid(i)
  if iid in g:continue
  g.append(iid)
  fi=i["fi"]
  if fi<MIN or fi>MAX:continue
  if i["km"]>MAX_KM and i["km"]>0:continue
  if i["yil"]>0 and i["yil"]<MIN_YIL:continue
  p=piyasa(i["b"])
  if p==0:p=int(fi*1.10)
  fark=p-fi
  yuz=round((fark/p)*100,1)
  if MIN_ESIK<=yuz<=MAX_ESIK:
   yeni+=1
   tg(f"🚨 <b>YENİ FIRSAT ARAÇ DÜŞTÜ!</b>\n\n🚗 <b>Araç:</b> {i['b']}\n📅 <b>Yıl:</b> {i['yil_str']}\n🛣 <b>Km:</b> {i['km_str']}\n📉 <b>İlan:</b> {i['f']}\n📊 <b>Piyasa:</b> {p:,} TL\n🎯 <b>Kâr:</b> {fark:,} TL (%{yuz} Altında)\n🌐 <b>Kaynak:</b> {i['kaynak']}\n🔗 <a href='{i['l']}'>İlana Git</a>")
   time.sleep(1)
 gk(g)
 print(f"  {len(ilanlar)} ilan, {yeni} firsat.")
main()
schedule.every(ARALIK).minutes.do(main)
while True:schedule.run_pending();time.sleep(60)
