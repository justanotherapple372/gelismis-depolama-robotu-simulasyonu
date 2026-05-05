import simpy
import random
import matplotlib.pyplot as plt

def depoyu_calistir():
    print("--- Özel Robot Atamalı Akıllı Depo Simülasyonu ---")
    
    try:
        # Robot Sayıları
        ra_say = int(input("A Tipi Robot Sayısı: "))
        rb_say = int(input("B Tipi Robot Sayısı: "))
        rc_say = int(input("C Tipi Robot Sayısı: "))
        
        # Ürün Parametreleri (Geliş Aralığı, Min ve Max Taşıma)
        a_gelis = float(input("A Tipi Ürün Geliş Aralığı (dk): "))
        a_min, a_max = float(input("A Min Taşıma: ")), float(input("A Max Taşıma: "))
        
        b_gelis = float(input("B Tipi Ürün Geliş Aralığı (dk): "))
        b_min, b_max = float(input("B Min Taşıma: ")), float(input("B Max Taşıma: "))
        
        c_gelis = float(input("C Tipi Ürün Geliş Aralığı (dk): "))
        c_min, c_max = float(input("C Min Taşıma: ")), float(input("C Max Taşıma: "))
        
        sim_suresi = int(input("Simülasyon Toplam Süre (Dakika): "))
    except ValueError:
        print("Lütfen geçerli sayısal değerler giriniz.")
        return

    # Veri Yapısı
    istatistikler = {
        'A': {'beklemeler': [], 'kullanim': [], 'zamanlar': [], 'renk': 'skyblue', 'etiket': 'Hafif (A)'},
        'B': {'beklemeler': [], 'kullanim': [], 'zamanlar': [], 'renk': 'orange', 'etiket': 'Orta (B)'},
        'C': {'beklemeler': [], 'kullanim': [], 'zamanlar': [], 'renk': 'crimson', 'etiket': 'Ağır (C)'}
    }

    class AkilliDepo:
        def __init__(self, env):
            self.env = env
            self.robotlar = {
                'A': simpy.Resource(env, ra_say),
                'B': simpy.Resource(env, rb_say),
                'C': simpy.Resource(env, rc_say)
            }

    def urun_sureci(env, tip, depo, min_s, max_s):
        varis = env.now
        robot_kaynagi = depo.robotlar[tip]
        
        with robot_kaynagi.request() as talep:
            yield talep
            bekleme = env.now - varis
            istatistikler[tip]['beklemeler'].append(bekleme)
            
            # Anlık kullanım verisi kaydı
            istatistikler[tip]['zamanlar'].append(env.now)
            istatistikler[tip]['kullanim'].append(robot_kaynagi.count)
            
            # Taşıma süreci
            yield env.timeout(random.uniform(min_s, max_s))

    def uretici(env, tip, gelis_araligi, depo, min_s, max_s):
        while True:
            yield env.timeout(random.expovariate(1.0 / gelis_araligi))
            env.process(urun_sureci(env, tip, depo, min_s, max_s))

    # Simülasyon Başlatma
    env = simpy.Environment()
    depo = AkilliDepo(env)

    env.process(uretici(env, 'A', a_gelis, depo, a_min, a_max))
    env.process(uretici(env, 'B', b_gelis, depo, b_min, b_max))
    env.process(uretici(env, 'C', c_gelis, depo, c_min, c_max))

    env.run(until=sim_suresi)

    # --- SİMÜLASYON ÖZET RAPORU ---
    print("\n" + "-"*40)
    print("--- Simülasyon Özet Raporu ---")
    print("-" * 40)
    
    toplam_islenen = 0
    for tip, veri in istatistikler.items():
        sayi = len(veri['beklemeler'])
        toplam_islenen += sayi
        if sayi > 0:
            ort_bekleme = sum(veri['beklemeler']) / sayi
            max_bekleme = max(veri['beklemeler'])
            print(f"{veri['etiket']}: {sayi} adet işlendi. Ort. Bekleme: {ort_bekleme:.2f} dk | Maks. Bekleme: {max_bekleme:.2f} dk")
        else:
            print(f"{veri['etiket']}: Hiç ürün işlenemedi.")
    
    print("-" * 40)
    print(f"TOPLAM İŞLENEN ÜRÜN: {toplam_islenen}")
    print("-" *40)

    # Grafikler
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Bekleme Dağılımı
    for tip, veri in istatistikler.items():
        if veri['beklemeler']:
            ax1.hist(veri['beklemeler'], bins=15, alpha=0.5, label=veri['etiket'], color=veri['renk'], edgecolor='black')
    ax1.set_title('Ürün Bazlı Bekleme Süreleri')
    ax1.set_xlabel('Dakika')
    ax1.legend()

    # Robot Doluluğu
    for tip, veri in istatistikler.items():
        if veri['zamanlar']:
            ax2.step(veri['zamanlar'], veri['kullanim'], where='post', label=f"{tip} Robotu", color=veri['renk'])
    ax2.set_title('Robot Tiplerinin Anlık Kullanımı')
    ax2.set_xlabel('Zaman (dk)')
    ax2.set_ylabel('Aktif Robot Sayısı')
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    depoyu_calistir()
