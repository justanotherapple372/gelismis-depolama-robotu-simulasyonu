import streamlit as st
import simpy
import random
import matplotlib.pyplot as plt

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Akıllı Depo Simülasyonu", layout="wide")

st.title("İnteraktif Akıllı Depo Simülasyonu Dashboard")
st.write("Sol taraftaki menüden sınıf parametrelerini ayarlayın, sınıflar arası taşıma kapasitelerini belirleyin ve simülasyonu başlatın.")

# --- SIDEBAR (GİRDİ ALANLARI) ---
st.sidebar.header("⚙️ Genel Sistem Parametreleri")

sinif_sayisi = st.sidebar.number_input(
    "Tanımlanacak Sınıf Sayısı", 
    min_value=1, value=2, step=1,
    help="Depoda çalışacak farklı ürün ve robot gruplarının toplam sayısını belirler."
)

personel_sayisi = st.sidebar.number_input(
    "Bakım Personeli (Teknisyen) Sayısı", 
    min_value=1, value=2, step=1,
    help="Şarjı yolda biten ve arızalanan robotları kurtarmakla görevli toplam teknisyen sayısıdır."
)

sim_suresi = st.sidebar.slider(
    "Simülasyon Toplam Süresi (Dakika)", 
    min_value=10, max_value=1440, value=480, step=30,
    help="Simülasyonun ne kadar süre boyunca koşturulacağını belirler."
)

genel_esik_aktif = st.sidebar.checkbox(
    "🔋 Tüm Sınıflar İçin 'Kritik Şarj Eşiğini' Yönet", 
    value=True
)

genel_sarj_esigi_yuzde = 0
if genel_esik_aktif:
    genel_sarj_esigi_yuzde = st.sidebar.slider(
        "Sistem Geneli Kritik Şarj Eşiği (%)", 
        min_value=5, max_value=50, value=20, step=5
    )

# --- SIDEBAR ALANI: DEPO YÖNETİMİ ---
st.sidebar.header("🏢 Depo Yönetimi (Raf Kapasiteleri)")
depo_kapasite_ayarlari = {}

for i in range(1, sinif_sayisi + 1):
    with st.sidebar.expander(f"🧱 Sınıf {i} Raf/Depolama Ayarı", expanded=False):
        kapasite_kisi_aktif = st.checkbox(
            f"Sınıf {i} İçin Raf Kapasitesi Sınırı Aktif", 
            value=False, 
            key=f"kap_aktif_{i}",
            help="Aktif edilirse raf dolduğunda mal kabul durur veya robotlar bekler. Aktif değilse depo rafları sınırsız kabul edilir."
        )
        
        if kapasite_kisi_aktif:
            raf_sayisi = st.number_input(
                f"Sınıf {i} Depo Raf Sayısı (Kapasite)", 
                min_value=1, value=100, step=10, 
                key=f"raf_sayi_{i}"
            )
            depo_kapasite_ayarlari[f"Sinif_{i}"] = raf_sayisi
        else:
            depo_kapasite_ayarlari[f"Sinif_{i}"] = float('inf') # Sınırsız kapasite

# Sınıf bazlı dinamik girdileri toplamak için sözlük
siniflar_verisi = {}

