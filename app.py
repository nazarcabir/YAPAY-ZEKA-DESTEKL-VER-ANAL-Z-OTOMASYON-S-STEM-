import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import sys

# Proje dizinini (araç yakıt projesi) sisteme ekleyelim ki map_utils'i içe aktarabilelim
# Eğer app.py masaüstündeyse, araç yakıt projesi klasörü altındadır.
proje_yolu = os.path.join(os.path.dirname(__file__), 'araç yakıt projesi')
if proje_yolu not in sys.path:
    sys.path.append(proje_yolu)

try:
    from map_utils import sehir_koordinati_bul, harita_olustur
except ImportError:
    # Eğer bulamazsa basit bir sözlük tanımlayalım
    def sehir_koordinati_bul(sehir):
        sehirler = {
            "bitis": (38.3938, 42.1232), "van": (38.4891, 43.3832),
            "istanbul": (41.0082, 28.9784), "ankara": (39.9334, 32.8597),
            "izmir": (38.4192, 27.1287), "antalya": (36.8969, 30.7133)
        }
        return sehirler.get(str(sehir).strip().lower(), (39.0, 35.0))
        
    def harita_olustur(b, v):
        return None, None

# ============================================================================
# 1. SAYFA AYARLARI VE CSS
# ============================================================================
st.set_page_config(page_title="Araç Yakıt Analizi", page_icon="🚗", layout="wide")

dark_mode = st.sidebar.toggle("🌙 Karanlık Mod", value=True)

if dark_mode:
    bg_color = "#0b0f19"
    bg_rgba = "rgba(11, 15, 25, 0.92)"
    text_color = "#e0e0e0"
    card_bg = "#1a2235"
    card_border = "#00ffcc"
    card_shadow = "0 4px 20px rgba(0, 255, 204, 0.15)"
    border_glow = "0 0 20px rgba(0, 255, 204, 0.2)"
    neon_color = "#00ffcc"
    button_grad = "linear-gradient(90deg, #00ffcc 0%, #0099ff 100%)"
    btn_text = "#0b0f19"
    map_shadow = "0px 0px 15px rgba(0, 255, 255, 0.4)"
    input_bg = "#1a2235"
    input_border = "#2a3b5c"
    sidebar_border = "none"
else:
    bg_color = "#f4f6f9"
    bg_rgba = "rgba(244, 246, 249, 0.92)"
    text_color = "#333333"
    card_bg = "#ffffff"
    card_border = "#e0e0e0"
    card_shadow = "0 4px 10px rgba(0, 0, 0, 0.05)"
    border_glow = "none"
    neon_color = "#0284c7"
    button_grad = "linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%)"
    btn_text = "#ffffff"
    map_shadow = "0px 4px 10px rgba(0, 0, 0, 0.1)"
    input_bg = "#f8f9fa"
    input_border = "#cccccc"
    sidebar_border = "1px solid #e0e0e0"
import base64
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

img_path = os.path.join(proje_yolu, 'image_8aae97.jpg')
bg_base64 = get_base64_of_bin_file(img_path)

if bg_base64:
    app_bg_css = f"""
        background-color: {bg_color} !important;
        background-image: linear-gradient({bg_rgba}, {bg_rgba}), url("data:image/jpeg;base64,{bg_base64}") !important;
        background-size: cover !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        background-position: center !important;
    """
else:
    app_bg_css = f"background-color: {bg_color} !important;"

