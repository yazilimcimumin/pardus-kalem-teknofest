# Pardus Akıllı Kalem ve Küresel Yakınlaştırma (Pinch-to-Zoom) Motoru ✒️🔍

Bu proje, **Teknofest Pardus Yerli Yazılım Yarışması 1. Talebi** kapsamında geliştirilmiştir. Sınıflardaki akıllı tahtalarda (Pardus ETAP) ve dokunmatik ekranlı Linux sistemlerinde görev yapan öğretmenlerin yaşadığı en büyük problemlerden biri olan **orijinal matematik föyleri veya PDF belgeleri üzerinde iki parmakla serbest yakınlaştırma (pinch-to-zoom) yapamama** ve **vektörel çizim aracı (geri alma eksikliği)** sorununu kökten çözer.

---

## 📌 Problem Tanımı
Mevcut çizim araçlarının yetersizliği, kararlı çalışan bir geri alma (Undo/Ctrl+Z) mekanizmasının bulunmaması ve öğretmenlerin akıllı tahta üzerinde Wine/Exe föy açıcılar ya da PDF okuyucular içindeyken iki parmakla pratik yakınlaştırma yapamamaları ders anlatım hızını ve kalitesini ciddi ölçüde düşürmektedir. Öğretmenler sürekli olarak PDF okuyucuların üst menülerindeki büyüteç ayarlarına bağımlı kalmaktadır.

---

## 🚀 Çözüm ve Geliştirme Stratejisi
**PyQt6** ve **QGraphicsView** mimarisi kullanılarak, düşük gecikmeli (low-latency) ve yüksek performanslı yeni bir **Pardus Kalem ve Jest Motoru** geliştirilmiştir. 

Bu modül ekranın üzerine tam saydam (transparent) bir katman olarak giydirilir. Sistem, X11/Wayland üzerinde çalışarak ekrandaki uygulamanın ne olduğundan bağımsız olarak (PDF okuyucu, Wine föy açıcı, web tarayıcı veya video) çalışır:
1. **Ekranı Dondurma (Screenshot Backdrop)**: Çizim moduna geçildiğinde anlık olarak masaüstünün yüksek çözünürlüklü bir ekran görüntüsü yakalanır ve çizim katmanının arka planına aktarılır.
2. **Küresel Yakınlaştırma (Pinch-to-Zoom & Pan)**: İki parmakla yapılan kıstırma hareketi algılandığında, hem arka plandaki ekran resmi hem de öğretmen tarafından çizilen vektör çizgileri **aynı anda, sıfır kaymayla ve pürüzsüzce** ölçeklendirilir.
3. **Sonsuz Çözünürlüklü Vektörel Nesneler**: Çizilen tüm çizgiler bellekte vektörel (`QGraphicsPathItem`) olarak tutulduğundan, döküman ne kadar büyütülürse büyütülsün çizimlerin çözünürlüğü bozulmaz, çizgiler net kalır.
4. **Hassas Vektörel Silgi (Stroke Collision)**: Silgi, diğer pikselleri bozmadan sadece hedeflenen vektörel çizgileri temas halinde tamamen siler.
5. **Kararlı Geri/İleri Al (Undo/Redo)**: Çizilen her çizgi ve silinen her eleman komut yığınında (Command Pattern) saklanır. `Ctrl+Z` ve `Ctrl+Y` adımları her ölçek seviyesinde kusursuz çalışır.

---

## ✨ Öne Çıkan Özellikler

* **Ultra Premium Glassmorphic Tasarım**: Pardus kurumsal kimliğine uygun, yarı saydam buzlu cam efekti, neon parıltılar, yumuşak yuvarlatılmış köşeler ve akıcı hover animasyonlarına sahip sürüklenebilir araç kutusu.
* **Küçültme Modu (Bubble View)**: Ekranı engellememek için araç kutusunu küçük, yüzen dairesel bir balona dönüştürebilme.
* **Kapsamlı Çizim Aletleri**: 
  * ✏️ **Akıllı Kalem**: İnce/Orta/Kalın ve Kırmızı, Mavi, Yeşil, Beyaz renk seçenekleri.
  * ✒️ **Vurgulayıcı**: Yazıların üstünü çizmek için yarı şeffaf fosforlu kalem.
  * 📐 **Akıllı Şekiller**: Düz Çizgi, Yön Oku (Ok çizim asistanı ile kusursuz açılı oklar), Dikdörtgen ve Daire.
  * 🧼 **Hassas Silgi**: Dokunulduğunda tüm çizgiyi yok eden akıllı vektörel silgi.
