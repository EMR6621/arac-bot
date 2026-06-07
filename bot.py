import requests,json,hashlib,os,schedule,time,re
from datetime import datetime
import xml.etree.ElementTree as ET

TOKEN="8915757374:AAH9dsLY8pcv82wBuzhVZyzGrH-rK2IsTNg"
CHAT="1334416527"
MIN=100000
MAX=3000000
MAX_KM=250000
MIN_YIL=2010
MIN_ESIK=5
MAX_ESIK=25
ARALIK=5
F="gorulmus.json"
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def gy():
 return json.load(open(F)) if os.path.exists(F) else []

def gk(l):
 json.dump(l[-2000:],open(F,"w"))

def tid(url):
 return hashlib.md5(url.encode()).hexdigest()

def tg(m):
 try:requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT,"text":m,"parse_mode":"HTML"},timeout=10)
 except:pass

def fp(s):
 try:return int(re.sub(r'[^\d]','',str(s).replace("TL","").strip()))
 except:return 0

def sahibinden_rss():
 il=[]
 try:
  url=f"https://www.sahibinden.com/otomobil?pagingSize=50&minPrice={MIN}&maxPrice={MAX}&sorting=date_desc&output=rss"
  r=requests.get(url,headers=H,timeout=15)
  root=ET.fromstring(r.content)
  for item in root.findall('.//item'):
   try:
    baslik=item.find('title').text or ""
    link=item.find('link').text or ""
    desc=item.find('description').text or ""
    fiyat=fp(re.search(r'[\d\.]+\s*TL',desc).group() if re.search(r'[\d\.]+\s*TL',desc) else "0")
    km_m=re.search(r'([\d\.]+)\s*[Kk][Mm]',desc)
    km=fp(km_m.group(1)) if km_m else 0
    yil_m=re.search(r'(20[0-9]{2}|19[0-9]{2})',baslik)
    yil=int(yil_m.group(1)) if yil_m else 0
    if fiyat>0:il.append({"b":baslik,"l":link,"f":fiyat,"km":km,"yil":yil})
   except:pass
  print(f"  Sahibinden RSS: {len(il)} ilan")
 except Exception as e:print(f"  RSS hata: {e}")
 return il

def piyasa_degeri(ilan,tumilan):
 benzer=[x for x in tumilan if x["f"]>0 and abs(x["f"]-ilan["f"])/max(ilan["f"],1)<0.3]
 if len(benzer)<3:return ilan["f"]*1.10
 return sum(x["f"] for x in benzer)/len(benzer)

def main():
 print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tarama basladi...")
 g=gy()
 ilanlar=sahibinden_rss()
 yeni=0
 for i in ilanlar:
  iid=tid(i["l"])
  if iid in g:continue
  g.append(iid)
  fi=i["f"]
  if fi<MIN or fi>MAX:continue
  if i["km"]>=MAX_KM and i["km"]>0:continue
  if i["yil"]>0 and i["yil"]<MIN_YIL:continue
  piyasa=piyasa_degeri(i,ilanlar)
  fark=piyasa-fi
  yuz=round((fark/piyasa)*100,1)
  if MIN_ESIK<=yuz<=MAX_ESIK:
   yeni+=1
   tg(f"🚨 <b>YENİ FIRSAT ARAÇ DÜŞTÜ!</b>\n\n🚗 <b>Araç:</b> {i['b']}\n📍 <b>Km:</b> {i['km']:,} KM\n💰 <b>İlan Fiyatı:</b> {fi:,} TL\n📊 <b>Piyasa Değeri:</b> {int(piyasa):,} TL\n🎯 <b>Net Kâr Potansiyeli:</b> {int(fark):,} TL (%{yuz} Altında)\n🔗 <a href='{i['l']}'>İlana Gitmek İçin Tıklayın</a>")
   time.sleep(1)
 gk(g)
 print(f"  {len(ilanlar)} ilan, {yeni} fırsat bulundu.")

schedule.every(ARALIK).minutes.do(main)
main()
while True:schedule.run_pending();time.sleep(60)
