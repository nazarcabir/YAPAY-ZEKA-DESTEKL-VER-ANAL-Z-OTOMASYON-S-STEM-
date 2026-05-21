# ============================================================================
# model.py — Makine Öğrenmesi Modeli (Araç Yakıt Tüketim Tahmini)
# ============================================================================
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import RandomForestRegressor
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost bulunamadı, Random Forest kullanılacak.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "fuel.csv")
MODEL_PATH = os.path.join(BASE_DIR, "yakit_modeli.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "label_encoders.pkl")


def mpg_to_l100km(mpg: float) -> float:
    if mpg <= 0:
        return np.nan
    return 235.215 / mpg


def veri_yukle_ve_temizle() -> pd.DataFrame:
    print("📂 Veri seti yükleniyor...")
    df = pd.read_csv(CSV_PATH, low_memory=False)

    gerekli_sutunlar = [
        "make", "model", "engine_displacement", "engine_cylinders",
        "fuel_type", "transmission", "combined_mpg_ft1", "year", "drive"
    ]

    mevcut = [col for col in gerekli_sutunlar if col in df.columns]
    df = df[mevcut].copy()

    df = df[df["combined_mpg_ft1"].notna()]
    df = df[df["combined_mpg_ft1"] > 0]

    df = df.dropna(subset=["engine_displacement", "engine_cylinders"])
    df = df[df["engine_displacement"] > 0]
    df = df[df["engine_cylinders"] > 0]

    df["tuketim_l100km"] = df["combined_mpg_ft1"].apply(mpg_to_l100km)
    df = df.dropna(subset=["tuketim_l100km"])

    for col in ["make", "model", "fuel_type", "transmission", "drive"]:
        if col in df.columns:
            df[col] = df[col].fillna("Bilinmiyor")

    return df


def vites_tipi_basitlestir(transmission_str: str) -> str:
    t = str(transmission_str).strip().lower()
    if t.startswith("automatic"):
        return "Otomatik"
    elif t.startswith("manual"):
        return "Manuel"
    else:
        return "Diğer"


def yakit_tipi_basitlestir(fuel_str: str) -> str:
    f = str(fuel_str).strip().lower()
    if "diesel" in f:
        return "Dizel"
    elif "premium" in f:
        return "Premium Benzin"
    elif "regular" in f or "gasoline" in f:
        return "Benzin"
    elif "e85" in f or "ethanol" in f:
        return "E85/Etanol"
    elif "natural" in f or "cng" in f:
        return "Doğalgaz"
    elif "electric" in f:
        return "Elektrik"
    else:
        return "Diğer"

def surus_tipi_basitlestir(drive_str: str) -> str:
    d = str(drive_str).strip().lower()
    if "4-wheel" in d or "all-wheel" in d or "4wd" in d or "awd" in d:
        return "4x4"
    elif "rear" in d or "rwd" in d:
        return "Arka Çeker"
    else:
        return "Ön Çeker"

def ozellik_muhendisligi(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vites_tipi"] = df["transmission"].apply(vites_tipi_basitlestir)
    df["yakit_tipi"] = df["fuel_type"].apply(yakit_tipi_basitlestir)
    df["hacim_silindir_orani"] = df["engine_displacement"] / df["engine_cylinders"]
    if "drive" in df.columns:
        df["surus_tipi"] = df["drive"].apply(surus_tipi_basitlestir)
    return df


def model_egit_ve_kaydet(force_retrain: bool = False):
    if not force_retrain and os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH):
        print("📦 Mevcut model yükleniyor...")
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODERS_PATH)
        return model, encoders, None

    df = veri_yukle_ve_temizle()
    df = ozellik_muhendisligi(df)

    df = df[df["yakit_tipi"] != "Elektrik"]

    ozellik_sutunlari = [
        "make", "model", "engine_displacement", "engine_cylinders",
        "vites_tipi", "yakit_tipi", "hacim_silindir_orani", "year"
    ]

    if "surus_tipi" in df.columns:
        ozellik_sutunlari.append("surus_tipi")

    hedef = "tuketim_l100km"

    encoders = {}
    kategorik_sutunlar = ["make", "model", "vites_tipi", "yakit_tipi"]
    if "surus_tipi" in df.columns:
        kategorik_sutunlar.append("surus_tipi")

    for col in kategorik_sutunlar:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    X = df[ozellik_sutunlari].values
    y = df[hedef].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("🔧 Model eğitiliyor...")
    if XGBOOST_AVAILABLE:
        model = XGBRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
    else:
        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    metrikler = {"MAE": round(mae, 3), "R²": round(r2, 4)}
    print(f"📊 Model Performansı → MAE: {mae:.3f} L/100km | R²: {r2:.4f}")

    joblib.dump(model, MODEL_PATH)
    joblib.dump({
        "encoders": encoders,
        "ozellik_sutunlari": ozellik_sutunlari,
        "kategorik_sutunlar": kategorik_sutunlar
    }, ENCODERS_PATH)
    print(f"💾 Model kaydedildi → {MODEL_PATH}")

    return model, encoders, metrikler


def tahmin_yap(model, encoder_bilgi: dict, kullanici_girdisi: dict) -> float:
    encoders = encoder_bilgi["encoders"]
    ozellik_sutunlari = encoder_bilgi["ozellik_sutunlari"]
    kategorik_sutunlar = encoder_bilgi["kategorik_sutunlar"]

    girdi_df = pd.DataFrame([kullanici_girdisi])
    girdi_df["hacim_silindir_orani"] = girdi_df["engine_displacement"] / girdi_df["engine_cylinders"]

    for col in kategorik_sutunlar:
        if col in girdi_df.columns and col in encoders:
            le = encoders[col]
            deger = str(girdi_df[col].iloc[0])
            if deger in le.classes_:
                girdi_df[col] = le.transform([deger])[0]
            else:
                girdi_df[col] = 0

    X_pred = girdi_df[ozellik_sutunlari].values
    tahmin = model.predict(X_pred)[0]

    return round(float(tahmin), 2)


def veri_seti_bilgileri() -> dict:
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df = df.dropna(subset=["engine_displacement", "engine_cylinders", "combined_mpg_ft1"])
    df = df[df["combined_mpg_ft1"] > 0]
    df = ozellik_muhendisligi(df)

    marka_modeller = df.groupby("make")["model"].unique().apply(lambda x: sorted(list(x))).to_dict()
    markalar = sorted(list(marka_modeller.keys()))

    yakit_tipleri = ["Benzin", "Dizel", "Premium Benzin", "E85/Etanol", "Doğalgaz", "Diğer"]
    vites_tipleri = ["Otomatik", "Manuel", "Diğer"]
    surus_tipleri = ["Ön Çeker", "Arka Çeker", "4x4"]

    return {
        "markalar": markalar,
        "marka_modeller": marka_modeller,
        "yakit_tipleri": yakit_tipleri,
        "vites_tipleri": vites_tipleri,
        "surus_tipleri": surus_tipleri,
    }

if __name__ == "__main__":
    model, encoders, metrikler = model_egit_ve_kaydet(force_retrain=True)
    if metrikler:
        print(f"\n{'='*50}")
        print(f"  MODEL EĞİTİM SONUÇLARI")
        print(f"{'='*50}")
        for k, v in metrikler.items():
            print(f"  {k}: {v}")
        print(f"{'='*50}")