* **İki Parmakla Yakınlaştırma ve Kaydırma**: İki parmakla ekranı çimdikleyerek büyütme, küçültme ve iki parmakla tuval üzerinde kayma.
* **🔍 Yakınlaştırma HUD Göstergesi**: Ekranda o anki yakınlaştırma oranını (%50 - %800) gösteren şık, yarı saydam kayar kapsül göstergesi.
* **⌨️ Klavye Desteği**: Tahta klavyeleri veya uzaktan kumandalar için `Ctrl+Z` (Geri Al) ve `Ctrl+Y` (İleri Al) kısayolları.
* **🖥️ Wayland & X11 Desteği**: XWayland stays-on-top uyumluluk katmanı sayesinde kararlı çalışma garantisi.

---

## 🛠️ Teknoloji Yığını (Tech Stack)

* **Dil**: Python 3.12+
* **Arayüz Framework**: PyQt6 (Qt 6.11+)
* **Grafik Motoru**: QGraphicsView / QGraphicsScene (GPU Donanım Hızlandırmalı Render ve Çift Tamponlama)
* **Dokunmatik Giriş İşleyici**: QTouchEvent tabanlı özel Çoklu Dokunma Hesaplama Motoru (Euclidean Distance & Midpoint tracking)
* **Tasarım Dili**: QSS (Qt Style Sheets) ile Premium Dark-Mode Glassmorphism

---

## 🚀 Çalıştırma Talimatları

Uygulamayı Pardus veya herhangi bir Linux dağıtımında çalıştırmak son derece kolaydır. Sisteminizde python3 kurulu olmalıdır.

### 1. Kurulum ve Bağımlılıklar
Aşağıdaki adımlarla sanal ortamı kurun ve PyQt6 yüklemesini gerçekleştirin (Uygulama dizinindeyken):
```bash
# Sanal ortam oluşturun
python3 -m venv venv

# Sanal ortamı aktifleştirip PyQt6 kurun
./venv/bin/pip install --upgrade pip
./venv/bin/pip install PyQt6
```

### 2. Uygulamayı Başlatma
Başlatıcı scriptimize çalışma izni verin ve çalıştırın:
```bash
chmod +x run.sh
./run.sh
```

---

## 📂 Proje Yapısı

```
Talep1/
├── venv/                       # Sanal Ortam Klasörü
├── core/
│   ├── engine.py               # Çizim Ayarları ve Kararlı Undo/Redo Yığın Motoru
│   └── gestures.py             # Düşük Gecikmeli Pinch-to-Zoom Hesaplayıcı
├── widgets/
│   ├── canvas.py               # Tam Ekran Çizim Katmanı, Ekran Görüntüsü Yakalayıcı ve HUD
│   └── toolbar.py              # Sürüklenebilir Glassmorphism Araç Çubuğu ve Vektör İkonlar
├── pardus_kalem.py             # Uygulama Giriş Kapısı ve Yaşam Döngüsü Koordinatörü
├── run.sh                      # Tek Tıklamayla Çalıştırma Scripti
├── .gitignore                  # Git klasör temizleyici
└── README.md                   # Proje dokümantasyonu
```

---

## 👨‍💻 Geliştirici Notu
Pardus ekosistemini güçlendirmek ve eğitimde yerli yazılım kullanımını üst seviyeye taşımak amacıyla geliştirilen bu modül, tüm akıllı tahtalarla tam uyumlu olup sınıf içi deneyimi eşsiz bir seviyeye çıkarmaktadır.
