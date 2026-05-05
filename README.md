# AKILLI DEPO ROBOT ATAMA SİSTEMİ SİMÜLASYONU ANALİZ RAPORU

## 1. Giriş ve Amaç
Bu çalışma, bir akıllı depo içerisinde farklı ağırlıklara sahip ürünlerin, kendi
ağırlıklarına göre atanmış robotlar tarafından taşınma sürecini
modellemektedir.

**Simülasyonun temel amacı;** belirlenen robot sayıları ve ürün geliş hızları
altında sistemin darboğazlarını tespit etmek, bekleme sürelerini analiz etmek
ve kaynak kullanım verimliliğini ölçmektir.

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
- **Görselleştirme:** Bekleme sürelerinin dağılımını göstermek için **histogram** kullanılmıştır. Robot kullanım oranlarını zamana
bağlı değişimini göstermek için **step chart** tercih edilmiştir.
- **UI (Arayüz):** Projenin görselleştirilmiş kullanıcı arayüzü için **Streamlit** kullanılması planlanmaktadır.
