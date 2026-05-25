#!/bin/bash
# Pardus Akıllı Kalem & Pinch-to-Zoom Motoru Başlatıcı Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Hata: venv (Sanal ortam) bulunamadı!"
    echo "Lütfen önce sanal ortamı kurun veya venv oluşturun."
    exit 1
fi

echo "Pardus Akıllı Kalem ve Küresel Yakınlaştırma Motoru başlatılıyor..."
./venv/bin/python3 pardus_kalem.py "$@"
