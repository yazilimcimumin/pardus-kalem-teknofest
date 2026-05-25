# Pardus Akıllı Kalem & Jest Motoru Kullanım Rehberi ✏️🔍

Bu rehber, **Pardus Akıllı Kalem & Küresel Yakınlaştırma (Pinch-to-Zoom) Motoru** uygulamasının tüm özelliklerini, kurulum adımlarını ve akıllı tahta (ETAP) ortamındaki pratik kullanım yöntemlerini detaylandırmak amacıyla hazırlanmıştır.

---

## 🌟 Öne Çıkan Özellikler

Pardus Akıllı Kalem, öğretmenlerin alışık olduğu **Fatih Kalem** deneyimini modern **Pardus Linux** ve akıllı tahta (ETAP) standartlarına taşır:

1. **Fatih Kalem Stili Kompakt Tasarım (Yatay Şerit)**:
   - Araç çubuğu dikey olarak yer kaplamak yerine yatay, modern, yuvarlatılmış ve **Glassmorphism (Buzlu Cam)** efektine sahip bir şerit halinde sunulur.
   - Ekranda istenilen yere sürüklenip bırakılabilir.

2. **Otomatik Küçülme (Kabarcık / Bubble Modu)**:
   - **İşaretçi (Mouse) Moduna** geçildiğinde, araç kutusu masaüstünde yer kaplamaması için otomatik olarak ekranın köşesinde küçük, dairesel bir kabarcığa (`[ ✏️ ]`) dönüşür.
   - Kabarcığa tekrar tıklandığında anında son kaldığı çizim aracıyla tam ekran moduna geri döner.

3. **Mavi Çerçeve Mod Bildirimi**:
   - Çizim modu aktif olduğunda, ekranın etrafını **4px kalınlığında parlak mavi bir çerçeve** kaplar.
   - Bu çerçeve, öğretmenlerin o sırada çizim modunda olduklarını ve ekrana dokunduklarında tahtayı kontrol etmek yerine çizim yapacaklarını anlamalarını sağlar.

4. **Sıfır Gecikmeli Pinch-to-Zoom ve Pan**:
   - İki parmakla kıstırma (**Pinch-to-Zoom**) ve kaydırma (**Pan**) hareketleri ile masaüstü arka planı ve çizimleriniz **birlikte, sıfır gecikmeyle** yakınlaştırılır veya uzaklaştırılır.
   - PDF dökümanları veya Wine üzerinde çalışan föy açıcılar çözünürlükleri bozulmadan devasa boyutlara büyütülebilir.

5. **Dinamik ve Akıllı Silgi**:
   - Silgi boyutu, kalem boyutunun **tam 4 katı** olacak şekilde dinamik olarak ayarlanır. Böylece kalın çizgileri silmek için tahtayı saatlerce ovalamak yerine tek dokunuşla silebilirsiniz.

6. **Gelişmiş Renk ve Boyut Yönetimi**:
   - **Hızlı Renkler**: Siyah (İlk Sırada), Kırmızı, Mavi ve Yeşil dairesel butonları ile hızlıca renk değiştirilebilir.
   - **Çift Tıklama ile Tam Palet**: Renk paletine veya hızlı renk butonlarına **çift tıklandığında** standart `QColorDialog` açılarak milyonlarca renk arasından seçim yapılabilir.
   - **Tek Global Boyut Slider'ı**: Tüm araçların boyutunu tek noktadan yöneten, içinde canlı boyut önizleme dairesi barındıran şık bir sürgü paneline sahiptir.

---

## 🛠️ Araç Çubuğu Kılavuzu

Yatay araç çubuğundaki düğmeler sırasıyla şu şekildedir:

