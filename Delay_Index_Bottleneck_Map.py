import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def darbogaz_harita_analizi(dosya_adi="ibb_trafik_verisi.json"):
    # 1. Masaüstü Yol Ayarı
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)
    
    # 2. Veriyi Yükle ve Temizle
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Sayısal dönüşümler
    for col in ['LATITUDE', 'LONGITUDE', 'AVERAGE_SPEED', 'MAXIMUM_SPEED', 'NUMBER_OF_VEHICLES']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Mühendislik İndeksi: Gecikme Oranı (Congestion Index)
    # Hız limitine göre ne kadar yavaş gidildiğini hesaplar
    max_speeds = df.groupby('GEOHASH')['MAXIMUM_SPEED'].transform('max').replace(0, 1)
    df['DELAY_INDEX'] = (1 - (df['AVERAGE_SPEED'] / max_speeds)) * 100

    # 4. GÖRSELLEŞTİRME (Harita Altta)
    fig = plt.figure(figsize=(14, 12))
    
    # Üst Panel: Yoğunluk Dağılımı
    ax1 = plt.subplot2grid((3, 1), (0, 0))
    sns.histplot(df['DELAY_INDEX'], bins=30, kde=True, ax=ax1, color='orange')
    ax1.set_title('Şehir Genelinde Gecikme İndeksi Dağılımı', fontsize=12)
    ax1.set_xlabel('Gecikme % (Yüksek = Kilit Trafik)')

    # Alt Panel: KOORDİNAT BAZLI DARBOĞAZ HARİTASI
    # Çubuğu ve haritayı aşağıya alıyoruz
    ax2 = plt.subplot2grid((3, 1), (1, 0), rowspan=2)
    
    # Sadece en yoğun noktaları daha belirgin çizelim (Filtre: İndeks > 40)
    sc = ax2.scatter(df['LONGITUDE'], df['LATITUDE'], 
                    c=df['DELAY_INDEX'], 
                    cmap='YlOrRd', 
                    s=df['NUMBER_OF_VEHICLES']/10, # Araç sayısına göre nokta büyüklüğü
                    alpha=0.6, 
                    edgecolors='none')
    
    # Renk çubuğunu (Colorbar) haritanın altına yerleştirme
    cbar = plt.colorbar(sc, ax=ax2, orientation='horizontal', pad=0.1, aspect=40)
    cbar.set_label('Yoğunluk Seviyesi (% Hız Kaybı)')
    
    ax2.set_title('KOORDİNAT BAZLI TRAFİK DARBOĞAZ HARİTASI', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Boylam (Longitude)')
    ax2.set_ylabel('Enlem (Latitude)')
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    output_path = os.path.join(desktop, 'darbogaz_koordinat_haritasi.png')
    plt.savefig(output_path, dpi=300)
    
    # 5. MÜHENDİSİN RADARINA TAKILAN NOKTALAR
    print("\n" + "="*60)
    print("      KRİTİK DARBOĞAZ LOKASYONLARI (TOP 10)")
    print("="*60)
    hotspots = df.groupby(['LATITUDE', 'LONGITUDE'])['DELAY_INDEX'].mean().sort_values(ascending=False).head(10)
    print(hotspots)
    print("="*60)
    print(f"[-] Görsel Analiz Kaydedildi: {output_path}")

if __name__ == "__main__":
    darbogaz_harita_analizi()