st.sidebar.header("🤖 Sınıf Bazlı Parametreler")
for i in range(1, sinif_sayisi + 1):
    with st.sidebar.expander(f"📦 Sınıf {i} Özellikleri", expanded=(i==1)):
        
        robot_adet = st.slider(
            f"Sınıf {i} Robot Sayısı", min_value=1, max_value=20, value=3, key=f"r_{i}"
        )
        gelis_araligi = st.slider(
            f"Sınıf {i} Ürün Geliş Aralığı (dk)", min_value=0.5, max_value=30.0, value=5.0, step=0.5, key=f"g_{i}"
        )
        max_calisma_suresi = st.slider(
            f"Sınıf {i} Robot Şarj Ömrü (dk)", min_value=5.0, max_value=240.0, value=30.0, step=1.0, key=f"mcs_{i}"
        )
        sarj_suresi = st.slider(
            f"Sınıf {i} Robot Şarj Süresi (dk)", min_value=1.0, max_value=120.0, value=15.0, step=1.0, key=f"ss_{i}"
        )
        
        kritik_sarj_suresi = max_calisma_suresi * (genel_sarj_esigi_yuzde / 100.0)
        
        dagilim_tipi = st.selectbox(
            f"Sınıf {i} Taşıma Süresi Dağılımı",
            options=["Uniform (Düzgün)", "Normal (Gauss)", "Triangular (Üçgensel)"],
            key=f"dagilim_{i}"
        )
        
        dagilim_parametreleri = {}
        if dagilim_tipi == "Uniform (Düzgün)":
            tasima_araligi = st.slider(f"Sınıf {i} Taşıma Süresi Aralığı (dk)", min_value=0.1, max_value=30.0, value=(4.0, 8.0), step=0.5, key=f"aralik_{i}")
            dagilim_parametreleri = {'tip': 'uniform', 'min': tasima_araligi[0], 'max': tasima_araligi[1]}
        elif dagilim_tipi == "Normal (Gauss)":
            c1, c2 = st.columns(2)
            mu = c1.number_input(f"Ortalama Süre (μ)", min_value=0.1, value=4.0, step=0.5, key=f"mu_{i}")
            sigma = c2.number_input(f"Standart Sapma (σ)", min_value=0.01, value=0.5, step=0.1, key=f"sigma_{i}")
            dagilim_parametreleri = {'tip': 'normal', 'mu': mu, 'sigma': sigma}
        elif dagilim_tipi == "Triangular (Üçgensel)":
            c1, c2, c3 = st.columns(3)
            low = c1.number_input(f"Alt Limit (Min)", min_value=0.1, value=2.0, step=0.5, key=f"low_{i}")
            mode = c2.number_input(f"En Olası (Mod)", min_value=0.1, value=3.5, step=0.5, key=f"mode_{i}")
            high = c3.number_input(f"Üst Limit (Max)", min_value=0.1, value=6.0, step=0.5, key=f"high_{i}")
            dagilim_parametreleri = {'tip': 'triangular', 'low': low, 'mode': mode, 'high': high}

        # --- ÇAPRAZ SINIF TAŞIMA VE KAPASİTE SEÇİMİ (MATRİS ALTYAPISI) ---
        st.markdown("---")
        baska_tasir_mi = st.checkbox(f"🔄 Sınıf {i} Robotları Başka Sınıf Ürünleri Taşıyabilir", value=False, key=f"baska_{i}")
        
        tasinabilir_siniflar = {}
        tasinabilir_siniflar[f"Sinif_{i}"] = 1 
        
        if baska_tasir_mi:
            diger_siniflar = [f"Sınıf {x}" for x in range(1, sinif_sayisi + 1) if x != i]
            if diger_siniflar:
                secilen_siniflar = st.multiselect(
                    f"Sınıf {i} Robotunun Taşıyabileceği Diğer Sınıflar:",
                    options=diger_siniflar,
                    key=f"secilen_{i}"
                )
                for secilen in secilen_siniflar:
                    s_id = secilen.replace("Sınıf ", "Sinif_")
                    kapasite = st.number_input(
                        f"👉 {secilen} ürününden tek seferde kaç adet taşıyabilir?",
                        min_value=1, value=2, step=1, key=f"kap_{i}_{s_id}",
                        help="Ağırlık farkından dolayı bu robota tek seferde yüklenebilecek maksimum ürün adedi."
                    )
                    tasinabilir_siniflar[s_id] = kapasite

        sinif_anahtar = f"Sinif_{i}"
        siniflar_verisi[sinif_anahtar] = {
            'id': i, 
            'robot_sayisi': robot_adet, 
            'gelis_araligi': gelis_araligi,
            'max_calisma_suresi': max_calisma_suresi,
            'sarj_suresi': sarj_suresi,
            'kritik_sarj_suresi': kritik_sarj_suresi,
            'dagilim': dagilim_parametreleri,
            'tasima_kapasiteleri': tasinabilir_siniflar, 
            'etiket': f"Sınıf {i}",
            'beklemeler': [], 'kullanim': [], 'zamanlar': [], 'yolda_kalan': 0
        }

