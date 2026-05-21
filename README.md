# Yapay Zeka Destekli Veri Analizi ve Otomasyon Sistemi (Yakıt Tahmin Projesi)

Bu proje, araçların yakıt tüketimlerini makine öğrenmesi algoritmalarıyla tahmin eden ve güzergah optimizasyonunu destekleyen yapay zeka tabanlı bir veri analizi otomasyon sistemidir.

## Proje İçeriği

- **app.py**: Streamlit tabanlı web arayüzü ana uygulaması. Kullanıcılar buradan araç modeli ve yakıt verilerini girerek tahminler alabilir.
- **model.py**: Makine öğrenmesi modelinin eğitilmesi ve tahmin yapılması işlemlerini içerir.
- **data_fetcher.py**: Verilerin çekilmesi ve ön işleme adımlarının gerçekleştirildiği modüldür.
- **map_utils.py**: Harita ve güzergah görselleştirmeleri için yardımcı fonksiyonları içerir.
- **veri_birlestir.py**: Farklı kaynaklardan gelen veri setlerini (örneğin fuel.csv) birleştirmek için kullanılır.
- **OptiYol_Baslat.bat**: Projeyi Windows ortamında hızlıca başlatmak (Streamlit uygulamasını ayağa kaldırmak) için kullanılan betik dosyasıdır.
- **.pkl Dosyaları**: Eğitilmiş modeller ve etiket kodlayıcılar (label_encoders.pkl, yakit_modeli.pkl).

## Gereksinimler

Projenin çalışması için Python ve ilgili kütüphanelerin yüklü olması gerekmektedir:
- Python 3.8+
- Streamlit
- Pandas
- Scikit-learn
- Numpy

## Kurulum ve Çalıştırma

1. Repository'yi klonlayın:
   ```bash
   git clone https://github.com/nazarcabir/YAPAY-ZEKA-DESTEKL-VER-ANAL-Z-OTOMASYON-S-STEM-.git
   cd YAPAY-ZEKA-DESTEKL-VER-ANAL-Z-OTOMASYON-S-STEM-
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
   *(Eğer requirements.txt yoksa, projedeki `.py` dosyalarına göre yukarıdaki kütüphaneleri manuel olarak yükleyebilirsiniz.)*

3. Uygulamayı başlatın:
   Windows kullanıyorsanız `OptiYol_Baslat.bat` dosyasına çift tıklayarak veya terminal üzerinden aşağıdaki komutla Streamlit'i başlatabilirsiniz:
   ```bash
   streamlit run app.py
   ```

## Özellikler

- **Yakıt Tüketim Tahmini**: Çeşitli parametreler girilerek aracın yakıt tüketimi yapay zeka modeliyle tahmin edilir.
- **Veri Analizi ve Görselleştirme**: Etkileşimli haritalar ve grafikler ile verilerin incelenmesi sağlanır.
- **Kullanıcı Dostu Arayüz**: Streamlit ile geliştirilmiş, kolay anlaşılır arayüz.

## Geliştirici
- Nazar Cabir
