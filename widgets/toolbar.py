from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QFrame, QLabel, QToolTip
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QMouseEvent
from core.engine import ToolMode, DrawingEngine

class VectorIconType:
    MOUSE = "mouse"
    PEN = "pen"
    HIGHLIGHTER = "highlighter"
    SHAPE = "shape"
    ERASER = "eraser"
    UNDO = "undo"
    REDO = "redo"
    CLEAR = "clear"
    CLOSE = "close"
    MINIMIZE = "minimize"
    EXPAND = "expand"

class VectorIconButton(QPushButton):
    """Sıfır bağımlılıklı, yüksek çözünürlüklü vektör çizimli modern buton"""
    def __init__(self, icon_type: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.setToolTip(tooltip)
        self.setFixedSize(46, 46)
        self.is_hovered = False
        self.is_checked_btn = False
        self.active_state = False

        # Tooltip tasarımını özelleştir
        self.setStyleSheet("""
            QToolTip {
                background-color: #1E1E28;
                color: #FFFFFF;
                border: 1px solid rgba(0, 255, 204, 0.4);
                border-radius: 6px;
                padding: 5px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
            }
        """)

    def set_checked(self, checked: bool):
        self.active_state = checked
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Hover veya Aktif durum arka plan rengi
        bg_color = QColor(255, 255, 255, 0)
        border_color = QColor(255, 255, 255, 0)

        if self.active_state:
            bg_color = QColor(0, 255, 204, 45) # Neon turkuaz yarı saydam
            border_color = QColor(0, 255, 204, 180)
        elif self.is_hovered:
            bg_color = QColor(255, 255, 255, 25) # Hafif beyaz parıltı
            border_color = QColor(255, 255, 255, 60)

        # Buton gövdesi
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(2, 2, self.width() - 4, self.height() - 4, 10, 10)

        # İkon Renkleri
        icon_color = QColor(255, 255, 255) # Varsayılan beyaz
        if self.active_state:
            icon_color = QColor(0, 255, 204) # Aktif ise turkuaz
        elif self.is_hovered:
            icon_color = QColor(0, 255, 204) # Hover ise turkuaz

        if self.icon_type == VectorIconType.CLOSE:
            icon_color = QColor(255, 80, 80) # Kapat butonu kırmızı

        # Çizim Ayarları
        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # VEKTÖREL İKON ÇİZİMLERİ (QPainterPath)
        if self.icon_type == VectorIconType.MOUSE:
            # Fare işareti oku
            path = QPainterPath()
            path.moveTo(cx - 6, cy - 8)
            path.lineTo(cx + 6, cy + 2)
            path.lineTo(cx + 1, cy + 3)
            path.lineTo(cx + 4, cy + 8)
            path.lineTo(cx + 2, cy + 9)
            path.lineTo(cx - 1, cy + 4)
            path.lineTo(cx - 6, cy + 8)
            path.closeSubpath()
            painter.setBrush(QBrush(icon_color if self.active_state else QColor(255,255,255,40)))
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.PEN:
            # Çapraz duran Kalem ikon
            path = QPainterPath()
            path.moveTo(cx - 8, cy + 8)
            path.lineTo(cx - 8, cy + 3)
            path.lineTo(cx + 3, cy - 8)
            path.lineTo(cx + 8, cy - 3)
            path.lineTo(cx - 3, cy + 8)
            path.closeSubpath()
            # Uç kısmı
            path.moveTo(cx - 8, cy + 3)
            path.lineTo(cx - 3, cy + 8)
            painter.drawPath(path)
            # Kalem Ucu
            tip = QPainterPath()
            tip.moveTo(cx - 8, cy + 5)
            tip.lineTo(cx - 8, cy + 8)
            tip.lineTo(cx - 5, cy + 8)
            tip.closeSubpath()
            painter.setBrush(QBrush(icon_color))
            painter.drawPath(tip)

        elif self.icon_type == VectorIconType.HIGHLIGHTER:
            # Vurgulayıcı Kalem
            path = QPainterPath()
            path.moveTo(cx - 5, cy + 9)
            path.lineTo(cx - 5, cy + 4)
            path.lineTo(cx + 4, cy - 5)
            path.lineTo(cx + 9, cy)
            path.lineTo(cx, cy + 9)
            path.closeSubpath()
            
            # Vurgulayıcı Uç
            path.moveTo(cx + 4, cy - 5)
            path.lineTo(cx + 1, cy - 8)
            path.lineTo(cx + 4, cy - 11)
            path.lineTo(cx + 7, cy - 8)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.SHAPE:
            # İç içe geometrik şekiller (Kare, Üçgen, Daire)
            painter.drawRect(int(cx - 9), int(cy - 9), 12, 12)
            painter.drawEllipse(int(cx - 2), int(cy - 2), 11, 11)

        elif self.icon_type == VectorIconType.ERASER:
            # Silgi blok ikon
            path = QPainterPath()
            path.moveTo(cx - 9, cy + 4)
            path.lineTo(cx - 3, cy - 6)
            path.lineTo(cx + 9, cy - 6)
            path.lineTo(cx + 3, cy + 4)
            path.closeSubpath()
            # Alt taban çizgisi
            path.moveTo(cx - 9, cy + 4)
            path.lineTo(cx + 9, cy + 4)
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.UNDO:
            # Geri Al (Dairesel Sol Ok)
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - 9, cy - 9, 18, 18), 30)
            path.arcTo(QRectF(cx - 9, cy - 9, 18, 18), 30, 260)
            painter.drawPath(path)
            
            # Ok ucu
            arrow = QPainterPath()
            arrow.moveTo(cx - 9, cy - 3)
            arrow.lineTo(cx - 13, cy + 1)
            arrow.lineTo(cx - 9, cy + 5)
            painter.drawPath(arrow)

        elif self.icon_type == VectorIconType.REDO:
            # İleri Al (Dairesel Sağ Ok)
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - 9, cy - 9, 18, 18), 150)
            path.arcTo(QRectF(cx - 9, cy - 9, 18, 18), 150, -260)
            painter.drawPath(path)
            
            # Ok ucu
            arrow = QPainterPath()
            arrow.moveTo(cx + 9, cy - 3)
            arrow.lineTo(cx + 13, cy + 1)
            arrow.lineTo(cx + 9, cy + 5)
            painter.drawPath(arrow)

        elif self.icon_type == VectorIconType.CLEAR:
            # Çöp Kutusu / Süpürge
            painter.drawRect(int(cx - 7), int(cy - 4), 14, 12)
            painter.drawLine(int(cx - 9), int(cy - 7), int(cx + 9), int(cy - 7))
            painter.drawRect(int(cx - 3), int(cy - 9), 6, 2)
            # İç dikey çizgiler
            painter.drawLine(int(cx - 3), int(cy - 2), int(cx - 3), int(cy + 6))
            painter.drawLine(int(cx + 3), int(cy - 2), int(cx + 3), int(cy + 6))

        elif self.icon_type == VectorIconType.CLOSE:
            # Çarpı (X) işareti
            painter.drawLine(int(cx - 7), int(cy - 7), int(cx + 7), int(cy + 7))
            painter.drawLine(int(cx + 7), int(cy - 7), int(cx - 7), int(cy + 7))

        elif self.icon_type == VectorIconType.MINIMIZE:
            # Yukarı katlama oku (Chevron Up)
            path = QPainterPath()
            path.moveTo(cx - 7, cy + 3)
            path.lineTo(cx, cy - 4)
            path.lineTo(cx + 7, cy + 3)
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.EXPAND:
            # Aşağı açma oku (Chevron Down)
            path = QPainterPath()
            path.moveTo(cx - 7, cy - 4)
            path.lineTo(cx, cy + 3)
            path.lineTo(cx + 7, cy - 4)
            painter.drawPath(path)

