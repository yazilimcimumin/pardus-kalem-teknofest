import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

# Proje yollarını ekle (içe aktarmalar için)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import DrawingEngine, ToolMode
from widgets.canvas import CanvasOverlay
from widgets.toolbar import FloatingToolbar

class PardusKalemApp:
    """Akıllı Kalem uygulamasının koordinasyonunu ve ana yaşam döngüsünü yöneten sınıf"""
    def __init__(self):
        # 1. Çekirdek Çizim Motoru
        self.engine = DrawingEngine()

        # 2. Tam Ekran Çizim Katmanı (Gizli başlar)
        self.canvas = CanvasOverlay(self.engine)
        
        # Ekran Boyutlarını Algıla ve Canvas'ı Kapla
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            self.canvas.setGeometry(screen_geometry)
        else:
            self.canvas.showFullScreen() # Güvenli yedekleme

        # 3. Yüzer Modern Araç Çubuğu
        self.toolbar = FloatingToolbar(self.engine)
        
        # Araç çubuğunu başlangıçta ekranın sağ-orta tarafına yerleştir
        geom = self.canvas.geometry()
        tb_x = geom.width() - 80
        tb_y = int((geom.height() - self.toolbar.height()) / 2)
        if tb_y < 50:
            tb_y = 100
        self.toolbar.move(tb_x, tb_y)
        self.toolbar.show()

        # Sinyal ve Olay Bağlantıları
        self.setup_connections()

        # Varsayılan mod olan "Çizim Modu" ile başlat
        self.canvas.freeze_screen(self.toolbar)
        self.canvas.show()
        self.canvas.raise_()
        self.toolbar.raise_()

    def setup_connections(self):
        # Araç Çubuğu -> Çizim Katmanı Mod Geçişleri
        self.toolbar.mode_changed.connect(self.on_mode_changed)
        
        # Araç Çubuğu -> Çekirdek İşlemler (Undo / Redo / Clear / Close)
        self.toolbar.undo_requested.connect(self.trigger_undo)
        self.toolbar.redo_requested.connect(self.trigger_redo)
        self.toolbar.clear_requested.connect(self.canvas.clear_canvas)
        self.toolbar.close_requested.connect(QApplication.quit)

        # KLAVYE KISAYOLLARI (Ctrl+Z ve Ctrl+Y)
        # Çizim katmanı açıkken öğretmen klavyeden de geri/ileri alabilmeli
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self.canvas)
        self.shortcut_undo.activated.connect(self.trigger_undo)
        
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self.canvas)
        self.shortcut_redo.activated.connect(self.trigger_redo)

    def on_mode_changed(self, mode: ToolMode):
        """Araç kutusunda mod değiştiğinde çizim katmanını koordine eder"""
        if mode == ToolMode.MOUSE:
            # İşaretçi modunda dondurulan ekran çözülür ve katman gizlenir
            self.canvas.unfreeze_screen()
            self.canvas.hide()
        else:
            # Herhangi bir çizim moduna geçildiğinde:
            if self.canvas.isHidden():
                # Eğer katman gizliyse, yeni bir ekran dondurma işlemi yap ve katmanı aç
                self.canvas.freeze_screen(self.toolbar)
                self.canvas.show()
            
            # Pencereleri öne çıkar (Araç çubuğu çizim katmanının üstünde durmalıdır)
            self.canvas.raise_()
            self.toolbar.raise_()

    def trigger_undo(self):
        """Çizim motorundan son işlemi geri alır"""
        self.engine.undo(self.canvas.scene)

    def trigger_redo(self):
        """Geri alınan işlemi ileri alır"""
        self.engine.redo(self.canvas.scene)

def main():
    # Wayland altında şeffaflık ve pencere konumlandırma sorunlarını gidermek için Qt öznitelik ayarı
    os.environ["QT_QPA_PLATFORM"] = "xcb" # XWayland/X11 platform entegrasyonu stays-on-top için en kararlı yoldur.
    
    app = QApplication(sys.argv)
    
    # Uygulama genelinde yazı tipi pürüzsüzleştirme ve stil desteği
    app.setStyle("Fusion")
    
    # Uygulama Koordinatörünü Başlat
    pardus_kalem = PardusKalemApp()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
