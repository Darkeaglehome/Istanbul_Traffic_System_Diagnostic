import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def gelismis_trafik_mekansal_analiz(dosya_adi="ibb_trafik_verisi.json"):
    # 1. Yol Ayarları
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)
    if not os.path.exists(dosya_yolu):
        print(f"Hata: {dosya_yolu} bulunamadı.")
        return

    # 2. Veri Yükleme ve Ön İşleme
    print("Gelişmiş mühendislik analizi başlatılıyor...")
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Sayısal dönüşümler
    cols = ['AVERAGE_SPEED', 'NUMBER_OF_VEHICLES', 'MAXIMUM_SPEED', 'LATITUDE', 'LONGITUDE']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['HOUR'] = df['DATE_TIME'].dt.hour
    df['DAY_TYPE'] = df['DATE_TIME'].dt.dayofweek.apply(lambda x: 'Hafta Sonu' if x >= 5 else 'Hafta İçi')

    # 3. MÜHENDİSLİK HESAPLAMALARI
    # A. Dinamik Yoğunluk İndeksi (V/Vmax Oranı)
    max_speeds = df.groupby('GEOHASH')['MAXIMUM_SPEED'].transform('max').replace(0, 1)
    df['CONGESTION_LEVEL'] = (1 - (df['AVERAGE_SPEED'] / max_speeds)) * 100
    
    # B. Hizmet Düzeyi (Level of Service - LOS) Sınıflandırması
    # A: Serbest Akış, F: Tam Tıkanıklık
    def lo_s_atama(val):
        if val < 20: return 'A'
        elif val < 40: return 'B'
        elif val < 60: return 'C'
        elif val < 80: return 'D'
        else: return 'F'
    df['LOS'] = df['CONGESTION_LEVEL'].apply(lo_s_atama)

    # 4. KOORDİNAT BAZLI YOĞUNLUK (Hotspot Analizi)
    # Koordinatları yuvarlayarak (0.001 hassasiyet yaklaşık 110 metredir) kümeleyelim
    df['LAT_ROUND'] = df['LATITUDE'].round(3)
    df['LON_ROUND'] = df['LONGITUDE'].round(3)
    
    koordinat_ozet = df.groupby(['LAT_ROUND', 'LON_ROUND']).agg({
        'CONGESTION_LEVEL': 'mean',
        'NUMBER_OF_VEHICLES': 'sum',
        'AVERAGE_SPEED': 'mean'
    }).reset_index().sort_values(by='CONGESTION_LEVEL', ascending=False)

    # 5. GÖRSELLEŞTİRME
    plt.figure(figsize=(15, 10))
    
    # Hafta İçi vs Hafta Sonu Kıyaslaması
    plt.subplot(2, 1, 1)
    sns.lineplot(data=df, x='HOUR', y='CONGESTION_LEVEL', hue='DAY_TYPE', palette='Set1', linewidth=2)
    plt.title('Hafta İçi vs Hafta Sonu Yoğunluk Karşılaştırması', fontsize=14)
    plt.grid(True, alpha=0.3)

    # Koordinat Bazlı Dağılım (Mini Harita Projeksiyonu)
    plt.subplot(2, 1, 2)
    scatter = plt.scatter(df['LONGITUDE'], df['LATITUDE'], c=df['CONGESTION_LEVEL'], 
                          cmap='YlOrRd', s=10, alpha=0.5)
    plt.colorbar(scatter, label='Yoğunluk İndeksi (%)')
    plt.title('Şehir Genelindeki Kritik Yoğunluk Odakları (Isı Haritası Taslağı)', fontsize=14)
    plt.xlabel('Boylam')
    plt.ylabel('Enlem')

    plt.tight_layout()
    plt.savefig(os.path.join(desktop, 'gelis_mis_trafik_analizi.png'))

    # 6. ÇIKTILAR VE CBS (GIS) HAZIRLIĞI
    # En yoğun 20 koordinatı ekrana bas
    print("\n" + "!"*60)
    print("      ACİL MÜDAHALE GEREKTİREN İLK 20 KOORDİNAT (HOTSPOTS)")
    print("!"*60)
    print(koordinat_ozet[['LAT_ROUND', 'LON_ROUND', 'CONGESTION_LEVEL', 'AVERAGE_SPEED']].head(20))
    
    # QGIS/ArcGIS için CSV çıktısı
    csv_yolu = os.path.join(desktop, 'ibb_trafik_analiz_GIS.csv')
    koordinat_ozet.to_csv(csv_yolu, index=False)
    
    print("\n" + "="*60)
    print(f"[-] CBS Analiz Dosyası Oluşturuldu: {csv_yolu}")
    print(f"[-] Grafik Raporu Kaydedildi: gelis_mis_trafik_analizi.png")
    print(f"[-] Toplam Analiz Edilen Segment Sayısı: {len(koordinat_ozet)}")
    print("="*60)

if __name__ == "__main__":
    gelismis_trafik_mekansal_analiz()
