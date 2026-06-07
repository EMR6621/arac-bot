import requests,json,hashlib,os,schedule,time,re
from datetime import datetime

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
H={
 "User-Agent":"sahibinden/6.30.0 (iPhone; iOS 16.0)",
 "Accept":"application/json",
 "Accept-Language":"tr-TR",
 "x-device-id":"abc123def456",
}

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
 try:return int(re.sub(r'[^\d]','',str(s).strip()))
 except:return 0

def sahibinden():
 il=[]
 try:
  url=f"https://api.sahibinden.com/v1/classifieds/search?category=15&minPrice={MIN}&maxPrice={MAX}&pagingSize=50&sortField=date&sortOrder=desc"
  r=requests.get(url,headers=H,timeout=15)
  data=r.json()
  ilanlar=data.get("classifieds",data.get("data",data.get("results",[])))
  for x in ilanlar:
   try:
    baslik=x.get("title","")
    link="https://www.sahibinden.com/ilan/"+str(x.get("id",""))
    fiyat=fp(x.get("price","0"))
    km=fp(x.get("km",x.get("mileage","0")))
    yil=fp(x.get("year","0"))
    if fiyat>0:il.append({"b":baslik,"l":link,"f":fiyat,"km":km,"yil":yil})
   except:pass
  print(f"  Sahibinden: {len(il)} ilan")
 except Exception as e:print(f"  Sahibinden hata: {e}")
 return il

def arabam():
 il=[]
 try:
  url=f"https://apigateway.arabam.com/v4/listing?take=50&skip=0&minPrice={MIN}&maxPrice={MAX}&sort=dateDesc&categoryId=1"
  r=requests.get(url,headers={"User-Agent":"arabam/9.0 (iPhone; iOS 16.0)","Accept":"application/json"},timeout=15)
  data=r.json()
  ilanlar=data.get("data",data.get("items",data.get("listings",[])))
  for x in ilanlar:
   try:
    baslik=x.get("title","")
    link="https://www.arabam.com"+x.get("url","/"+str(x.get("id","")))
    fiyat=fp(x.get("price","0"))
    km=fp(x.get("km",x.get("mileage","0")))
    yil=fp(x.get("year","0"))
    if fiyat>0:il.append({"b":baslik,"l":link,"f":fiyat,"km":km,"yil":yil})
   except:pass
  print(f"  Arabam.com: {len(il)} ilan")
 except Exception as e:print(f"  Arabam hata: {e}")
 return il

def piyasa(ilan,tumilan):
 benzer=[x for x in tumilan if x["f"]>0 and abs(x["f"]-ilan["f"])/max(ilan["f"],1)<0.3]
 if len(benzer)<3:return ilan["f"]*1.10
 return sum(x["f"] for x in benzer)/len(benzer)

def main():
 print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tarama basladi...")
 g=gy()
 ilanlar=sahibinden()+arabam()
 yeni=0
 for i in ilanlar:
  iid=tid(i["l"])
  if iid in g:continue
  g.append(iid)
  fi=i["f"]
  if fi<MIN or fi>MAX:continue
  if i["km"]>=MAX_KM and i["km"]>0:continue
  if i["yil"]>0 and i["yil"]<MIN_YIL:continue
  p=piyasa(i,ilanlar)
  fark=p-fi
  yuz=round((fark/p)*100,1)
  if MIN_ESIK<=yuz<=MAX_ESIK:
   yeni+=1
   tg(f"🚨 <b>YENİ FIRSAT ARAÇ DÜŞTÜ!</b>\n\n🚗 <b>Araç:</b> {i['b']}\n📍 <b>Km:</b> {i['km']:,} KM\n💰 <b>İlan Fiyatı:</b> {fi:,} TL\n📊 <b>Piyasa Değeri:</b> {int(p):,} TL\n🎯 <b>Kâr Potansiyeli:</b> {int(fark):,} TL (%{yuz} Altında)\n🔗 <a href='{i['l']}'>İlana Gitmek İçin Tıklayın</a>")
   time.sleep(1)
 gk(g)
 print(f"  {len(ilanlar)} ilan, {yeni} fırsat bulundu.")

schedule.every(ARALIK).minutes.do(main)
main()
while True:schedule.run_pending();time.sleep(60)
