import os
from dotenv import load_dotenv

# Noktasız env dosyasını yükle
load_dotenv("env")

class Config:
    """Antigravity Sistemi İçin Tam Konfigürasyon"""
    
    # MongoDB Bağlantısı
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = "antigravity_db"
    USERS_COLLECTION = "users"
    INVENTORY_COLLECTION = "inventory"

    # AI Analiz Ayarları (Hata Veren Kısımlar Burasıydı)
    CRITICAL_DAYS_THRESHOLD = 3
    WARNING_DAYS_THRESHOLD = 7
    OVERSTOCK_MULTIPLIER = 3.0
    SAFETY_STOCK_MULTIPLIER = 1.5

    # Mesajlar
    MESSAGES = {
        "boot": "🚀 Antigravity systems initializing...",
        "connected": "🛰️ Ground control connected — MongoDB Atlas online.",
        "error": "💥 System anomaly detected: {error}",
        "divider": "─" * 55,
    }