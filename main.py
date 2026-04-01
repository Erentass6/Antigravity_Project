import os
import hashlib
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Konfigürasyon ve env Yükleme
load_dotenv("env")
MONGO_URI = os.getenv("MONGO_URI")

# 2. MongoDB Bağlantısı
try:
    client = MongoClient(MONGO_URI)
    db = client["antigravity_db"]
    users_coll = db["users"]
    inv_coll = db["inventory"]
    client.admin.command('ping')
    print("🛰️ Ground control connected — MongoDB Atlas online.")
except Exception as e:
    print(f"💥 Bağlantı Hatası: {e}")
    exit()

# 3. Ana Fonksiyonlar
current_user = None

def main():
    global current_user
    while True:
        print("\n" + "="*45)
        print("   ANTIGRAVITY: ZERO-G INVENTORY SYSTEM")
        print("="*45)
        
        if not current_user:
            print("1. Giriş Yap\n2. Kayıt Ol\n3. Çıkış")
            secim = input("\nSeçiminiz: ")
            
            if secim == "1":
                u = input("Kullanıcı Adı: ")
                p = hashlib.sha256(input("Şifre: ").encode()).hexdigest()
                user = users_coll.find_one({"username": u, "password": p})
                if user:
                    current_user = u
                    print(f"✅ Hoş geldin Komutan {u}!")
                else:
                    print("❌ Hatalı giriş!")
            elif secim == "2":
                u = input("Yeni Kullanıcı Adı: ")
                p = hashlib.sha256(input("Yeni Şifre: ").encode()).hexdigest()
                if users_coll.find_one({"username": u}):
                    print("⚠️ Bu kullanıcı zaten var!")
                else:
                    users_coll.insert_one({"username": u, "password": p})
                    print("🚀 Kayıt başarılı! Giriş yapabilirsiniz.")
            elif secim == "3": break
        else:
            print(f"--- 👨‍🚀 Komutan: {current_user} ---")
            print("1. Ürün Ekle\n2. Stokları Listele\n3. AI Analizi\n4. Çıkış Yap")
            secim = input("\nSeçiminiz: ")
            
            if secim == "1":
                n = input("Ürün Adı: ")
                q = int(input("Adet: "))
                price = float(input("Birim Fiyat: "))
                inv_coll.insert_one({"name": n, "quantity": q, "price": price, "owner": current_user})
                print("📦 Ürün başarıyla eklendi!")
            elif secim == "2":
                items = list(inv_coll.find())
                print("\n📋 GÜNCEL STOK LİSTESİ:")
                for i in items:
                    print(f"- {i['name']}: {i['quantity']} adet | {i['price']} TL")
            elif secim == "3":
                items = list(inv_coll.find())
                print("\n🤖 AI DANIŞMAN RAPORU:")
                if not items: print("🔭 Stokta ürün yok.")
                for i in items:
                    durum = "🔴 KRİTİK" if i['quantity'] < 5 else "🟢 STABİL"
                    print(f"{durum}: {i['name']} ({i['quantity']} adet)")
            elif secim == "4":
                current_user = None

if __name__ == "__main__":
    main()