# --- YARDIMCI FONKSİYONLAR ---
def tasima_suresi_hesapla(dagilim_ayari):
    sure = 0.1
    if dagilim_ayari['tip'] == 'uniform':
        sure = random.uniform(dagilim_ayari['min'], dagilim_ayari['max'])
    elif dagilim_ayari['tip'] == 'normal':
        sure = random.normalvariate(dagilim_ayari['mu'], dagilim_ayari['sigma'])
    elif dagilim_ayari['tip'] == 'triangular':
        low, mode, high = dagilim_ayari['low'], dagilim_ayari['mode'], dagilim_ayari['high']
        if not (low <= mode <= high):
            mode = (low + high) / 2
        sure = random.triangular(low, high, mode)
    return max(0.1, sure)

# --- SIMPY SİMÜLASYON MOTORU VE SINIFLARI ---
class Robot:
    def __init__(self, isim, ana_sinif_adi, batarya_kapasitesi):
        self.isim = isim
        self.ana_sinif_adi = ana_sinif_adi 
        self.kalan_sarj = batarya_kapasitesi
        self.durum = "HAZIR"  

class AkilliDepo:
    def __init__(self, env, siniflar_konfigrasyonu, personel_sayisi, raf_konfigrasyonu):
        self.env = env
        self.siniflar = siniflar_konfigrasyonu
        self.robot_havuzlari = {}
        self.sarj_istasyonlari = {}
        self.depo_raflari = {}
        
        self.mal_kabul_alani = {s_isim: [] for s_isim in siniflar_konfigrasyonu.keys()}
        
        for s_isim, s_veri in siniflar_konfigrasyonu.items():
            self.robot_havuzlari[s_isim] = simpy.Store(env, capacity=s_veri['robot_sayisi'])
            self.sarj_istasyonlari[s_isim] = simpy.Resource(env, capacity=s_veri['robot_sayisi'])
            self.depo_raflari[s_isim] = simpy.Container(env, capacity=raf_konfigrasyonu[s_isim], init=0)
            
            for i in range(s_veri['robot_sayisi']):
                self.robot_havuzlari[s_isim].put(Robot(f"R-{s_isim}-{i+1}", s_isim, s_veri['max_calisma_suresi']))
        
        self.personel = simpy.Resource(env, capacity=personel_sayisi)

    @property
    def toplam_mal_kabul_yuku(self):
        return sum(len(alan) for alan in self.mal_kabul_alani.values())

personel_izleme = {'zaman': [0.0], 'kullanim_orani': [0.0]}
mal_kabul_izleme = {}

