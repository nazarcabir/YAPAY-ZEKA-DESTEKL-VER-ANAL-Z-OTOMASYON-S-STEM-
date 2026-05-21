import pandas as pd
import glob
import os

# 1. Adımda oluşturduğun klasörün adı
klasor_yolu = 'data/' 

# Klasördeki tüm CSV dosyalarını bul
tum_dosyalar = glob.glob(os.path.join(klasor_yolu, "*.csv"))
veri_listesi = []

print("Dosyalar okunuyor ve birleştiriliyor, lütfen bekleyin...")

for dosya in tum_dosyalar:
    # Bozuk/kirli verileri (unclean) projemize dahil etmiyoruz
    if "unclean" in dosya.lower():
        continue
        
    # Dosya adından markayı çekiyoruz (Örn: 'data/bmw.csv' -> 'Bmw')
    marka = os.path.basename(dosya).split('.')[0].capitalize()
    
    # Veriyi oku, markayı yeni bir sütun olarak başa ekle
    try:
        df = pd.read_csv(dosya)
        df.insert(0, 'Make', marka) # 'Make' sütununu en başa koyuyoruz
        veri_listesi.append(df)
        print(f"{marka} verisi başarıyla eklendi.")
    except Exception as e:
        print(f"{dosya} okunurken bir hata oluştu: {e}")

# Tüm markaları alt alta tek bir devasa tabloya çevir
ana_veri = pd.concat(veri_listesi, ignore_index=True)

# İşi biten bu devasa veriyi kaydediyoruz
ana_veri.to_csv('tum_araclar_master.csv', index=False)

print("\n--- İŞLEM TAMAM ---")
print(f"Toplam {len(ana_veri)} adet aracın verisi 'tum_araclar_master.csv' adıyla kaydedildi!")
