# ============================================================================
# data_fetcher.py — Dinamik Akaryakıt Fiyatı Çekme Modülü
# ============================================================================
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Güncel (Nisan 2026 gerçek) KDV Dahil Fiyatlar (TL/Litre)
YEDEK_FIYATLAR = {
    "Benzin": 64.71,
    "Dizel": 72.76,
    "LPG": 34.87,
    "Premium Benzin": 66.50,
    "E85/Etanol": 55.00,
    "Doğalgaz": 25.00,
    "Diğer": 65.00,
}

def guncel_fiyatlari_cek() -> dict:
    fiyatlar = None
    try:
        fiyatlar = _petrolofisi_cek()
        if fiyatlar:
            return {
                "fiyatlar": fiyatlar,
                "kaynak": "petrolofisi.com.tr",
                "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
    except Exception as e:
        print(f"⚠️ petrolofisi.com.tr hatası: {e}")

    try:
        fiyatlar = _benzinfiyatlari_com_cek()
        if fiyatlar:
            return {
                "fiyatlar": fiyatlar,
                "kaynak": "benzinfiyatlari.com",
                "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
    except Exception as e:
        print(f"⚠️ benzinfiyatlari.com hatası: {e}")

    print("📌 Yedek fiyatlar kullanılıyor.")
    return {
        "fiyatlar": YEDEK_FIYATLAR.copy(),
        "kaynak": "Güncel Fiyatlar (Varsayılan)",
        "tarih": datetime.now().strftime("%d.%m.%Y")
    }

def _benzinfiyatlari_com_cek() -> dict | None:
    url = "https://www.benzinfiyatlari.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    fiyatlar = {}
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            isim = cells[0].get_text(strip=True).lower()
            fiyat_text = cells[1].get_text(strip=True)
            try:
                fiyat = float(fiyat_text.replace(",", ".").replace("₺", "").strip())
            except:
                continue
            if "kurşunsuz" in isim or "benzin" in isim:
                fiyatlar["Benzin"] = fiyat
            elif "motorin" in isim or "dizel" in isim:
                fiyatlar["Dizel"] = fiyat
            elif "lpg" in isim or "otogaz" in isim:
                fiyatlar["LPG"] = fiyat

    if len(fiyatlar) >= 2:
        for tip, yedek_fiyat in YEDEK_FIYATLAR.items():
            if tip not in fiyatlar:
                fiyatlar[tip] = yedek_fiyat
        return fiyatlar
    return None

def _petrolofisi_cek() -> dict | None:
    url = "https://www.petrolofisi.com.tr/akaryakit-fiyatlari"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    fiyatlar = {}
    price_elements = soup.find_all(class_=lambda c: c and "price" in c.lower()) if soup else []
    for el in price_elements:
        text = el.get_text(strip=True)
        try:
            fiyat = float(text.replace(",", ".").replace("₺", "").replace("TL", "").strip())
            if 20 < fiyat < 60:
                if not fiyatlar.get("Benzin"):
                    fiyatlar["Benzin"] = fiyat
                elif not fiyatlar.get("Dizel"):
                    fiyatlar["Dizel"] = fiyat
                elif not fiyatlar.get("LPG"):
                    fiyatlar["LPG"] = fiyat
        except:
            continue
    if len(fiyatlar) >= 2:
        for tip, yedek_fiyat in YEDEK_FIYATLAR.items():
            if tip not in fiyatlar:
                fiyatlar[tip] = yedek_fiyat
        return fiyatlar
    return None

def yakit_fiyati_al(yakit_tipi: str, fiyat_bilgisi: dict) -> float:
    fiyatlar = fiyat_bilgisi.get("fiyatlar", YEDEK_FIYATLAR)
    if yakit_tipi in fiyatlar:
        return fiyatlar[yakit_tipi]
    eslestirme = {
        "Benzin": ["Benzin", "Regular Gasoline", "Premium Benzin"],
        "Dizel": ["Dizel", "Diesel"],
        "LPG": ["LPG"],
        "Premium Benzin": ["Premium Benzin", "Premium Gasoline"],
        "E85/Etanol": ["E85/Etanol"],
        "Doğalgaz": ["Doğalgaz", "CNG"],
    }
    for kategori, alternatifler in eslestirme.items():
        if yakit_tipi in alternatifler and kategori in fiyatlar:
            return fiyatlar[kategori]
    return fiyatlar.get("Benzin", YEDEK_FIYATLAR["Benzin"])
