# ============================================================================
# map_utils.py — Harita ve Rota İşlemleri Modülü
# ============================================================================
import math
import requests
import folium
import streamlit as st

@st.cache_data
def haversine_mesafe(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@st.cache_data(show_spinner=False)
def osrm_rota_bul(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson&alternatives=true"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                routes = []
                for route in data['routes']:
                    distance = route['distance'] / 1000.0 # km
                    duration = route['duration'] / 60.0 # minutes
                    geometry = route['geometry']['coordinates'] # [lon, lat]
                    path = [[pt[1], pt[0]] for pt in geometry]
                    routes.append({"distance": distance, "duration": duration, "path": path})
                return routes
    except Exception as e:
        print("OSRM API Hatası:", e)
    
    kus_ucusu = haversine_mesafe(lat1, lon1, lat2, lon2)
    return [{"distance": kus_ucusu * 1.3, "duration": (kus_ucusu * 1.3) / 80 * 60, "path": [[lat1, lon1], [lat2, lon2]]}]

TURKIYE_SEHIRLER = {
    "Adana": (37.0000, 35.3213), "Adıyaman": (37.7648, 38.2786), "Afyonkarahisar": (38.7507, 30.5567),
    "Ağrı": (39.7191, 43.0503), "Aksaray": (38.3687, 34.0370), "Amasya": (40.6499, 35.8353),
    "Ankara": (39.9334, 32.8597), "Antalya": (36.8969, 30.7133), "Artvin": (41.1828, 41.8183),
    "Aydın": (37.8560, 27.8416), "Balıkesir": (39.6484, 27.8826), "Bartın": (41.6344, 32.3375),
    "Batman": (37.8812, 41.1351), "Bayburt": (40.2552, 40.2249), "Bilecik": (40.0567, 30.0665),
    "Bingöl": (38.8855, 40.4966), "Bitlis": (38.3938, 42.1232), "Bolu": (40.7310, 31.6061),
    "Burdur": (37.7203, 30.2903), "Bursa": (40.1885, 29.0610), "Çanakkale": (40.1553, 26.4142),
    "Çankırı": (40.6013, 33.6134), "Çorum": (40.5506, 34.9556), "Denizli": (37.7765, 29.0864),
    "Diyarbakır": (37.9144, 40.2306), "Düzce": (40.8438, 31.1565), "Edirne": (41.6818, 26.5623),
    "Elazığ": (38.6810, 39.2264), "Erzincan": (39.7500, 39.5000), "Erzurum": (39.9000, 41.2700),
    "Eskişehir": (39.7767, 30.5206), "Gaziantep": (37.0662, 37.3833), "Giresun": (40.9128, 38.3895),
    "Gümüşhane": (40.4386, 39.5086), "Hakkari": (37.5744, 43.7408), "Hatay": (36.4018, 36.3498),
    "Iğdır": (39.9167, 44.0500), "Isparta": (37.7648, 30.5566), "İstanbul": (41.0082, 28.9784),
    "İzmir": (38.4192, 27.1287), "Kahramanmaraş": (37.5847, 36.9371), "Karabük": (41.2061, 32.6204),
    "Karaman": (37.1759, 33.2287), "Kars": (40.6167, 43.1000), "Kastamonu": (41.3887, 33.7827),
    "Kayseri": (38.7312, 35.4787), "Kilis": (36.7184, 37.1212), "Kırıkkale": (39.8468, 33.5153),
    "Kırklareli": (41.7333, 27.2167), "Kırşehir": (39.1425, 34.1709), "Kocaeli": (40.8533, 29.8815),
    "Konya": (37.8746, 32.4932), "Kütahya": (39.4167, 29.9833), "Malatya": (38.3552, 38.3095),
    "Manisa": (38.6191, 27.4289), "Mardin": (37.3212, 40.7245), "Mersin": (36.8121, 34.6415),
    "Muğla": (37.2153, 28.3636), "Muş": (38.7346, 41.4910), "Nevşehir": (38.6939, 34.6857),
    "Niğde": (37.9667, 34.6833), "Ordu": (41.0000, 37.8833), "Osmaniye": (37.0746, 36.2464),
    "Rize": (41.0201, 40.5234), "Sakarya": (40.6940, 30.4358), "Samsun": (41.2928, 36.3313),
    "Şanlıurfa": (37.1591, 38.7969), "Siirt": (37.9273, 41.9420), "Sinop": (42.0231, 35.1531),
    "Sivas": (39.7477, 37.0179), "Şırnak": (37.4187, 42.4918), "Tekirdağ": (41.0000, 27.5167),
    "Tokat": (40.3167, 36.5500), "Trabzon": (41.0027, 39.7168), "Tunceli": (39.1079, 39.5401),
    "Uşak": (38.6823, 29.4082), "Van": (38.4891, 43.3832), "Yalova": (40.6500, 29.2667),
    "Yozgat": (39.8181, 34.8147), "Zonguldak": (41.4564, 31.7987),
}

from geopy.geocoders import Nominatim

def asfalta_kilitle(lat, lon):
    url = f"http://router.project-osrm.org/nearest/v1/driving/{lon},{lat}?number=1"
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                snap_lon, snap_lat = data['waypoints'][0]['location']
                return snap_lat, snap_lon
    except:
        pass
    return lat, lon

@st.cache_data(show_spinner=False)
def sehir_koordinati_bul(sehir: str) -> tuple | None:
    # 1. Önce kesin ve milimetrik şehir merkezi sözlüğümüzü kontrol edelim
    for anahtar, koord in TURKIYE_SEHIRLER.items():
        if anahtar.lower() == sehir.strip().lower():
            return asfalta_kilitle(koord[0], koord[1])
            
    # 2. Eğer listede olmayan bir ilçe vs. aranıyorsa Geopy'ye (Uyduya) soralım
    try:
        geolocator = Nominatim(user_agent="arac_yakit_app_123")
        # 'Merkez' kelimesini ekleyelim ki ilin tüm coğrafi merkezini (dağları) almasın
        location = geolocator.geocode(sehir + " Merkez, Türkiye", timeout=5)
        if location:
            return asfalta_kilitle(location.latitude, location.longitude)
    except:
        pass
        
    return None

@st.cache_data(show_spinner=False)
def ters_koordinat_bul(lat, lon):
    try:
        geolocator = Nominatim(user_agent="arac_yakit_app_123")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city', address.get('province', address.get('town', '')))
            suburb = address.get('suburb', address.get('village', ''))
            if suburb and city:
                return f"{suburb}, {city}"
            elif city:
                return city
            else:
                return location.address.split(",")[0]
    except:
        pass
    return f"{lat:.4f}, {lon:.4f}"
@st.cache_data(show_spinner=False)
def akaryakit_istasyonlari_getir(min_lat, min_lon, max_lat, max_lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    node["amenity"="fuel"]({min_lat},{min_lon},{max_lat},{max_lon});
    out 20;
    """
    try:
        r = requests.get(overpass_url, params={'data': overpass_query}, timeout=3)
        return r.json().get('elements', [])
    except:
        return []

def harita_olustur(baslangic: str, bitis: str):
    koord1 = sehir_koordinati_bul(baslangic)
    koord2 = sehir_koordinati_bul(bitis)
    
    if not koord1 or not koord2:
        return None, None
        
    routes = osrm_rota_bul(koord1[0], koord1[1], koord2[0], koord2[1])
    
    merkez_lat = (koord1[0] + koord2[0]) / 2
    merkez_lon = (koord1[1] + koord2[1]) / 2
    
    m = folium.Map(location=[merkez_lat, merkez_lon], zoom_start=6, tiles=None)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Yol Haritası',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Rotaları en kısadan en uzuna sırala (En Ekonomik Yol)
    routes = sorted(routes, key=lambda x: x["distance"])
    
    # Rota Çizgileri (Ana ve Alternatifler)
    for i, route in enumerate(routes):
        if i == 0: # En Ekonomik Ana Rota
            folium.PolyLine(route["path"], color="#0000FF", weight=6, opacity=1.0).add_to(m)
        else: # Daha Uzun Alternatif Rotalar
            folium.PolyLine(route["path"], color="#808080", weight=4, opacity=0.7, dash_array="10, 10").add_to(m)
    
    # Başlangıç ve Bitiş Markerları
    folium.Marker(koord1, popup=f"<b>Başlangıç:</b> {baslangic.capitalize()}", icon=folium.Icon(color="green", icon="play")).add_to(m)
    folium.Marker(koord2, popup=f"<b>Bitiş:</b> {bitis.capitalize()}", icon=folium.Icon(color="red", icon="flag")).add_to(m)
    
    # Akaryakıt İstasyonları (Overpass API)
    min_lat = min(koord1[0], koord2[0]) - 0.05
    max_lat = max(koord1[0], koord2[0]) + 0.05
    min_lon = min(koord1[1], koord2[1]) - 0.05
    max_lon = max(koord1[1], koord2[1]) + 0.05
    
    istasyonlar = akaryakit_istasyonlari_getir(min_lat, min_lon, max_lat, max_lon)
    for ist in istasyonlar:
        name = ist.get('tags', {}).get('name', 'Benzin İstasyonu')
        folium.Marker(
            [ist['lat'], ist['lon']],
            popup=name,
            icon=folium.Icon(color="orange", icon="gas-pump", prefix='fa')
        ).add_to(m)
    
    m.fit_bounds([koord1, koord2])
    
    return m, {"routes": routes}

def sehir_listesi() -> list:
    return sorted(TURKIYE_SEHIRLER.keys())
