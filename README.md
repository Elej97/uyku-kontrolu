# 💤 Göz Kapakları Kapanınca Uyku Modu ve Geri Sayım Sistemi

Bu proje, kullanıcının göz kapaklarının kapandığını (uykuya geçiş anını) gerçek zamanlı olarak algılayan ve belirlenen süre boyunca kapalı kaldığında otomatik olarak hedeflenen YouTube linkini açan **iki farklı** versiyona (Python & Web) sahip akıllı bir takip sistemidir.

Proje, hem yerel makinenizde Python ile çalıştırılabilir hem de tamamen tarayıcı üzerinden (GitHub Pages vb.) bir web bağlantısı olarak kullanılabilir.

---

## 🚀 Proje Sürümleri

### 1. Web Sürümü (`index.html`) - *Önerilen & Kolay Kurulum*
Tarayıcınızın kamerasını ve **MediaPipe Face Mesh (CDN)** teknolojisini kullanan, kurulum gerektirmeyen versiyondur. 

*   **Canlı Demo / Link Yapma**: Bu projeyi GitHub'a yüklediğinizde, repository ayarlarından **GitHub Pages**'ı aktif ederek doğrudan internete açık bir link haline getirebilirsiniz!
*   **Özellikler**:
    *   Cam morfizasyonlu (Glassmorphic) premium karanlık tema arayüzü.
    *   Göz açıklık oranlarını (EAR) canlı gösteren grafik göstergeler.
    *   Tarayıcı üzerinden anlık olarak değiştirilebilen **EAR Eşiği**, **Geri Sayım Süresi**, **Bekleme Süresi** ve **YouTube Video Linki**.
    *   Sol üstte dinamik yeşil dolum halkası animasyonu.

#### Çalıştırma:
1. `index.html` dosyasını tarayıcınızda (Chrome, Edge vb.) çift tıklayarak açın.
2. Kamera izni verin.
3. Gözlerinizi kapatıp sistemi test edin!

---

### 2. Python Sürümü (`tel.py`)
Yerel bilgisayarınızda OpenCV ve MediaPipe Face Mesh kütüphanelerini kullanarak çalışan Python versiyonudur.

#### Kurulum:
Gerekli kütüphaneleri yüklemek için terminalde aşağıdaki komutları çalıştırın:
```bash
pip install mediapipe==0.10.14 opencv-python opencv-contrib-python matplotlib numpy
```

#### Çalıştırma:
```bash
python tel.py
```
*   Çıkmak için klavyeden `Q` veya `ESC` tuşlarına basabilir, ya da pencerenin sağ üstündeki **(X)** kapatma butonuna tıklayabilirsiniz.

---

## 📊 EAR (Eye Aspect Ratio - Göz Açıklık Oranı) Kalibrasyonu

Gözlerinizin kapalı olup olmadığını anlamak için **EAR** formülü kullanılır. Yüzün yapısına, kameranın açısına veya ışık koşullarına göre bu eşik değerinin kalibre edilmesi gerekebilir.

1. **Açık Göz Değeri**: Ekrandaki/terminaldeki `EAR` değerlerini izleyin. Gözleriniz açıkken bu değer genellikle `0.25 - 0.35` arasındadır.
2. **Kapalı Göz Değeri**: Gözlerinizi kapattığınızda bu değer `0.15 - 0.20` seviyelerine düşer.
3. **Hassasiyet Ayarı**:
    *   **Web Sürümünde**: Sağ paneldeki kaydırıcıyı (Slider) kullanarak eşiği anında güncelleyebilirsiniz.
    *   **Python Sürümünde**: `tel.py` içindeki `EAR_THRESHOLD` (varsayılan: `0.21`) parametresini düzenleyebilirsiniz.

---

## ⚙️ Genel Ayarlar

Her iki sürümde de aşağıdaki ayarları kendinize göre değiştirebilirsiniz:
*   `YOUTUBE_URL`: Gözler kapandığında açılacak olan video linki.
*   `COUNTDOWN_TARGET`: Gözlerin kaç saniye boyunca sürekli kapalı kalması gerektiği (Varsayılan: 3s).
*   `COOLDOWN_SECONDS`: Video açıldıktan sonra kazara tekrar tetiklenmemesi için beklenecek süre (Varsayılan: 15s).