| Simge | Araç Adı | Açıklama |
| :---: | :--- | :--- |
| `⋮` | **Sürükleme Kolu** | Araç çubuğunu ekranda istediğiniz yere taşımak için bu alandan tutun. |
| 🖱️ | **İşaretçi Modu** | Çizim modunu kapatır, ekranı çözer ve araç kutusunu küçük bir kabarcığa küçültür. Masaüstündeki diğer pencereleri yönetmenizi sağlar. |
| ✏️ | **Çizim Kalemi** | İnce ve hassas vektörel çizimler yapmanızı sağlar. |
| 🖍️ | **Fosforlu Kalem** | Dökümanların üzerini çizmek için yarı şeffaf, kalın vurgulayıcı kalem. |
| 🧼 | **Vektörel Silgi** | Çizgilere temas ettiği anda ilgili çizimi tamamen kaldıran akıllı silgi (Boyutu kalem boyutunun 4 katıdır). |
| 📐 | **Geometrik Şekiller** | Tıklandığında açılan alt menüden; *Düz Çizgi, Yön Oku, Dikdörtgen ve Daire* çizim araçlarını seçebilirsiniz. |
| 🎨 | **Renk Paleti** | Tıklandığında Siyah, Kırmızı, Mavi, Yeşil hızlı seçim dairesi ve Özel Renk Butonu açılır. Çift tıklama ile tam palet açılır. |
| 📏 | **Boyut Ayarı** | Canlı önizleme dairesi içeren ve tüm araçların boyutunu değiştiren global sürgüyü (slider) açar. |
| ↩️ | **Geri Al** | Yapılan son çizimi veya silme işlemini geri alır (`Ctrl+Z`). |
| ↪️ | **İleri Al** | Geri alınan işlemi ileri alır (`Ctrl+Y`). |
| 🗑️ | **Ekranı Temizle** | Ekrandaki tüm çizimleri tek seferde siler (Geri alınabilir!). |
| ❌ | **Çıkış** | Uygulamadan tamamen çıkar. |

---

## ⌨️ Klavye Kısayolları

Özellikle klavyeli veya grafik tabletli kullanımlarda hız kazanmak için şu kısayolları kullanabilirsiniz:

- **`Ctrl + Z`**: Geri Al (Undo)
- **`Ctrl + Y`**: İleri Al (Redo)

---

## 🚀 Kurulum ve Çalıştırma

Pardus Kalem, akıllı tahtalara tek tıkla kurulabilecek şekilde paketlenmiştir.

### 1. Kolay Başlatma (Klasör İçinden)
Uygulamayı kurmadan, doğrudan klasör içinden çalıştırmak için terminalde şu komutu vermeniz yeterlidir:
```bash
./run.sh
```
*(Eğer sanal ortam kurulu değilse otomatik uyaracaktır)*

### 2. Akıllı Tahtaya / Sisteme Kurulum (Önerilen)
Öğretmenlerin uygulamayı tahta açılır açılmaz kullanabilmesi, Masaüstünde ve Başlangıç Menüsünde (Uygulama Menüsü) kısayol olarak bulabilmesi için özel `install.sh` scripti hazırlanmıştır.

**Sadece Mevcut Kullanıcı İçin Kurulum (Sudo Şifresi Gerektirmez):**
```bash
./install.sh
```
Bu komut uygulamayı mevcut kullanıcının dizinine (`~/.local/share/pardus-kalem`) kurar, masaüstüne çalıştırılabilir bir kısayol atar ve Pardus menüsüne ekler.

**Tüm Tahta Genelinde Kurulum (Yönetici Yetkisi ile):**
```bash
sudo ./install.sh
```
Uygulamayı `/opt/pardus-kalem` altına kurarak tahtadaki tüm kullanıcı hesapları (Öğretmen, Öğrenci vb.) için masaüstü kısayollarını otomatik olarak hazırlar.

---

## 💡 İpuçları ve En İyi Deneyim

- **Masaüstüne Hızlı Dönüş**: Sınıfta bir öğrenci tahtaya soru çözmeye kalktığında veya dökümanı değiştirmeniz gerektiğinde `🖱️` (İşaretçi) simgesine basın. Araç kutusu anında sağ alt köşede minik bir daireye dönüşecek ve ekranda ders dökümanı tam boy kalacaktır. Tekrar dokunduğunuzda kaldığınız yerden çizmeye devam edebilirsiniz.
- **Daha Büyük Silgi**: Kalem boyutu slider'ını artırdığınızda silginizin boyutu da otomatik olarak büyüyecektir. Büyük alanları silmek için kalem boyutunu artırıp silgiyi kullanabilirsiniz.
- **İki Parmak Jestleri**: Yakınlaştırma yaparken iki parmağınızı ekrana dokundurup açın. Kaydırma yapmak için ise iki parmağınızı basılı tutarak ekranda sürükleyin.
