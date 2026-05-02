import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import numpy as np

def ustad_seviye_trafik_analizi(dosya_adi="ibb_trafik_verisi.json"):
    # 1. Konum Ayarları
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)
    if not os.path.exists(dosya_yolu):
        print(f"Hata: {dosya_yolu} bulunamadı.")
        return

    # 2. Veri Yükleme ve Zenginleştirme
    print("Üstat seviyesi analiz verileri işleniyor...")
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Sayısal veri dönüşümleri
    numeric_cols = ['AVERAGE_SPEED', 'NUMBER_OF_VEHICLES', 'MAXIMUM_SPEED', 'LATITUDE', 'LONGITUDE']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['HOUR'] = df['DATE_TIME'].dt.hour
    df['DAY_NAME'] = df['DATE_TIME'].dt.day_name()
    
    # Mühendislik İndeksi Hesaplama (V/Vmax)
    max_speeds = df.groupby('GEOHASH')['MAXIMUM_SPEED'].transform('max').replace(0, 1)
    df['CONGESTION_%'] = (1 - (df['AVERAGE_SPEED'] / max_speeds)) * 100

    # 3. GÖRSELLEŞTİRME PANELİ (3 Farklı Perspektif)
    fig = plt.figure(figsize=(20, 15))
    plt.suptitle('İLERİ SEVİYE TRAFİK MÜHENDİSLİĞİ KARAR DESTEK PANELİ', fontsize=20, fontweight='bold')

    # A. YOĞUNLUK ISI MATRİSİ (Günlük ve Saatlik Bazda Şehrin Nabzı)
    plt.subplot(2, 2, 1)
    pivot_df = df.pivot_table(values='CONGESTION_%', index='DAY_NAME', columns='HOUR', aggfunc='mean')
    # Günleri sıralayalım
    gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_df = pivot_df.reindex(gun_sirasi)
    sns.heatmap(pivot_df, cmap='YlOrRd', annot=False, cbar_kws={'label': 'Yoğunluk (%)'})
    plt.title('Haftalık Trafik Yoğunluk Isı Matrisi', fontsize=14)
    plt.xlabel('Günün Saati')
    plt.ylabel('Gün')

    # B. HIZ DAĞILIMI VE HİZMET DÜZEYİ (Violin Plot)
    plt.subplot(2, 2, 2)
    sns.violinplot(x='HOUR', y='AVERAGE_SPEED', data=df, palette='coolwarm', inner='quartile')
    plt.title('Saatlik Hız Değişkenliği (Varyasyon Analizi)', fontsize=14)
    plt.xlabel('Saat')
    plt.ylabel('Hız (km/sa)')
    plt.axhline(df['AVERAGE_SPEED'].mean(), color='blue', linestyle='--', label='Genel Ort.')

    # C. ARAÇ SAYISI VS YOĞUNLUK (Kapasite Doygunluk Analizi)
    plt.subplot(2, 2, 3)
    # Regresyon analizi ile kapasite aşım noktasını görelim
    sns.regplot(x='NUMBER_OF_VEHICLES', y='AVERAGE_SPEED', data=df.sample(min(len(df), 1000)), 
                scatter_kws={'alpha':0.2}, line_kws={'color':'red'})
    plt.title('Kapasite-Hız İlişkisi (Akış Rejimi)', fontsize=14)
    plt.xlabel('Araç Sayısı')
    plt.ylabel('Hız (km/sa)')

    # D. MEKANSAL DARBOĞAZLAR (En Yoğun 15 Nokta)
    plt.subplot(2, 2, 4)
    top_bottlenecks = df.groupby(['LATITUDE', 'LONGITUDE'])['CONGESTION_%'].mean().sort_values(ascending=False).head(15)
    top_bottlenecks.plot(kind='barh', color='darkred')
    plt.title('En Kritik 15 Koordinat (Mekansal Darboğazlar)', fontsize=14)
    plt.xlabel('Ortalama Yoğunluk (%)')
    plt.ylabel('Koordinat (Lat, Lon)')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # 4. ÇIKTILAR
    output_img = os.path.join(desktop, 'ustad_analiz_paneli.png')
    plt.savefig(output_img)
    
    # Teknik Rapor
    print("\n" + "█"*60)
    print("      TRAFİK ÜSTADI - ANALİTİK RAPOR ÇIKTISI")
    print("█"*60)
    print(f"[-] En Stabil Gün: {pivot_df.mean(axis=1).idxmin()}")
    print(f"[-] Şehir İçi Akış Rejimi: {'Kararsız (Unstable)' if df['AVERAGE_SPEED'].std() > 15 else 'Stabil'}")
    print(f"[-] Kritik Hız Eşiği: {df['AVERAGE_SPEED'].quantile(0.15):.2f} km/sa (Alt %15 dilimi)")
    print(f"[-] Grafik Raporu Hazır: {output_img}")
    print("█"*60)

if __name__ == "__main__":
    ustad_seviye_trafik_analizi()