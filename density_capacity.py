import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def trafik_bas_muhendis_analizi(dosya_adi="ibb_trafik_verisi.json"):
    # 1. Masaüstü Yolunu Tespit Et
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)

    if not os.path.exists(dosya_yolu):
        print(f"Hata: '{dosya_yolu}' bulunamadı.")
        return

    # 2. Veriyi Yükle
    print("Veri yükleniyor ve mühendislik hesaplamaları yapılıyor...")
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Sayısal dönüşümler
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['HOUR'] = df['DATE_TIME'].dt.hour
    for col in ['AVERAGE_SPEED', 'NUMBER_OF_VEHICLES', 'MAXIMUM_SPEED']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. MÜHENDİSLİK HESAPLAMASI: Yoğunluk İndeksi Oluşturma
    # İndeks = 100 * (1 - (Mevcut Hız / Maksimum Hız))
    # Bu formül hız düştükçe yoğunluk endeksini artırır.
    
    # Her bölge (GEOHASH) için gözlemlenen en yüksek hızı 'serbest akış' kabul edelim
    max_speeds = df.groupby('GEOHASH')['MAXIMUM_SPEED'].transform('max')
    
    # Sıfıra bölünme hatasını engellemek için minimum 1 km/s hız varsayalım
    df['TRAFFIC_INDEX'] = (1 - (df['AVERAGE_SPEED'] / max_speeds.replace(0, 1))) * 100
    df['TRAFFIC_INDEX'] = df['TRAFFIC_INDEX'].clip(0, 100) # 0-100 arası sınırla

    # 4. Analiz ve Görselleştirme
    plt.style.use('ggplot')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # A. Peak Hour Analizi
    saatlik_ort = df.groupby('HOUR')['TRAFFIC_INDEX'].mean()
    sns.lineplot(x=saatlik_ort.index, y=saatlik_ort.values, ax=ax1, color='darkred', linewidth=2.5)
    ax1.set_title('Hesaplanan Saatlik Trafik Yoğunluk Trendi', fontsize=14)
    ax1.set_ylabel('Yoğunluk İndeksi (%)')
    ax1.set_xticks(range(0, 24))

    # B. Araç Sayısı vs Hız (Akış Diyagramı)
    sns.scatterplot(data=df.sample(min(len(df), 2000)), x='NUMBER_OF_VEHICLES', y='AVERAGE_SPEED', ax=ax2, alpha=0.5)
    ax2.set_title('Araç Sayısı - Ortalama Hız İlişkisi (Kapasite Analizi)', fontsize=14)
    ax2.set_xlabel('Şerit Başına Tahmini Araç Sayısı')
    ax2.set_ylabel('Hız (km/sa)')

    plt.tight_layout()
    plot_yolu = os.path.join(desktop, 'muhendislik_analiz_sonuc.png')
    plt.savefig(plot_yolu)

    # 5. Teknik Rapor
    print("\n" + "="*50)
    print("      TRAFİK MÜHENDİSLİĞİ TÜRETİLMİŞ VERİ RAPORU")
    print("="*50)
    print(f"[-] Analiz Edilen Nokta Sayısı: {df['GEOHASH'].nunique()}")
    print(f"[-] Şehir Geneli Ortalama Hız: {df['AVERAGE_SPEED'].mean():.2f} km/sa")
    print(f"[-] En Yoğun Saat (Peak Hour): {saatlik_ort.idxmax()}:00")
    print(f"[-] Ortalama Yoğunluk Seviyesi: %{df['TRAFFIC_INDEX'].mean():.1f}")
    print(f"[-] Grafik Dosyası: {plot_yolu}")
    print("="*50)
    
    if saatlik_ort.idxmax() in [7, 8, 9, 17, 18, 19]:
        print("MÜHENDİS NOTU: Zirve saatler işe gidiş/dönüş periyotlarıyla tam uyumlu.")

if __name__ == "__main__":
    trafik_bas_muhendis_analizi()