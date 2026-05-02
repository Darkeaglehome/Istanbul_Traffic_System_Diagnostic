import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import contextily as ctx

def harita_odakli_darbogaz_analizi(dosya_adi="ibb_trafik_verisi.json"):
    # 1. Yol ve Dosya Kontrolü
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Sayısal veri dönüşümü
    for col in ['LATITUDE', 'LONGITUDE', 'AVERAGE_SPEED', 'MAXIMUM_SPEED', 'NUMBER_OF_VEHICLES']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Darboğaz Hesaplama ve İlk 20 Nokta
    max_speeds = df.groupby('GEOHASH')['MAXIMUM_SPEED'].transform('max').replace(0, 1)
    df['CONGESTION'] = (1 - (df['AVERAGE_SPEED'] / max_speeds)) * 100
    
    top_20 = df.groupby(['LATITUDE', 'LONGITUDE']).agg({
        'CONGESTION': 'mean',
        'NUMBER_OF_VEHICLES': 'sum'
    }).reset_index().sort_values(by='CONGESTION', ascending=False).head(20)

    # 3. GÖRSELLEŞTİRME (Gerçek Harita Altlığı ile)
    # Figür boyutunu büyütelim ki detaylar seçilsin
    fig, ax = plt.subplots(figsize=(15, 12))

    # Darboğaz noktalarını büyük, içi dolu kırmızı daireler olarak çiz
    # s=300 sabit boyutu sayesinde noktalar küçülüp kaybolmaz
    scatter = ax.scatter(top_20['LONGITUDE'], top_20['LATITUDE'], 
                         c='red', 
                         s=400, 
                         alpha=0.7, 
                         edgecolors='black', 
                         linewidth=2, 
                         zorder=5)

    # Numaralandırma (Daha okunaklı olması için beyaz zeminli)
    for i, row in top_20.reset_index().iterrows():
        ax.text(row['LONGITUDE'], row['LATITUDE'], str(i+1), 
                fontsize=12, fontweight='bold', ha='center', va='center', 
                color='white', zorder=6)

    # 4. ZOOM VE HARİTA AYARI
    # Sınırları sadece en yoğun noktaların etrafına daralt (Zoom etkisi)
    margin = 0.02 # Yakınlık derecesi (daha küçük sayı = daha çok yakınlaşma)
    ax.set_xlim(top_20['LONGITUDE'].min() - margin, top_20['LONGITUDE'].max() + margin)
    ax.set_ylim(top_20['LATITUDE'].min() - margin, top_20['LATITUDE'].max() + margin)

    # Arka plana OpenStreetMap ekle
    # crs='epsg:4326' koordinat sistemini (WGS84) temsil eder
    ctx.add_basemap(ax, crs='epsg:4326', source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_title('İBB TRAFİK DARBOĞAZLARI - LOKASYON ODAKLI ANALİZ', fontsize=16, fontweight='bold')
    ax.set_axis_off() # Koordinat eksenlerini gizle (Daha temiz görünüm)

    # Çıktı
    output_path = os.path.join(desktop, 'gercek_harita_darbogaz.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n[!] Harita 'gercek_harita_darbogaz.png' adıyla masaüstüne kaydedildi.")

if __name__ == "__main__":
    harita_odakli_darbogaz_analizi()