def urun_sureci(env, urun_sinif_adi, depo):
    varis_zamani = env.now
    
    if depo.depo_raflari[urun_sinif_adi].level >= depo.depo_raflari[urun_sinif_adi].capacity:
        return 

    depo.mal_kabul_alani[urun_sinif_adi].append(varis_zamani)
    
    mal_kabul_izleme[urun_sinif_adi]['zaman'].append(env.now)
    mal_kabul_izleme[urun_sinif_adi]['alanda_bekleyen'].append(len(depo.mal_kabul_alani[urun_sinif_adi]))
    
    uyumlu_robot_siniflari = []
    for r_sinif_adi, r_veri in depo.siniflar.items():
        if urun_sinif_adi in r_veri['tasima_kapasiteleri']:
            uyumlu_robot_siniflari.append(r_sinif_adi)
            
    tetikleyiciler = [depo.robot_havuzlari[r_sinif].get() for r_sinif in uyumlu_robot_siniflari]
    sonuc = yield env.any_of(tetikleyiciler)
    
    alinan_get_olayi = list(sonuc.keys())[0]
    robot = sonuc[alinan_get_olayi]
    robot_unvan_sinif = robot.ana_sinif_adi
    
    if varis_zamani not in depo.mal_kabul_alani[urun_sinif_adi]:
        yield depo.robot_havuzlari[robot_unvan_sinif].put(robot) 
        return 

    tasima_kapasitesi = depo.siniflar[robot_unvan_sinif]['tasima_kapasiteleri'][urun_sinif_adi]
    
    goturulecek_adet = 0
    for _ in range(tasima_kapasitesi):
        if depo.mal_kabul_alani[urun_sinif_adi]:
            mevcut_bos_yer = depo.depo_raflari[urun_sinif_adi].capacity - depo.depo_raflari[urun_sinif_adi].level
            if mevcut_bos_yer > goturulecek_adet:
                urun_v_zamani = depo.mal_kabul_alani[urun_sinif_adi].pop(0)
                bekleme = env.now - urun_v_zamani
                siniflar_verisi[urun_sinif_adi]['beklemeler'].append(bekleme)
                goturulecek_adet += 1
            else:
                break
                
    mal_kabul_izleme[urun_sinif_adi]['zaman'].append(env.now)
    mal_kabul_izleme[urun_sinif_adi]['alanda_bekleyen'].append(len(depo.mal_kabul_alani[urun_sinif_adi]))
    
    if goturulecek_adet == 0:
        yield depo.robot_havuzlari[robot_unvan_sinif].put(robot)
        return

    mesgul_robot = depo.siniflar[robot_unvan_sinif]['robot_sayisi'] - len(depo.robot_havuzlari[robot_unvan_sinif].items)
    yuzde_doluluk = (mesgul_robot / depo.siniflar[robot_unvan_sinif]['robot_sayisi']) * 100
    siniflar_verisi[robot_unvan_sinif]['zamanlar'].append(env.now)
    siniflar_verisi[robot_unvan_sinif]['kullanim'].append(yuzde_doluluk)

    tasima_suresi = tasima_suresi_hesapla(depo.siniflar[robot_unvan_sinif]['dagilim'])
    
    if robot.kalan_sarj >= tasima_suresi:
        robot.durum = "TASIMA_DA"
        yield env.timeout(tasima_suresi)
        robot.kalan_sarj -= tasima_suresi
        
        yield depo.depo_raflari[urun_sinif_adi].put(goturulecek_adet)
        
        if robot.kalan_sarj <= depo.siniflar[robot_unvan_sinif]['kritik_sarj_suresi']:
            env.process(robot_sarj_sureci(env, robot, robot_unvan_sinif, depo))
        else:
            yield depo.robot_havuzlari[robot_unvan_sinif].put(robot)
    else:
        yolda_gecen_sure = robot.kalan_sarj
        yield env.timeout(yolda_gecen_sure)
        robot.kalan_sarj = 0
        robot.durum = "ARIZALI"
        siniflar_verisi[robot_unvan_sinif]['yolda_kalan'] += 1
        env.process(robot_kurtarma_sureci(env, robot, robot_unvan_sinif, depo))

def robot_kurtarma_sureci(env, robot, robot_unvan_sinif, depo):
    with depo.personel.request() as talep:
        yield talep
        personel_izleme['zaman'].append(env.now)
        personel_izleme['kullanim_orani'].append((depo.personel.count / depo.personel.capacity) * 100)
        yield env.timeout(10.0)
        env.process(robot_sarj_sureci(env, robot, robot_unvan_sinif, depo))
    personel_izleme['zaman'].append(env.now)
    personel_izleme['kullanim_orani'].append((depo.personel.count / depo.personel.capacity) * 100)

def robot_sarj_sureci(env, robot, robot_unvan_sinif, depo):
    robot.durum = "SARJ_DA"
    with depo.sarj_istasyonlari[robot_unvan_sinif].request() as talep:
        yield talep
        yield env.timeout(depo.siniflar[robot_unvan_sinif]['sarj_suresi'])
        robot.kalan_sarj = depo.siniflar[robot_unvan_sinif]['max_calisma_suresi']
        robot.durum = "HAZIR"
    yield depo.robot_havuzlari[robot_unvan_sinif].put(robot)

