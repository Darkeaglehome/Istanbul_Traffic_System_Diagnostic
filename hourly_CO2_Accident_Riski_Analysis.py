import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def ileri_muhendislik_analiz_paketi(dosya_adi="ibb_trafik_verisi.json"):
    # Masaüstü yolu tespiti
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser('~'), 'Masaüstü')
    
    dosya_yolu = os.path.join(desktop, dosya_adi)
    with open(dosya_yolu, 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))

    # Veri Hazırlığı
    df['AVERAGE_SPEED'] = pd.to_numeric(df['AVERAGE_SPEED'], errors='coerce')
    df['NUMBER_OF_VEHICLES'] = pd.to_numeric(df['NUMBER_OF_VEHICLES'], errors='coerce')
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df['HOUR'] = df['DATE_TIME'].dt.hour

    # 1. EMİSYON TAHMİNİ (Basit Lineer Model: Düşük hız = Yüksek Emisyon)
    # Formül: Araç Sayısı * (Sabit + Hız Faktörü)
    df['ESTIMATED_CO2'] = df['NUMBER_OF_VEHICLES'] * (150 + (80 / (df['AVERAGE_SPEED'] + 1) * 10))

    # 2. TRAFİK KARARLILIĞI (Hız Standart Sapması)
    # Hızdaki yüksek değişim kararsız akışı (unstable flow) gösterir
    stability = df.groupby('HOUR')['AVERAGE_SPEED'].std().rename('SPEED_VARIATION')

    # 3. GÖRSELLEŞTİRME
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

    # A. Karbon Ayak İzi Analizi
    emisyon_saatlik = df.groupby('HOUR')['ESTIMATED_CO2'].sum()
    ax1.fill_between(emisyon_saatlik.index, emisyon_saatlik.values, color='green', alpha=0.3)
    ax1.plot(emisyon_saatlik.index, emisyon_saatlik.values, color='darkgreen', linewidth=2)
    ax1.set_title('Saatlik Tahmini CO2 Emisyon Yükü (Çevresel Etki)', fontsize=14)
    ax1.set_ylabel('Tahmini Gram/Saat')

    # B. Akış Kararlılığı (Güvenlik Analizi)
    sns.barplot(x=stability.index, y=stability.values, ax=ax2, palette='OrRd')
    ax2.set_title('Trafik Akış Kararsızlığı (Yüksek Değer = Kaza Riski ve Şok Dalgası)', fontsize=14)
    ax2.set_ylabel('Hız Değişkenliği (Std Dev)')

    plt.tight_layout()
    plt.savefig(os.path.join(desktop, 'cevresel_ve_guvenlik_analizi.png'))
    
    print(f"\n[!] Yeni Analiz Tamamlandı.")
    print(f"[-] En yüksek emisyon saati: {emisyon_saatlik.idxmax()}:00")
    print(f"[-] En kararsız (riskli) trafik saati: {stability.idxmax()}:00")

if __name__ == "__main__":
    ileri_muhendislik_analiz_paketi()