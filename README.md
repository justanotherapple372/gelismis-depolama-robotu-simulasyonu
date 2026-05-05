# AKILLI DEPO ROBOT ATAMA SİSTEMİ SİMÜLASYONU ANALİZ RAPORU

## 1. Giriş ve Amaç
Bu çalışma, bir akıllı depo içerisinde farklı ağırlıklara sahip ürünlerin, kendi ağırlıklarına göre atanmış robotlar tarafından taşınma sürecini modellemektedir.

**Simülasyonun temel amacı;** belirlenen robot sayıları ve ürün geliş hızları altında sistemin darboğazlarını tespit etmek, bekleme sürelerini analiz etmek ve kaynak kullanım verimliliğini ölçmektir.

## 2. Sistem Mimarisi ve Metodoloji

Simülasyon, **Python dili** ve **SimPy** kütüphanesi kullanılarak geliştirilmiştir. Sistem üç ana bileşenden oluşmaktadır:
- Varlıklar (Entities): Hafif (A), Orta (B) ve Ağır (C) ağırlıklara sahip tipindeki ürün veya içinde ürün olan konteynerler.
- Kaynaklar (Resources): Projedeki robotları temsil eder.
- Süreçler:
    - Üretici (Producer): Ürünlerin gelişini üstel dağılıma göre tetikler.
    - Taşıma (Process): Ürünlerin robotlar tarafından taşınmasını uniform dağılıma göre simüle eder.


## 3. Kullanılan Teknoloji, Kütüphane, Veri Seti, Görselleştirme ve UI:

- **Python:** Simülasyon modelinin geliştirilmesi için kullanılan ana programlama dili.
    - **Simpy:** Ayrık olay simülasyonu modelini oluşturmak için kullanılan temel kütüphane.
    - **matplotlib:** Simülasyon sonuçlarının grafiksel olarak görselleştirilmesini sağlayan kütüphane.
- **Veri Seti:**
    - Gerçek bir veri seti kullanılmamıştır yani kendimiz oluşturduk.
    - Ürün geliş zamanları **Üstel Dağılım (Exponential Distribution)** ile, taşıma süreleri ise **Düzgün Dağılım (Uniform Distribution)** ile rastgele oluşturulmuştur.
- **Görselleştirme:** Bekleme sürelerinin dağılımını göstermek için **histogram** kullanılmıştır. Robot kullanım oranlarını zamana bağlı değişimini göstermek için **step chart** tercih edilmiştir.
- **UI (Arayüz):** Projenin görselleştirilmiş kullanıcı arayüzü için **Streamlit** kullanılması planlanmaktadır.

## 4. Parametre Tanımlamaları

Sistem, kullanıcıdan alınan şu değişkenler üzerine kurulmuştur:
- **Geliş Aralığı:** Ürünlerin sisteme giriş sıklığı (dk).
- **Taşıma Süresi (Min/Max):** Robotun bir ürünü teslim etme süresi.
- **Simülasyon süresi:** Toplam simüle süresi.

## 5. Algoritma Akışı:

Sistemin çalışma mantığı aşağıdaki adımları izlemektedir:

1) **Üretici (Producer):** Belirlenen ortalama süreye göre rastgele zamanlarda ürün nesneleri oluşturur.
2) **Sıralama (Queuing):** Gelen ürün, boşta bir robot olup olmadığını kontrol eder. Eğer tüm robotlar meşgulse, ürün **"talep"** sırasında bekler.
3) **İşlem (Processing):** Robot tahsis edildiğinde, taşıma süresi kadar zaman geçer.
4) **Serbest Bırakma (Release):** İşlem bittiğinde robot serbest bırakılır ve sıradaki ürün işleme alınır.

## 6. Performans Göstergeleri (Metrikler)

Raporun en önemli kısmını oluşturan grafiklerin teknik açıklamaları şöyledir:
- Bekleme Süreleri Dağılımı (Histogram): Bu grafik, sistemin hizmet kalitesini ölçer.
    – Verimlilik Göstergesi: Histogramın sol tarafa (0'a yakın) yığılması, sistemin akıcı olduğunu gösterir.
    – Darboğaz Analizi: Histogramın sağa doğru uzayan bir "kuyruk" (tail) oluşturması, bazı ürünlerin aşırı beklediğini ve sistemin doyuma ulaştığını kanıtlar.
- Anlık Robot Kullanımı (Step Chart): Bu grafik, kaynağın yani robotların kullanım oranını analiz eder.
    – Kapasite Planlama: Grafiğin sürekli değerin tavan çizgisi seyretmesi, sistemin yetersiz olduğunu ve daha fazla robot yatırımına ihtiyaç duyulduğunu gösterir.
    – Durağanlık: Grafikteki dalgalanmalar, sistemin yoğun ve sakin saatlerini ayırt etmemizi sağlar.
- İşlenen Ürün Sayısı, Ortalama ve Maksimum Bekleme sürelerinin hesaplanması.

## 7. Senaryo #1: Yetersiz Robot Sayısı

Bu senaryoda amacımız, robotların sürekli %100 dolulukta çalışmasını ve bekleme kuyruğunun zamanla doğrusal olarak artmasını
sağlamaktır

![Simülasyon Diyagramı](grafikler/1inputlar.png)

![Simülasyon Diyagramı](grafikler/1simulasyonOzet.png)

![Simülasyon Diyagramı](grafikler/1grafik.png)