class FloatingToolbar(QWidget):
    """Masaüstünde her zaman en üstte duran, modern cam arayüze sahip
    sürüklenebilir ve küçültülebilir yüzer araç kutusu.
    """
    mode_changed = pyqtSignal(ToolMode)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, engine: DrawingEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._drag_pos = QPoint()
        self.is_collapsed = False

        # Pencere Türü: Çerçevesiz, Her Zaman Üstte, Panel/Araç Penceresi
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Görsel Neon Gölge Efekti
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Ana Arayüz Tasarımı
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Cam Panel Gövdesi
        self.panel = QFrame(self)
        self.panel.setObjectName("glassPanel")
        self.panel.setStyleSheet("""
            QFrame#glassPanel {
                background-color: rgba(26, 26, 36, 0.85); /* Derin şeffaf lacivert/siyah */
                border: 1px solid rgba(255, 255, 255, 0.12); /* Glassmorphic parlak kenarlık */
                border-radius: 18px;
            }
        """)
        
        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(8, 12, 8, 12)
        self.panel_layout.setSpacing(6)

        # 1. Grab Handle (Sürükleme Alanı ve Logo)
        self.grab_handle = QFrame(self.panel)
        self.grab_handle.setFixedHeight(30)
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        
        grab_layout = QVBoxLayout(self.grab_handle)
        grab_layout.setContentsMargins(0, 0, 0, 0)
        grab_layout.setSpacing(2)
        
        # Pardus Kalem Yazısı
        title = QLabel("PARDUS", self.grab_handle)
        title.setFont(QFont("Inter", 7, QFont.Weight.Bold))
        title.setStyleSheet("color: rgba(0, 255, 204, 0.9); letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("KALEM", self.grab_handle)
        subtitle.setFont(QFont("Inter", 6, QFont.Weight.Bold))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 3 Yatay Sürükleme Noktası (Tasarım Detayı)
        dots = QLabel("•••", self.grab_handle)
        dots.setStyleSheet("color: rgba(255, 255, 255, 0.35); font-size: 8px;")
        dots.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        grab_layout.addWidget(title)
        grab_layout.addWidget(subtitle)
        grab_layout.addWidget(dots)

        self.panel_layout.addWidget(self.grab_handle)

        # 2. Araç Butonları Grubu
        self.buttons = {}
        
        # İşaretçi Modu
        self.btn_mouse = VectorIconButton(VectorIconType.MOUSE, "İşaretçi Modu (Masaüstü Etkileşim)")
        self.btn_mouse.clicked.connect(lambda: self.select_mode(ToolMode.MOUSE))
        self.panel_layout.addWidget(self.btn_mouse)
        self.buttons[ToolMode.MOUSE] = self.btn_mouse

        # Normal Kalem
        self.btn_pen = VectorIconButton(VectorIconType.PEN, "Akıllı Vektörel Kalem")
        self.btn_pen.clicked.connect(lambda: self.select_mode(ToolMode.PEN))
        self.panel_layout.addWidget(self.btn_pen)
        self.buttons[ToolMode.PEN] = self.btn_pen

        # Vurgulayıcı (Highlighter)
        self.btn_highlighter = VectorIconButton(VectorIconType.HIGHLIGHTER, "Fosforlu Kalem / Vurgulayıcı")
        self.btn_highlighter.clicked.connect(lambda: self.select_mode(ToolMode.HIGHLIGHTER))
        self.panel_layout.addWidget(self.btn_highlighter)
        self.buttons[ToolMode.HIGHLIGHTER] = self.btn_highlighter

        # Şekiller Menüsü
        self.btn_shape = VectorIconButton(VectorIconType.SHAPE, "Geometrik Şekiller (Tıkla ve Değiştir)")
        self.btn_shape.clicked.connect(self.toggle_shape_drawer)
        self.panel_layout.addWidget(self.btn_shape)

        # Şekil Seçenekleri Çekmecesi (Drawer Widget)
        self.shape_drawer = QFrame(self.panel)
        self.shape_drawer.setStyleSheet("background: rgba(0, 0, 0, 0.15); border-radius: 8px;")
        self.shape_drawer_layout = QVBoxLayout(self.shape_drawer)
        self.shape_drawer_layout.setContentsMargins(4, 4, 4, 4)
        self.shape_drawer_layout.setSpacing(4)
        
        self.btn_draw_line = QPushButton("╱  Düz Çizgi", self.shape_drawer)
        self.btn_draw_arrow = QPushButton("➔  Yön Oku", self.shape_drawer)
        self.btn_draw_rect = QPushButton("⬜ Dikdörtgen", self.shape_drawer)
        self.btn_draw_circle = QPushButton("⭕ Daire", self.shape_drawer)

        for btn, mode in [(self.btn_draw_line, ToolMode.LINE), 
                          (self.btn_draw_arrow, ToolMode.ARROW), 
                          (self.btn_draw_rect, ToolMode.RECTANGLE), 
                          (self.btn_draw_circle, ToolMode.CIRCLE)]:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    text-align: left;
                    font-family: 'Inter', sans-serif;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: rgba(0, 255, 204, 0.2);
                    color: #00FFCC;
                }
            """)
            btn.clicked.connect(lambda checked, m=mode: self.select_shape_mode(m))
            self.shape_drawer_layout.addWidget(btn)

        self.panel_layout.addWidget(self.shape_drawer)
        self.shape_drawer.hide() # Başlangıçta gizli

        # Silgi
        self.btn_eraser = VectorIconButton(VectorIconType.ERASER, "Vektörel Silgi (Çizgi Odaklı)")
        self.btn_eraser.clicked.connect(lambda: self.select_mode(ToolMode.ERASER))
        self.panel_layout.addWidget(self.btn_eraser)
        self.buttons[ToolMode.ERASER] = self.btn_eraser

        # İnce Bölücü Çizgi
        separator = QFrame(self.panel)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        self.panel_layout.addWidget(separator)

        # Geri Al / İleri Al / Temizle
        self.btn_undo = VectorIconButton(VectorIconType.UNDO, "Geri Al (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo_requested.emit)
        self.panel_layout.addWidget(self.btn_undo)

        self.btn_redo = VectorIconButton(VectorIconType.REDO, "İleri Al (Ctrl+Y)")
        self.btn_redo.clicked.connect(self.redo_requested.emit)
        self.panel_layout.addWidget(self.btn_redo)

        self.btn_clear = VectorIconButton(VectorIconType.CLEAR, "Ekranı Temizle")
        self.btn_clear.clicked.connect(self.clear_requested.emit)
        self.panel_layout.addWidget(self.btn_clear)

        # Renk Çekmecesi Butonu
        self.btn_color = QPushButton(self.panel)
        self.btn_color.setFixedSize(46, 20)
        self.btn_color.setToolTip("Renk & Kalınlık Paletini Göster")
        self.btn_color.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 red, stop:0.25 yellow, stop:0.5 green, stop:0.75 blue, stop:1 magenta);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QPushButton:hover {
                border: 1px solid #00FFCC;
            }
        """)
        self.btn_color.clicked.connect(self.toggle_color_drawer)
        self.panel_layout.addWidget(self.btn_color)

        # Renk & Kalınlık Paleti Çekmecesi (Color Drawer)
        self.color_drawer = QFrame(self.panel)
        self.color_drawer.setStyleSheet("background: rgba(0, 0, 0, 0.15); border-radius: 8px;")
        self.color_drawer_layout = QVBoxLayout(self.color_drawer)
        self.color_drawer_layout.setContentsMargins(6, 6, 6, 6)
        self.color_drawer_layout.setSpacing(6)

        # 4 Renk Dairesi
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(4)
        for c_name, q_color in [("red", QColor(255, 0, 0)), 
                                ("blue", QColor(0, 102, 255)), 
                                ("green", QColor(0, 204, 102)), 
                                ("black", QColor(255, 255, 255))]: # Koyu temada siyah yerine beyaz çizeceğiz!
            c_btn = QPushButton()
            c_btn.setFixedSize(16, 16)
            bg_color_str = "white" if c_name == "black" else c_name
            c_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color_str};
                    border: 1px solid rgba(255, 255, 255, 0.4);
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    border: 2px solid #00FFCC;
                }}
            """)
            c_btn.clicked.connect(lambda checked, col=q_color: self.select_color(col))
            colors_layout.addWidget(c_btn)
        
        self.color_drawer_layout.addLayout(colors_layout)

        # Kalınlık Ayarları (3 boy yuvarlak)
        thickness_layout = QHBoxLayout()
        thickness_layout.setSpacing(4)
        for t_size, t_width in [("İnce", 2), ("Orta", 5), ("Kalın", 10)]:
            t_btn = QPushButton(t_size[0]) # Sadece ilk harf (İ, O, K)
            t_btn.setFixedSize(16, 16)
            t_btn.setFont(QFont("Inter", 7, QFont.Weight.Bold))
            t_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #00FFCC;
                    color: #1A1A24;
                }
            """)
            t_btn.clicked.connect(lambda checked, w=t_width: self.select_thickness(w))
            thickness_layout.addWidget(t_btn)

        self.color_drawer_layout.addLayout(thickness_layout)
        self.panel_layout.addWidget(self.color_drawer)
        self.color_drawer.hide() # Başlangıçta gizli

        # İnce Bölücü Çizgi
        separator2 = QFrame(self.panel)
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        self.panel_layout.addWidget(separator2)

        # Küçültme (Minimize) Butonu
        self.btn_min = VectorIconButton(VectorIconType.MINIMIZE, "Araç Kutusunu Küçült")
        self.btn_min.clicked.connect(self.toggle_collapse)
        self.panel_layout.addWidget(self.btn_min)

        # Kapat (Close) Butonu
        self.btn_close = VectorIconButton(VectorIconType.CLOSE, "Uygulamadan Çık")
        self.btn_close.clicked.connect(self.close_requested.emit)
        self.panel_layout.addWidget(self.btn_close)

        self.main_layout.addWidget(self.panel)

        # Başlangıç Durum Seçimi
        self.select_mode(ToolMode.PEN)

    # Katlanma / Küçülme (Collapse) Özelliği
    def toggle_collapse(self):
        """Araç kutusunu küçük bir daireye katlar veya geri açar"""
        if not self.is_collapsed:
            # Küçült
            self.panel.hide()
            
            # Küçük daire widget oluştur
            self.bubble = QFrame(self)
            self.bubble.setObjectName("bubblePanel")
            self.bubble.setFixedSize(50, 50)
            self.bubble.setStyleSheet("""
                QFrame#bubblePanel {
                    background-color: rgba(26, 26, 36, 0.9);
                    border: 1.5px solid #00FFCC;
                    border-radius: 25px;
                }
            """)
            
            bubble_layout = QVBoxLayout(self.bubble)
            bubble_layout.setContentsMargins(2, 2, 2, 2)
            
            # Küçültüldüğünde açma butonu (kalem ikonu)
            btn_expand = VectorIconButton(VectorIconType.PEN, "Araç Kutusunu Aç", self.bubble)
            btn_expand.setFixedSize(44, 44)
            btn_expand.setStyleSheet("background: transparent; border: none;")
            btn_expand.clicked.connect(self.toggle_collapse)
            bubble_layout.addWidget(btn_expand)
            
            self.main_layout.addWidget(self.bubble)
            self.is_collapsed = True
            
            # Pencere genişlik/yükseklik ayarla
            self.setFixedSize(70, 70)
        else:
            # Geri Aç
            self.bubble.hide()
            self.bubble.deleteLater()
            self.panel.show()
            self.is_collapsed = False
            self.setMinimumSize(0, 0)
            self.adjustSize()
            self.setFixedSize(self.sizeHint())

    # Çekmece Kontrolleri
    def toggle_shape_drawer(self):
        if self.shape_drawer.isHidden():
            self.color_drawer.hide()
            self.shape_drawer.show()
        else:
            self.shape_drawer.hide()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def toggle_color_drawer(self):
        if self.color_drawer.isHidden():
            self.shape_drawer.hide()
            self.color_drawer.show()
        else:
            self.color_drawer.hide()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    # Mod ve Ayar Seçimleri
    def select_mode(self, mode: ToolMode):
        self.engine.set_active_tool(mode)
        
        # Tüm butonların aktiflik durumunu temizle
        for m, btn in self.buttons.items():
            btn.set_checked(m == mode)
        
        # Eğer şekil butonlarından biri seçildiyse, ana Şekil butonunu aktif yap
        is_shape_mode = mode in [ToolMode.LINE, ToolMode.ARROW, ToolMode.RECTANGLE, ToolMode.CIRCLE]
        self.btn_shape.set_checked(is_shape_mode)
        if not is_shape_mode:
            self.shape_drawer.hide()

        self.mode_changed.emit(mode)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def select_shape_mode(self, mode: ToolMode):
        self.select_mode(mode)
        self.shape_drawer.hide()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def select_color(self, color: QColor):
        self.engine.set_color(color)
        self.color_drawer.hide()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def select_thickness(self, width: int):
        self.engine.set_pen_width(width)
        self.engine.set_highlighter_width(width * 4) # Vurgulayıcı kalem kalınlığı nispeten daha kalın olmalıdır
        self.color_drawer.hide()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    # MOUSE SÜRÜKLEME (Dragging) DESTEĞİ
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Mouse tıklandığında konum farkını kaydet
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.grab_handle.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            # Mouse hareket ettikçe pencereyi taşı
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
