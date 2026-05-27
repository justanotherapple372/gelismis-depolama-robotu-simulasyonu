# 🏢 Akıllı Depo Dijital İkizi Simülasyonu

Bu proje; modern, çok sınıflı ve otonom robotların görev yaptığı akıllı depo sistemlerinin davranışlarını analiz etmek, darboğazları tespit etmek ve kapasite planlaması yapmak için geliştirilmiş **etkileşimli bir ayrık olay simülasyonu**.  

Arka planda **SimPy** ayrık olaylı simülasyon (Discrete-Event Simulation) motorunu kullanırken, ön yüzde kullanıcı etkileşimi ve anlık görselleştirme için **Streamlit** altyapısından faydalanır.
---

### 🛠️ Kullanılan Teknolojiler ve Paketler

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![SimPy](https://img.shields.io/badge/SimPy-A9A9A9?style=for-the-badge&logo=python-foundation-is-a-member-of-the-python-software-foundation&logoColor=black)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

## 🚀 Öne Çıkan Özellikler

* **Dinamik Sınıf Yönetimi:** Kullanıcı tanımlı sayıda ürün ve robot sınıfı ($N$ adet sınıf) oluşturabilme.
* **Çapraz Taşıma ve Kapasite Matrisi:** Sınıflar arası esnek görev atama. Bir sınıfın robotu, ağırlık veya hacim kısıtlarına göre diğer sınıfların ürünlerini farklı taşıma kapasiteleriyle taşıyabilir.
* **Gelişmiş Olasılık Dağılımları:** Ürün taşıma süreleri için **Uniform (Düzgün)**, **Normal (Gauss)** veya **Triangular (Üçgensel)** dağılım modelleri seçimi.
* **Stok Kısıtları & Mal Kabul Kesintisi:** Sınırlı/sınırsız raf kapasitesi simülasyonu. Raf dolduğunda otomatik süreç durdurma yönetimi.
* **Kritik Şarj ve Teknisyen Kurtarma Döngüsü:** Görev esnasında şarjı kritik eşiğin altına düşen robotların şarj istasyonuna yönlendirilmesi; şarjı tamamen biten robotların ise kısıtlı sayıdaki bakım personeli (teknisyen) tarafından kurtarılma senaryosu.
* **Zengin Analitik Raporlama:** Matplotlib entegrasyonu ile doluluk, histogram beklemeleri, personel verimliliği ve anlık kuyruk analizi grafikleri.

---

## 🛠️ Mimari ve İş Akışı (Logics)

Simülasyonun temel işleyiş mantığı şu adımları izler:

1.  **Üretici (Poisson Süreci):** Ürünler, parametrik olarak girilen geliş aralıklarına göre Üstel Dağılım (`random.expovariate`) ile mal kabul alanına giriş yapar.
2.  **Robot Tahsisi (`simpy.AnyOf`):** Mal kabul alanına gelen bir ürün, kendisini taşımaya yetkili (kendi sınıfı veya çapraz tanımlanmış) en hızlı boşa çıkan robot havuzundan (`simpy.Store`) bir robot talep eder.
3.  **Kapasite Kontrolü:** Robot, mal kabul alanından tek seferde taşıyabileceği maksimum ürün adedi kadar ürünü yükler (raf kapasitesinin aşılmaması şartıyla).
4.  **Enerji / Arıza Yönetimi:**
    * Eğer robotun şarjı taşıma süresinden **uzunsa**; görev tamamlanır, raf konteyner seviyesi artar ve şarj durumuna göre robot istasyona veya havuza döner.
    * Eğer robotun şarjı yolda **biterse**; robot `ARIZALI` durumuna geçer. Sınırlı kaynak olan teknisyen (`simpy.Resource`) kuyruğuna girer. Teknisyen robotu kurtardıktan sonra robot şarj sürecine dahil edilir.

---

## 📊 Ekran Görüntüleri ve Analiz Panelleri

Simülasyon başarıyla tamamlandığında sistem aşağıdaki 4 temel metrik grafiğini dinamik olarak üretir:

* **Mal Kabul Bekleme Süreleri Histogramı:** Hangi ürün sınıfının depoya yerleşmek için ne kadar süre kuyrukta beklediğinin frekans dağılımı.
* **Robot Sınıfları Aktiflik Oranı (%):** Zamana bağlı olarak robot filolarının kapasite kullanım oranları.
* **Bakım Personeli Meşguliyet Oranı (%):** Teknisyenlerin süreç boyunca ne kadar verimli çalıştığı ve darboğaz oluşturup oluşturmadığı.
* **Anlık Mal Kabul Yükü:** Depo giriş alanında biriken anlık palet/ürün sayısının zaman serisi grafiği.

---

## 💻 Kurulum ve Çalıştırma

Projenizi yerel ortamınızda ayağa kaldırmak için aşağıdaki adımları takip edebilirsiniz.

### 1. Gereksinimlerin Yüklenmesi

Öncelikle projenin çalışması için gerekli kütüphaneleri yükleyin:
`pip install streamlit simpy matplotlib`

## 2. Uygulamayı Başlatma

Proje dosyasının bulunduğu dizinde terminal üzerinden şu komutu çalıştırın:
`streamlit run app.py`

Giriş yaptıktan sonra tarayıcınızda otomatik olarak açılan **http://localhost:8501** adresinden dijital ikiz paneline erişebilirsiniz.

# ⚙️ Parametre KılavuzuParametre 

Parametre Alanı,Açıklama

Tanımlanacak Sınıf Sayısı | Depodaki bağımsız ürün tipi ve robot filosu varyasyon sayısını belirler.
--- | ---
Bakım Personeli Sayısı | Yolda kalan robotlara müdahale edebilecek eşzamanlı maksimum teknisyen sayısıdır.
Kritik Şarj Eşiği (%) | Robotların görev sonrası şarj istasyonuna gitmeye karar verme yüzdesidir.
Ürün Geliş Aralığı (dk) | İlgili sınıfa ait ürünlerin ortalama geliş sıklığıdır (Poisson akışı).
Taşıma Süresi Dağılımı | Robotun yükleme noktasından rafa gidiş-dönüş süresinin matematiksel karakteristiğidir.
