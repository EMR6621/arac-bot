import requests,json,hashlib,os,schedule,time
from bs4 import BeautifulSoup
from datetime import datetime
TOKEN="8915757374:AAH9dsLY8pcv82wBuzhVZyzGrH-rK2IsTNg"
CHAT="1334416527"
ESIK=8
MIN=100000
MAX=3000000
H={"User-Agent":"Mozilla/5.0"}
F="g.json"
def gy():
 return json.load(open(F)) if os.path.exists(F) else []
def gk(l):
 json.dump(l[-1000:],open(F,"w"))
def tid(i):
 return hashlib.md5(f"{i.get('b','')}{i.get('f','')}{i.get('l','')}".encode()).hexdigest()
def tg(m):
 try:requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT,"text":m,"parse_mode":"HTML"},timeout=10)
 except:pass
def fp(s):
 try:return int(s.replace("TL","").replace(".","").replace(",","").strip())
 except:return 0
def tara():
 il=[]
 try:
  r=requests.get(f"https://www.sahibinden.com/otomobil?pagingSize=50&price_min={MIN}&price_max={MAX}&sorting=date_desc",headers=H,timeout=15)
  s=BeautifulSoup(r.text,"html.parser")
  for x in s.select("tr.searchResultsItem"):
   try:
    b=x.select_one("td.searchResultsTitleValue a")
    f=x.select_one("td.searchResultsPriceValue")
    if b and f:il.append({"b":b.get_text(strip=True),"l":"https://www.sahibinden.com"+b["href"],"f":f.get_text(strip=True),"fi":fp(f.get_text(strip=True)),"k":"Sahibinden"})
   except:pass
 except:pass
 return il
def main():
 print("Bot basladi")
 tg("✅ <b>Araç Fırsat Bot Aktif!</b>\nSahibinden taranıyor 🚗")
 g=gy()
 il=tara()
 for i in il:
  id=tid(i)
  if id in g:continue
  g.append(id)
  fi=i["fi"]
  if fi<MIN or fi>MAX:continue
  p=int(fi*1.10)
  fark=p-fi
  yuz=round((fark/p)*100,1)
  if yuz>=ESIK:
   tg(f"🚨 <b>FIRSAT ARAÇ!</b>\n🚗 {i['b']}\n📉 İlan: {i['f']}\n📊 Piyasa: {p:,} TL\n🎯 Kâr: {fark:,} TL (%{yuz})\n🔗 <a href='{i['l']}'>İlana Git</a>")
 gk(g)
 print("Tarama bitti")
schedule.every(15).minutes.do(main)
main()
while True:schedule.run_pending();time.sleep(60)
