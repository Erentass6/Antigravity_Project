"""
╔══════════════════════════════════════════════════════════╗
║       ANTIGRAVITY: ZERO-G INVENTORY — Web Engine        ║
║    "Lighten your logistics, elevate your efficiency."    ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import hashlib
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

load_dotenv("env")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── MongoDB Bağlantısı ──────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["antigravity_db"]
users_coll = db["users"]
inv_coll = db["inventory"]

# Indexleri güvenli şekilde kuralım
users_coll.create_index("username", unique=True)
# HATA VEREN INDEX BURADAN SİLİNDİ!

# ── Auth Yardımcıları ────────────────────────────────────────
def hash_password(password, salt):
    salted = "{}{}".format(salt, password).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# ── AI Analiz Motoru ────────────────────────────────────────
def analyze_product(product):
    name = product.get("product_name", "Bilinmiyor")
    stock = product.get("current_stock", 0)
    daily = product.get("daily_sales", 0)
    lead = product.get("lead_time_days", 0)
    
    days_left = stock / daily if daily > 0 else 999
    
    if days_left <= 3:
        status, icon, msg = "CRITICAL", "🔴", f"!! KRİTİK !! {name} stokları {days_left:.1f} gün içinde bitiyor!"
    elif days_left <= 7:
        status, icon, msg = "WARNING", "🟡", f"UYARI: {name} için sipariş vakti yaklaşıyor."
    else:
        status, icon, msg = "HEALTHY", "🟢", f"{name} stok durumu stabil. Yörünge normal."

    return {"product_name": name, "status": status, "icon": icon, "message": msg, "current_stock": stock}

# ── Sayfa Yönlendirmeleri ────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("dashboard")) if "username" in session else redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    user = users_coll.find_one({"username": data.get("username")})
    if user and hash_password(data.get("password"), user.get("salt")) == user.get("password_hash"):
        session["username"] = data.get("username")
        return jsonify({"ok": True, "msg": "Sisteme giriş yapıldı, Komutan!"})
    return jsonify({"ok": False, "msg": "Erişim reddedildi!"}), 401

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    salt = os.urandom(32).hex()
    try:
        users_coll.insert_one({
            "username": data.get("username"),
            "password_hash": hash_password(data.get("password"), salt),
            "salt": salt,
            "created_at": datetime.now(timezone.utc)
        })
        return jsonify({"ok": True, "msg": "Kayıt başarılı."})
    except DuplicateKeyError:
        return jsonify({"ok": False, "msg": "Bu kullanıcı zaten var."})

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html", username=session["username"])

@app.route("/api/products", methods=["GET", "POST"])
@login_required
def handle_products():
    if request.method == "POST":
        data = request.get_json()
        inv_coll.insert_one({
            "product_code": data["product_code"],
            "product_name": data["product_name"],
            "current_stock": int(data["current_stock"]),
            "daily_sales": float(data["daily_sales"]),
            "lead_time_days": int(data["lead_time_days"]),
            "unit_price": float(data["unit_price"]),
            "added_by": session["username"]
        })
        return jsonify({"ok": True})
    return jsonify(list(inv_coll.find({}, {"_id": 0})))

@app.route("/api/ai-scan")
@login_required
def ai_scan():
    products = list(inv_coll.find())
    report = {"analyses": [analyze_product(p) for p in products], "total": len(products)}
    return jsonify({"ok": True, "report": report})

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login_page"))

# 🚀 MOTORU 5001 PORTUNDA ÇALIŞTIR
if __name__ == "__main__":
    print("🛰️  Antigravity Web Engine 5001 portunda ateşleniyor...")
    app.run(debug=True, host="0.0.0.0", port=5001)