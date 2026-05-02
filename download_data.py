import requests
import json
import time
import os

def ibb_tum_veriyi_indir(resource_id, dosya_adi="ibb_trafik_verisi.json"):
    base_url = 'https://data.ibb.gov.tr/api/3/action/datastore_search'
    limit = 10000  # Her istekte 10.000 satır çek
    offset = 0
    tum_kayitlar = []
    
    # Masaüstü yolunu işletim sistemine göre otomatik bulma
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # Eğer masaüstü klasörü bulunamazsa (bazı Türkçe/İngilizce sistemlerde farklı olabilir), alternatif olarak 'Masaüstü' de kontrol edilebilir.
    if not os.path.exists(desktop_path):
        desktop_path_tr = os.path.join(os.path.expanduser('~'), 'Masaüstü')
        if os.path.exists(desktop_path_tr):
            desktop_path = desktop_path_tr

    dosya_yolu = os.path.join(desktop_path, dosya_adi)
    
    print(f"Veri indirme işlemi başlatıldı: {resource_id}")
    print(f"Kaydedilecek konum: {dosya_yolu}\n")

    while True:
        try:
            params = {
                'resource_id': resource_id,
                'limit': limit,
                'offset': offset
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            data = response.json()
            
            if not data['success']:
                print("API Hatası:", data.get('error'))
                break

            kayitlar = data['result']['records']
            
            if not kayitlar:
                print("\nİndirilecek başka veri kalmadı.")
                break
            
            tum_kayitlar.extend(kayitlar)
            offset += limit
            
            # İlerlemeyi göster
            print(f"Şu ana kadar {len(tum_kayitlar)} satır indirildi...", end='\r')
            
            # Sunucuyu yormamak için kısa bir ara
            time.sleep(0.5)

        except Exception as e:
            print(f"\nBağlantı hatası: {e}. 5 saniye sonra tekrar denenecek...")
            time.sleep(5)
            continue

    # Veriyi Masaüstüne JSON formatında kaydet
    print(f"\n\nİşlem tamamlandı! Toplam {len(tum_kayitlar)} satır veri alındı.")
    
    with open(dosya_yolu, 'w', encoding='utf-8') as f:
        json.dump(tum_kayitlar, f, ensure_ascii=False, indent=4)
    
    print(f"Başarıyla kaydedildi: {dosya_yolu}")

# Sizin verdiğiniz Resource ID
TRAFIK_RESOURCE_ID = 'db9c7fb3-e7f9-435a-92f4-1b917e357821'

# Çalıştır
ibb_tum_veriyi_indir(TRAFIK_RESOURCE_ID)