def uretici(env, s_isim, depo):
    gelis_araligi = depo.siniflar[s_isim]['gelis_araligi']
    while True:
        yield env.timeout(random.expovariate(1.0 / gelis_araligi))
        env.process(urun_sureci(env, s_isim, depo))

# --- SIMULATION BUTTON AND ENGINE ---
if st.sidebar.button("🚀 Simülasyonu Başlat", use_container_width=True):
    personel_izleme = {'zaman': [0.0], 'kullanim_orani': [0.0]}
    mal_kabul_izleme = {s_isim: {'zaman': [0.0], 'alanda_bekleyen': [0]} for s_isim in siniflar_verisi.keys()}
    
    with st.spinner("Simülasyon yürütülüyor..."):
        env = simpy.Environment()
        depo = AkilliDepo(env, siniflar_verisi, personel_sayisi, depo_kapasite_ayarlari)

        for s_isim in siniflar_verisi.keys():
            env.process(uretici(env, s_isim, depo))

        env.run(until=sim_suresi)

    son_raf_seviyeleri = {s_isim: depo.depo_raflari[s_isim].level for s_isim in siniflar_verisi.keys()}

    st.session_state.sim_sonuclari = {
        'siniflar_verisi': siniflar_verisi,
        'toplam_mal_kabul_yuku': depo.toplam_mal_kabul_yuku,
        'personel_izleme': personel_izleme,
        'mal_kabul_izleme': mal_kabul_izleme,
        'son_raf_seviyeleri': son_raf_seviyeleri,
        'depo_kapasite_ayarlari': depo_kapasite_ayarlari
    }
    st.success("✅ Simülasyon Başarıyla Tamamlandı!")