st.markdown(f"""
<style>
    /* Temel Mod Arka Plan ve Metin Renkleri */
    .stApp, [data-testid="stAppViewContainer"], section[data-testid="stSidebar"] {{
        {app_bg_css}
    }}
    [data-testid="stSidebar"] {{
        background-color: {bg_color} !important;
        border-right: {sidebar_border} !important;
    }}
    
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp span,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: {text_color} !important;
    }}
    
    /* Widget (Input) Renkleri */
    div[data-baseweb="select"] > div, input[type="text"], input[type="number"], div[role="radiogroup"],
    [data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] input {{
        background-color: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px;
    }}
    div[data-baseweb="select"] span, [data-testid="stSidebar"] div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}
    
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div.stButton > button, div.stButton > button span {{
        color: inherit !important;
    }}
    
    /* Ana Sütunları (Yolculuk / Harita) Kart Gibi Yapma */
    div[data-testid="column"] {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 15px;
        padding: 20px;
        box-shadow: {card_shadow};
        margin-bottom: 20px;
    }}
    
    /* Fütüristik Başlık */
    .main-title {{
        text-align: center;
        background: {button_grad};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-shadow: {border_glow};
    }}
    
    /* Özel st.metric (Dashboard Kartları) */
    div[data-testid="metric-container"] {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 12px;
        padding: 15px;
        box-shadow: {card_shadow};
        transition: all 0.3s ease;
    }}
    div[data-testid="metric-container"]:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }}
    
    label[data-testid="stMetricLabel"] {{
        color: {neon_color} !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        color: {text_color} !important;
        font-weight: 800 !important;
    }}
    
    /* Fütüristik Butonlar */
    div.stButton > button {{
        background: {button_grad} !important;
        color: {btn_text} !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button:hover {{
        opacity: 0.9 !important;
        transform: translateY(-2px) !important;
        box-shadow: {card_shadow} !important;
    }}
    
    /* Google Haritalar Butonu */
    .google-btn {{
        display: inline-block;
        padding: 12px 20px;
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 100%);
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.3);
        transition: all 0.3s ease;
    }}
    .google-btn:hover {{
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.6);
        transform: translateY(-2px);
    }}
    
    /* Harita Çerçevesi (iframe) */
    iframe[title="streamlit_folium.st_folium"] {{
        border-radius: 15px;
        box-shadow: {map_shadow};
        border: 1px solid {card_border};
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; font-size: 3rem;">⛽🛣️ <span class="main-title">Dinamik Yakıt ve Rota Analizi</span></h1>', unsafe_allow_html=True)

# ============================================================================
# TÜRKİYE ARAÇ HAVUZU
# ============================================================================
TR_ARACLAR = [
    # --- FIAT ---
    {"make": "FIAT", "model": "Egea", "enginesize": 1.3, "fueltype": "Dizel", "l_100km": 4.2, "is_tr": True},
    {"make": "FIAT", "model": "Egea", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 4.7, "is_tr": True},
    {"make": "FIAT", "model": "Egea", "enginesize": 1.4, "fueltype": "Benzin", "l_100km": 6.8, "is_tr": True},
    {"make": "FIAT", "model": "Egea Cross", "enginesize": 1.4, "fueltype": "Benzin", "l_100km": 7.0, "is_tr": True},
    {"make": "FIAT", "model": "Egea Cross", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 4.8, "is_tr": True},
    {"make": "FIAT", "model": "Linea", "enginesize": 1.3, "fueltype": "Dizel", "l_100km": 4.9, "is_tr": True},
    {"make": "FIAT", "model": "Doblo", "enginesize": 1.3, "fueltype": "Dizel", "l_100km": 5.2, "is_tr": True},
    {"make": "FIAT", "model": "Doblo", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 5.8, "is_tr": True},
    {"make": "FIAT", "model": "Fiorino", "enginesize": 1.3, "fueltype": "Dizel", "l_100km": 4.5, "is_tr": True},
    {"make": "FIAT", "model": "Panda", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 4.8, "is_tr": True},
    {"make": "FIAT", "model": "500", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 4.6, "is_tr": True},

    # --- RENAULT ---
    {"make": "RENAULT", "model": "Megane IV", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.4, "is_tr": True},
    {"make": "RENAULT", "model": "Megane IV", "enginesize": 1.3, "fueltype": "Benzin", "l_100km": 5.9, "is_tr": True},
    {"make": "RENAULT", "model": "Megane IV", "enginesize": 1.2, "fueltype": "Benzin", "l_100km": 5.7, "is_tr": True},
    {"make": "RENAULT", "model": "Megane Sedan", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.5, "is_tr": True},
    {"make": "RENAULT", "model": "Megane Sedan", "enginesize": 1.3, "fueltype": "Benzin", "l_100km": 6.0, "is_tr": True},
    {"make": "RENAULT", "model": "Megane III", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.7, "is_tr": True},
    {"make": "RENAULT", "model": "Clio", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 5.2, "is_tr": True},
    {"make": "RENAULT", "model": "Clio", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 3.9, "is_tr": True},
    {"make": "RENAULT", "model": "Fluence", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.6, "is_tr": True},
    {"make": "RENAULT", "model": "Captur", "enginesize": 1.3, "fueltype": "Benzin", "l_100km": 6.1, "is_tr": True},
    {"make": "RENAULT", "model": "Austral", "enginesize": 1.2, "fueltype": "Benzin", "l_100km": 5.4, "is_tr": True},
    {"make": "RENAULT", "model": "Taliant", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 5.6, "is_tr": True},

    # --- VOLKSWAGEN ---
    {"make": "VOLKSWAGEN", "model": "Golf", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 5.1, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Golf", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 5.3, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Golf", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 4.2, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Passat", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 5.8, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Passat", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 4.6, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Polo", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 4.9, "is_tr": True},
    {"make": "VOLKSWAGEN", "model": "Tiguan", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 6.8, "is_tr": True},

    # --- TOYOTA ---
    {"make": "TOYOTA", "model": "Corolla", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 5.8, "is_tr": True},
    {"make": "TOYOTA", "model": "Corolla", "enginesize": 1.8, "fueltype": "Benzin", "l_100km": 4.0, "is_tr": True},
    {"make": "TOYOTA", "model": "Yaris", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 3.8, "is_tr": True},
    {"make": "TOYOTA", "model": "C-HR", "enginesize": 1.8, "fueltype": "Benzin", "l_100km": 3.9, "is_tr": True},

    # --- FORD ---
    {"make": "FORD", "model": "Focus", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 5.2, "is_tr": True},
    {"make": "FORD", "model": "Focus", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.4, "is_tr": True},
    {"make": "FORD", "model": "Fiesta", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 4.8, "is_tr": True},
    {"make": "FORD", "model": "Courier", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 5.0, "is_tr": True},

    # --- HYUNDAI ---
    {"make": "HYUNDAI", "model": "i20", "enginesize": 1.4, "fueltype": "Benzin", "l_100km": 6.2, "is_tr": True},
    {"make": "HYUNDAI", "model": "Tucson", "enginesize": 1.6, "fueltype": "Dizel", "l_100km": 5.7, "is_tr": True},
    {"make": "HYUNDAI", "model": "Bayon", "enginesize": 1.4, "fueltype": "Benzin", "l_100km": 6.4, "is_tr": True},

    # --- HONDA ---
    {"make": "HONDA", "model": "Civic", "enginesize": 1.6, "fueltype": "Benzin", "l_100km": 6.7, "is_tr": True},
    {"make": "HONDA", "model": "Civic", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 6.2, "is_tr": True},

    # --- DACIA ---
    {"make": "DACIA", "model": "Duster", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.9, "is_tr": True},
    {"make": "DACIA", "model": "Sandero", "enginesize": 1.0, "fueltype": "Benzin", "l_100km": 5.1, "is_tr": True},

    # --- PEUGEOT ---
    {"make": "PEUGEOT", "model": "2008", "enginesize": 1.2, "fueltype": "Benzin", "l_100km": 5.2, "is_tr": True},
    {"make": "PEUGEOT", "model": "3008", "enginesize": 1.5, "fueltype": "Dizel", "l_100km": 4.5, "is_tr": True},

    # --- OPEL ---
    {"make": "OPEL", "model": "Corsa", "enginesize": 1.2, "fueltype": "Benzin", "l_100km": 4.5, "is_tr": True},
    {"make": "OPEL", "model": "Astra", "enginesize": 1.2, "fueltype": "Benzin", "l_100km": 5.4, "is_tr": True},

    # --- AUDI ---
    {"make": "AUDI", "model": "A3", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 5.2, "is_tr": True},
    {"make": "AUDI", "model": "A4", "enginesize": 2.0, "fueltype": "Dizel", "l_100km": 5.1, "is_tr": True},

    # --- BMW ---
    {"make": "BMW", "model": "320i", "enginesize": 1.6, "fueltype": "Benzin", "l_100km": 7.3, "is_tr": True},
    {"make": "BMW", "model": "520d", "enginesize": 2.0, "fueltype": "Dizel", "l_100km": 5.6, "is_tr": True},

    # --- MERCEDES-BENZ ---
    {"make": "MERCEDES-BENZ", "model": "C 200", "enginesize": 1.5, "fueltype": "Benzin", "l_100km": 6.8, "is_tr": True},
    {"make": "MERCEDES-BENZ", "model": "E 220 d", "enginesize": 2.0, "fueltype": "Dizel", "l_100km": 5.3, "is_tr": True},
]

# ============================================================================
# 2. VERİ YÜKLEME
# ============================================================================
@st.cache_data(show_spinner="Veriler yükleniyor, lütfen bekleyin...")
def veri_yukle_ve_birlestir():
    olasi_yollar = [
        'fuel.csv',
        r'C:\Users\furkan\OneDrive\Desktop\araç yakıt projesi\fuel.csv',
        os.path.join('araç yakıt projesi', 'fuel.csv')
    ]
    
    dosya_adi = None
    for yol in olasi_yollar:
        if os.path.exists(yol):
            dosya_adi = yol
            break
            
    df_ana = pd.DataFrame()
    if dosya_adi:
        df_ana = pd.read_csv(dosya_adi, low_memory=False)
        df_ana.columns = df_ana.columns.str.lower()
        
        df_ana = df_ana.rename(columns={
            'fuel_type': 'fueltype',
            'combined_mpg_ft1': 'mpg',
            'engine_displacement': 'enginesize'
        })
        
        for col in ['model', 'transmission', 'fueltype', 'make']:
            if col in df_ana.columns:
                df_ana[col] = df_ana[col].astype(str).str.strip()
                
        if 'mpg' in df_ana.columns:
            df_ana['mpg'] = pd.to_numeric(df_ana['mpg'], errors='coerce')
            df_ana['l_100km'] = df_ana['mpg'].apply(lambda x: 235.215 / x if pd.notnull(x) and x > 0 else None)
            
        df_ana['is_tr'] = False
    
    df_tr = pd.DataFrame(TR_ARACLAR)
    
    if not df_ana.empty:
        if 'model' in df_ana.columns:
            df_ana = df_ana[~df_ana['model'].str.lower().str.contains('unclean|quattro|20v', na=False)]
        df_kombine = pd.concat([df_tr, df_ana], ignore_index=True)
    else:
        df_kombine = df_tr
        
    df_kombine.columns = df_kombine.columns.str.strip().str.lower()
    df_kombine['make'] = df_kombine['make'].str.upper()
    return df_kombine

@st.cache_data
def akaryakit_istasyonlari_bul(min_lat, min_lng, max_lat, max_lng):
    import requests
    try:
        url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:10];
        node["amenity"="fuel"]({min_lat},{min_lng},{max_lat},{max_lng});
        out body;
        """
        res = requests.get(url, params={'data': query}, timeout=5)
        if res.status_code == 200:
            return res.json().get("elements", [])
    except:
        pass
    return []

# ============================================================================
# 3. ARAYÜZ MANTIĞI
# ============================================================================
df = veri_yukle_ve_birlestir()

if df.empty:
    st.error("⚠️ Veri seti oluşturulamadı.")
else:
    st.sidebar.markdown("## 🔧 Araç Özellikleri")
    
    if 'clear_counter' not in st.session_state:
        st.session_state.clear_counter = 0
    cc = st.session_state.clear_counter
    
    populer_markalar = sorted(df[df['is_tr'] == True]['make'].unique())
    diger_markalar = sorted(df[(df['is_tr'] != True) & (~df['make'].isin(populer_markalar))]['make'].dropna().unique())
    
    tum_markalar = [""] + populer_markalar + diger_markalar
    
    secilen_marka = st.sidebar.selectbox("🏷️ Marka Seçin", tum_markalar, key=f'marka_secim_{cc}', index=0)
    
    if secilen_marka != "":
        marka_df = df[df['make'] == secilen_marka]
        modeller = sorted(marka_df['model'].dropna().unique())
    else:
        modeller = []
    
    if len(modeller) > 0:
        modeller_opts = [""] + modeller
        secilen_model = st.sidebar.selectbox("🚘 Model Seçin", modeller_opts, key=f'model_secim_{cc}', index=0)
    else:
        if secilen_marka != "":
            st.sidebar.warning(f"{secilen_marka} markasına ait model bulunamadı.")
        secilen_model = None

    if secilen_model and secilen_model != "":
        model_df = marka_df[marka_df['model'] == secilen_model]
    else:
        model_df = pd.DataFrame()
    
    motor_secimi = None
    # 1.2'den 3.0'a kadar 0.1 artışla liste oluşturuyoruz
    sabit_motorlar = [round(x * 0.1, 1) for x in range(12, 31)]
    
    if secilen_model and secilen_model != "":
        motor_secimi = st.sidebar.selectbox("🔩 Motor Hacmi (Litre)", sabit_motorlar, key=f'motor_secim_{cc}', index=3) # Varsayılan 1.5
        arac_yili = st.sidebar.selectbox("📅 Araç Yılı", list(range(2026, 1989, -1)), index=11, key=f'yil_secim_{cc}') # Varsayılan 2015
        ortalama_hiz = st.sidebar.slider("🚀 Ortalama Hız (km/s)", 50, 160, 90, step=5, key=f'hiz_secim_{cc}')

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⛽ Yakıt Seçimi")
    
    yakit_fiyatlari = {"Benzin": 66.31, "Dizel": 74.47, "LPG": 35.51}
    yakit_tipleri = ["Benzin", "Dizel", "LPG", "Benzin + LPG"]
    yakit_tipi = st.sidebar.radio("Araç Yakıt Türü", yakit_tipleri, key=f'yakit_secim_{cc}', index=None)
    
    # Tümünü Temizle Butonu
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ TÜMÜNÜ TEMİZLE", use_container_width=True):
        st.session_state.clear_counter += 1
        st.session_state.baslangic_sehir = ""
        st.session_state.varis_sehir = ""
        st.session_state.click_state = 0
        st.session_state.last_processed_click = None
        st.rerun()
    
    if yakit_tipi:
        if yakit_tipi != "Benzin + LPG":
            guncel_fiyat = yakit_fiyatlari[yakit_tipi]
            st.sidebar.info(f"**Güncel {yakit_tipi} Fiyatı:** {guncel_fiyat} ₺/L")
        else:
            guncel_fiyat = 0 
            st.sidebar.info(f"**Güncel Fiyatlar:** Benzin {yakit_fiyatlari['Benzin']} ₺ | LPG {yakit_fiyatlari['LPG']} ₺")

    # Tüketim Hesaplama Mantığı
    ortalama_tuketim = 8.0
    if not model_df.empty:
        # 1. Baz Tüketimi Belirle
        tam_eslesme = model_df[model_df['enginesize'] == motor_secimi]
        if not tam_eslesme.empty:
            ortalama_tuketim = tam_eslesme['l_100km'].iloc[0]
        else:
            baz_veri = model_df.iloc[0]
            baz_tuketim = baz_veri['l_100km']
            baz_motor = baz_veri['enginesize']
            motor_farki = motor_secimi - baz_motor
            ortalama_tuketim = baz_tuketim * (1 + (motor_farki * 0.3)) 

        # 2. Hız Faktörü Uygula (90 km/s üzeri her 10 km/s için %8 artış)
        if ortalama_hiz > 90:
            hiz_etkisi = ((ortalama_hiz - 90) / 10) * 0.08
            ortalama_tuketim *= (1 + hiz_etkisi)
        elif ortalama_hiz < 60:
            ortalama_tuketim *= 1.10 # Çok düşük hızlarda verimsiz yanma

        # 3. Yıl (Yıpranma/Teknoloji) Faktörü Uygula
        if arac_yili < 2010:
            ortalama_tuketim *= 1.12 # %12 yıpranma payı
        elif arac_yili < 2015:
            ortalama_tuketim *= 1.06 # %6 yıpranma payı
        elif arac_yili >= 2020:
            ortalama_tuketim *= 0.97 # %3 yeni teknoloji tasarrufu

        if pd.isna(ortalama_tuketim):
            ortalama_tuketim = 8.0
            
    st.sidebar.markdown(f"<h3 style='text-align: center; color: #26D0CE;'>⛽ Tüketim: {round(ortalama_tuketim, 2)} L / 100km</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    if "baslangic_sehir" not in st.session_state:
        st.session_state["baslangic_sehir"] = ""
    if "varis_sehir" not in st.session_state:
        st.session_state["varis_sehir"] = ""

    with col1:
        st.markdown("### 📍 Yolculuk Detayları")
        
        try:
            from map_utils import sehir_listesi
            iller = [""] + sehir_listesi()
        except:
            iller = ["", "Ankara", "Bitlis", "İzmir", "Muş", "Van"]
            
        if st.session_state.get('baslangic_sehir') and st.session_state['baslangic_sehir'] not in iller:
            iller.append(st.session_state['baslangic_sehir'])
        if st.session_state.get('varis_sehir') and st.session_state['varis_sehir'] not in iller:
            iller.append(st.session_state['varis_sehir'])
            
        c_bas, c_bit = st.columns(2)
        with c_bas:
            baslangic = st.selectbox("Başlangıç Noktası", options=iller, key='baslangic_sehir')
        with c_bit:
            varis = st.selectbox("Varış Noktası", options=iller, key='varis_sehir')
            
        submit_rota = st.button("🗺️ ROTA ÇİZ VE MALİYET HESAPLA", use_container_width=True)
            
        # Eğer kullanıcı giriş yapmadıysa işlem yapma
        m = None
        rota_bilgi = None
        gercek_mesafe = 1.0
        
        koord_bas = None
        koord_bit = None
        if baslangic and varis:
            try:
                from map_utils import sehir_koordinati_bul
                koord_bas = sehir_koordinati_bul(baslangic)
                koord_bit = sehir_koordinati_bul(varis)
            except:
                pass
                
            try:
                from map_utils import harita_olustur
                m, rota_bilgi = harita_olustur(baslangic, varis)
                if rota_bilgi and "routes" in rota_bilgi and len(rota_bilgi["routes"]) > 0:
                    gercek_mesafe = round(float(rota_bilgi["routes"][0]["distance"]), 1)
                    
                if m and koord_bas and koord_bit:
                    min_lat = min(koord_bas[0], koord_bit[0]) - 0.02
                    max_lat = max(koord_bas[0], koord_bit[0]) + 0.02
                    min_lng = min(koord_bas[1], koord_bit[1]) - 0.02
                    max_lng = max(koord_bas[1], koord_bit[1]) + 0.02
                    
                    istasyonlar = akaryakit_istasyonlari_bul(min_lat, min_lng, max_lat, max_lng)
                    for ist in istasyonlar:
                        lat = ist.get("lat")
                        lon = ist.get("lon")
                        tags = ist.get("tags", {})
                        ad = tags.get("name", "Akaryakıt İstasyonu")
                        marka = tags.get("brand", "")
                        popup_text = f"{ad} ({marka})" if marka else ad
                        
                        if lat and lon:
                            folium.Marker(
                                [lat, lon],
                                popup=popup_text,
                                icon=folium.Icon(color='orange', icon='gas-pump', prefix='fa')
                            ).add_to(m)
            except:
                pass
        
        # Form dışındaki alan: Mesafe ince ayarı ve sonuçlar
        if baslangic and varis:
            mesafe = st.number_input("Mesafe Ayarı (km) - İnternetten Alındı, Değiştirebilirsiniz", 
                                     min_value=1.0, max_value=5000.0, value=gercek_mesafe, step=0.1, format="%.1f")
            
            # Dinamik Google Maps Linki (Birebir aynı konumu göstermesi için koordinatlarla)
            if koord_bas and koord_bit:
                google_maps_url = f"https://www.google.com/maps/dir/{koord_bas[0]},{koord_bas[1]}/{koord_bit[0]},{koord_bit[1]}"
            else:
                google_maps_url = f"https://www.google.com/maps/dir/{baslangic}/{varis}"
                
            st.markdown(f'<a href="{google_maps_url}" target="_blank" class="google-btn">🗺️ Google Haritalar\'da Aç</a>', unsafe_allow_html=True)
            
            # Hesaplama Sonuçları Dashboard
            toplam_yakit = (ortalama_tuketim / 100) * mesafe
            
            if yakit_tipi:
                if yakit_tipi == "Benzin + LPG":
                    benzin_yakit = toplam_yakit * 0.05
                    lpg_yakit = toplam_yakit * 0.95
                    toplam_maliyet = (benzin_yakit * yakit_fiyatlari["Benzin"]) + (lpg_yakit * yakit_fiyatlari["LPG"])
                else:
                    toplam_maliyet = toplam_yakit * guncel_fiyat
                
                st.markdown("---")
                st.markdown("### 📊 Yolculuk Özeti (Dashboard)")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Toplam Mesafe", f"{mesafe:.1f} km")
                m2.metric("Toplam Yakıt", f"{round(toplam_yakit, 2)} L")
                m3.metric("Toplam Maliyet", f"{round(toplam_maliyet, 2)} ₺")
                
                if yakit_tipi == "Benzin + LPG":
                    st.info(f"🌿 **Hibrit Tüketim Dağılımı:** {round(benzin_yakit, 2)} L Benzin + {round(lpg_yakit, 2)} L LPG")
                
                st.success(f"Bu yolculuk **{yakit_tipi}** ile yaklaşık **{round(toplam_maliyet, 2)} TL** tutacaktır.")
            else:
                st.warning("Hesaplama için lütfen sol menüden Yakıt Türünü seçin.")

    with col2:
        st.markdown("### 🗺️ Rota Haritası")
        
        if m is None:
            # SIFIR VE TERTEMİZ HARİTA (Türkiye Odaklı)
            m = folium.Map(location=[38.9637, 35.2433], zoom_start=6, tiles=None)
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                attr='Google',
                name='Google Yol Haritası',
                overlay=False,
                control=True
            ).add_to(m)
            
        harita_verisi = st_folium(m, width=600, height=450, returned_objects=["last_clicked"])
        
        # Haritadan Tıklama (Click-to-Select) Mantığı
        if harita_verisi and harita_verisi.get("last_clicked"):
            lat = harita_verisi["last_clicked"]["lat"]
            lng = harita_verisi["last_clicked"]["lng"]
            
            if 'last_processed_click' not in st.session_state:
                st.session_state.last_processed_click = None
                
            if 'click_state' not in st.session_state:
                st.session_state.click_state = 0
                
            current_click = f"{lat},{lng}"
            
            if current_click != st.session_state.last_processed_click:
                st.session_state.last_processed_click = current_click
                try:
                    from map_utils import ters_koordinat_bul
                    yer_ismi = ters_koordinat_bul(lat, lng)
                    
                    if st.session_state.click_state == 0 or st.session_state.click_state == 2:
                        st.session_state["baslangic_sehir"] = yer_ismi
                        st.session_state["varis_sehir"] = "" # İkinci tıklamayı bekle
                        st.session_state.click_state = 1
                    elif st.session_state.click_state == 1:
                        st.session_state["varis_sehir"] = yer_ismi
                        st.session_state.click_state = 2
                        
                    st.rerun()
                except Exception as e:
                    pass
        
        if rota_bilgi and "routes" in rota_bilgi:
            for idx, route in enumerate(rota_bilgi["routes"]):
                s_saat = route["duration"] // 60
                s_dk = route["duration"] % 60
                if idx == 0:
                    st.success(f"🔵 **Ana Rota:** {route['distance']:.1f} km | Tahmini Süre: {int(s_saat)} sa {int(s_dk)} dk")
                else:
                    st.caption(f"🔘 *Alternatif Rota {idx}:* {route['distance']:.1f} km | Tahmini Süre: {int(s_saat)} sa {int(s_dk)} dk")
