#!/bin/bash
# Pardus Akıllı Kalem - Tek Tıkla Kurulum ve Entegrasyon Sistemi
# Bu script, uygulamayı Pardus/ETAP tahtalara kurar ve Masaüstüne / Başlangıç Menüsüne kısayol ekler.

# Renk tanımları
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # Renksiz

echo -e "${CYAN}================================================================${NC}"
echo -e "${GREEN}    Pardus Akıllı Kalem & Küresel Yakınlaştırma Motoru Kurulumu   ${NC}"
echo -e "${CYAN}================================================================${NC}"

# Script dizinini tespit et
SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SRC_DIR"

# 1. Kurulum Türünü Belirle (Root vs Normal Kullanıcı)
if [ "$EUID" -eq 0 ]; then
    # Sistem genelinde kurulum (Sudo yetkisiyle çalıştırıldıysa)
    echo -e "${BLUE}[Bilgi] Kurulum sistem genelinde (/opt) yapılacaktır...${NC}"
    INSTALL_DIR="/opt/pardus-kalem"
    DESKTOP_DIR="/usr/share/applications"
    USER_DESKTOP_PATHS=()
    
    # Tüm normal kullanıcıların masaüstü yollarını topla
    for user_home in /home/*; do
        if [ -d "$user_home" ]; then
            # Türkçe ve İngilizce Masaüstü klasörlerini kontrol et
            if [ -d "$user_home/Masaüstü" ]; then
                USER_DESKTOP_PATHS+=("$user_home/Masaüstü")
            elif [ -d "$user_home/Desktop" ]; then
                USER_DESKTOP_PATHS+=("$user_home/Desktop")
            fi
        fi
    done
else
    # Sadece mevcut kullanıcı için kurulum (Sudo gerektirmez!)
    echo -e "${BLUE}[Bilgi] Kurulum mevcut kullanıcı düzeyinde (~/.local/share) yapılacaktır...${NC}"
    INSTALL_DIR="$HOME/.local/share/pardus-kalem"
    DESKTOP_DIR="$HOME/.local/share/applications"
    USER_DESKTOP_PATHS=()
    
    # Mevcut kullanıcının masaüstü yolu
    if [ -d "$HOME/Masaüstü" ]; then
        USER_DESKTOP_PATHS+=("$HOME/Masaüstü")
    elif [ -d "$HOME/Desktop" ]; then
        USER_DESKTOP_PATHS+=("$HOME/Desktop")
    fi
fi

# 2. Kurulum Dizinlerini Oluştur ve Dosyaları Kopyala
echo -e "${CYAN}[1/4] Dosyalar hedef konuma aktarılıyor...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"

# Gerekli dosyaları kopyala
cp -r core "$INSTALL_DIR/"
cp -r widgets "$INSTALL_DIR/"
cp pardus_kalem.py "$INSTALL_DIR/"
cp run.sh "$INSTALL_DIR/"
cp icon.png "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/run.sh"

echo -e "${GREEN}✔ Dosyalar başarıyla kopyalandı: $INSTALL_DIR${NC}"

# 3. Sanal Ortamı Hazırla (Python Venv)
echo -e "${CYAN}[2/4] Python sanal ortamı yapılandırılıyor (Bağımlılıklar kuruluyor)...${NC}"
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install PyQt6

echo -e "${GREEN}✔ Sanal ortam ve PyQt6 bağımlılıkları tamamlandı.${NC}"

# 4. Desktop Entry (Kısayol) Oluştur
echo -e "${CYAN}[3/4] Sistem kısayolları ve menü entegrasyonu yapılıyor...${NC}"
DESKTOP_FILE="pardus-kalem.desktop"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=Pardus Akıllı Kalem
Comment=Pardus ve ETAP için Dokunmatik Çizim ve Yakınlaştırma Motoru
Exec=$INSTALL_DIR/run.sh
Icon=$INSTALL_DIR/icon.png
Terminal=false
Categories=Education;Utility;Graphics;
StartupNotify=true
X-KeepTerminal=false
EOF

# Uygulama menüsüne kısayolu kopyala
cp "$DESKTOP_FILE" "$DESKTOP_DIR/"
chmod +x "$DESKTOP_DIR/$DESKTOP_FILE"

# 5. Masaüstü Simgesini Yerleştir ve Güvenli/Çalıştırılabilir Olarak İşaretle
echo -e "${CYAN}[4/4] Masaüstü kısayolu oluşturuluyor...${NC}"
for desktop_path in "${USER_DESKTOP_PATHS[@]}"; do
    if [ -d "$desktop_path" ]; then
        TARGET_SHORTCUT="$desktop_path/$DESKTOP_FILE"
        cp "$DESKTOP_FILE" "$TARGET_SHORTCUT"
        chmod +x "$TARGET_SHORTCUT"
        
        # XFCE/KDE masaüstünde "Güvenilmeyen Kısayol" uyarısını engellemek için GIO metadata ekle
        if command -v gio &> /dev/null; then
            gio set "$TARGET_SHORTCUT" "metadata::trusted" yes 2>/dev/null
            echo -e "${GREEN}✔ Kısayol güvenli olarak işaretlendi: $TARGET_SHORTCUT${NC}"
        else
            echo -e "${BLUE}ℹ Kısayol masaüstüne eklendi: $TARGET_SHORTCUT${NC}"
        fi
    fi
done

# Geçici oluşturulan .desktop dosyasını temizle
rm "$DESKTOP_FILE"

echo -e "${CYAN}================================================================${NC}"
echo -e "${GREEN}   🎉 PARDUS AKILLI KALEM BAŞARIYLA KURULDU VE ENTEGRE EDİLDİ! ${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "${BLUE}Kurulum Konumu:${NC} $INSTALL_DIR"
echo -e "${BLUE}Masaüstü ve Pardus Başlangıç Menüsünde 'Pardus Akıllı Kalem' adıyla bulabilirsiniz.${NC}"
echo -e "${GREEN}İyi dersler dileriz! ✏️🔍${NC}"
EOF