# --- RAPORLAMA VE GÖRSELLEŞTİRME ALANI ---
if 'sim_sonuclari' in st.session_state:
    sonuclar = st.session_state.sim_sonuclari
    s_verisi = sonuclar['siniflar_verisi']
    
    toplam_islenen = sum(len(veri['beklemeler']) for veri in s_verisi.values())
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Depolanan Toplam Ürün Miktarı", value=f"{toplam_islenen} adet")
    col2.metric(label="Mal Kabul Alanında Kalan Ürün (Toplam)", value=f"{sonuclar['toplam_mal_kabul_yuku']} adet")
    col3.metric(label="Toplam Görevde İken Şarjı Biten Robot", value=f"{sum(v['yolda_kalan'] for v in s_verisi.values())} kez")

    st.subheader("📋 Sınıf Bazlı Operasyonel Rapor")
    rapor_data = []
    for s_isim, veri in s_verisi.items():
        sayi = len(veri['beklemeler'])
        ort_bekleme = sum(veri['beklemeler']) / sayi if sayi > 0 else 0.0
        max_bekleme = max(veri['beklemeler']) if sayi > 0 else 0.0
        
        max_kap = sonuclar['depo_kapasite_ayarlari'][s_isim]
        mevcut_stok = sonuclar['son_raf_seviyeleri'][s_isim]
        
        if max_kap == float('inf'):
            doluluk_metni = f"{mevcut_stok} / Sınırsız"
        else:
            yuzde = (mevcut_stok / max_kap) * 100
            doluluk_metni = f"{mevcut_stok} / {max_kap} (%{round(yuzde,1)})"
        
        # MATRİS METNİ BURADA OLUŞTURULUYOR
        kapasiteler = ", ".join([f"{k.replace('Sinif_', 'Sınıf ')} ({v} Adet)" for k, v in veri['tasima_kapasiteleri'].items()])
        
        rapor_data.append({
            "Sınıf Adı": veri['etiket'],
            "Taşıma Kabiliyeti Matrisi": kapasiteler, # Eklenen matris sütunu
            "Mevcut Raf Doluluğu / Kapasite": doluluk_metni,
            "Depolanan Ürün (Adet)": sayi,
            "Mal Kabul Ort. Bekleme (dk)": round(ort_bekleme, 2),
            "Mal Kabul Maks. Bekleme (dk)": round(max_bekleme, 2),
            "Bataryası Biten Robot": veri['yolda_kalan']
        })
    st.table(rapor_data)

    st.subheader("📊 Grafiksel Analiz Paneli")
    cmap = plt.get_cmap('tab10')
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        grafik_cizildi_mi = False
        for idx, (s_isim, veri) in enumerate(s_verisi.items()):
            if veri['beklemeler']:
                ax1.hist(veri['beklemeler'], bins=15, alpha=0.5, label=veri['etiket'], color=cmap(idx), edgecolor='black')
                grafik_cizildi_mi = True
        if not grafik_cizildi_mi:
            ax1.text(0.5, 0.5, 'Histogram için yeterli veri oluşmadı.', horizontalalignment='center', verticalalignment='center')
        else:
            ax1.legend()
        ax1.set_title('Sınıf Bazlı Ürünlerin Mal Kabul Alanında Bekleme Süreleri')
        ax1.set_xlabel('Dakika')
        ax1.set_ylabel('Frekans')
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1)

    with g_col2:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        aktiflik_cizildi_mi = False
        for idx, (s_isim, veri) in enumerate(s_verisi.items()):
            if veri['zamanlar'] and veri['kullanim']:
                ax2.step(veri['zamanlar'], veri['kullanim'], where='post', label=f"{veri['etiket']} Aktiflik %", color=cmap(idx), alpha=0.8)
                aktiflik_cizildi_mi = True
        if not aktiflik_cizildi_mi:
            ax2.text(0.5, 0.5, 'Aktiflik grafiği için yeterli veri oluşmadı.', horizontalalignment='center', verticalalignment='center')
        else:
            ax2.legend()
        ax2.set_title('Zamana Göre Robot Sınıflarının Aktiflik Oranı (%)')
        ax2.set_xlabel('Zaman (dk)')
        ax2.set_ylabel('Doluluk (%)')
        ax2.set_ylim(-5, 110)
        ax2.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig2)

    g_col3, g_col4 = st.columns(2)

    with g_col3:
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        p_izleme = sonuclar['personel_izleme']
        if len(p_izleme['zaman']) > 1:
            ax3.step(p_izleme['zaman'], p_izleme['kullanim_orani'], where='post', color='purple', linewidth=2, label='Teknisyen Doluluk %')
        ax3.set_title('Zamana Göre Bakım Personeli Kullanım Oranı (%)')
        ax3.set_xlabel('Zaman (dk)')
        ax3.set_ylabel('Personel Meşguliyet %')
        ax3.set_ylim(-5, 110)
        ax3.legend()
        ax3.grid(True, linestyle=':', color='purple', alpha=0.4)
        st.pyplot(fig3)

    with g_col4:
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        m_izleme = sonuclar['mal_kabul_izleme']
        
        m_cizildi_mi = False
        for idx, (s_isim, veri) in enumerate(m_izleme.items()):
            if len(veri['zaman']) > 1 and len(veri['alanda_bekleyen']) > 0:
                etiket_adi = s_verisi[s_isim]['etiket']
                ax4.plot(veri['zaman'], veri['alanda_bekleyen'], drawstyle='steps-post', label=f"{etiket_adi} Yükü", color=cmap(idx), alpha=0.8)
                m_cizildi_mi = True
                
        if not m_cizildi_mi:
            ax4.text(0.5, 0.5, 'Mal kabul verisi oluşmadı.', horizontalalignment='center', verticalalignment='center')
        else:
            ax4.legend(loc='upper right')
            
        ax4.set_title('Sınıf Bazlı Mal Kabul Alanında Bekleyen Anlık Ürün Sayısı')
        ax4.set_xlabel('Zaman (dk)')
        ax4.set_ylabel('Alandaki Ürün Miktarı (Adet)')
        ax4.grid(True, alpha=0.5)
        st.pyplot(fig4)
else:
    st.info("Simülasyonu çalıştırmak için sol menünün altındaki **Simülasyonu Başlat** butonuna basın.")