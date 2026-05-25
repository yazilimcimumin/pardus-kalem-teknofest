from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QLabel, QSlider, QApplication, QColorDialog
)
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QMouseEvent
from core.engine import ToolMode, DrawingEngine

class VectorIconType:
    MOUSE = "mouse"
    PEN = "pen"
    HIGHLIGHTER = "highlighter"
    SHAPE = "shape"
    ERASER = "eraser"
    SIZE = "size"
    PALETTE = "palette"
    UNDO = "undo"
    REDO = "redo"
    CLEAR = "clear"
    CLOSE = "close"
    
    # Şekiller (Shapes)
    LINE = "line"
    ARROW = "arrow"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"

class VectorIconButton(QPushButton):
    """Sıfır bağımlılıklı, yüksek çözünürlüklü vektör çizimli modern buton"""
    def __init__(self, icon_type: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.setToolTip(tooltip)
        self.setFixedSize(38, 38) # Standardized compact button size
        self.is_hovered = False
        self.active_state = False

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
              # Çizim modundayken ve canvas açıkken ekranın etrafını mavi bir çerçeveyle kapla (etkin mod bildirimi)
            border_color = QColor(0, 255, 204, 180)
        elif self.is_hovered:
            bg_color = QColor(255, 255, 255, 25) # Hafif beyaz parıltı
            border_color = QColor(255, 255, 255, 60)

        # Buton gövdesi
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

        # İkon Renkleri
        icon_color = QColor(255, 255, 255) # Varsayılan beyaz
        if self.active_state or self.is_hovered:
            icon_color = QColor(0, 255, 204) # Turkuaz

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
            path = QPainterPath()
            path.moveTo(cx - 5, cy - 7)
            path.lineTo(cx + 5, cy + 1)
            path.lineTo(cx + 1, cy + 2)
            path.lineTo(cx + 3, cy + 7)
            path.lineTo(cx + 1, cy + 8)
            path.lineTo(cx - 1, cy + 3)
            path.lineTo(cx - 5, cy + 6)
            path.closeSubpath()
            painter.setBrush(QBrush(icon_color if self.active_state else QColor(255, 255, 255, 40)))
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.PEN:
            path = QPainterPath()
            path.moveTo(cx - 7, cy + 7)
            path.lineTo(cx - 7, cy + 3)
            path.lineTo(cx + 3, cy - 7)
            path.lineTo(cx + 7, cy - 3)
            path.lineTo(cx - 3, cy + 7)
            path.closeSubpath()
            path.moveTo(cx - 7, cy + 3)
            path.lineTo(cx - 3, cy + 7)
            painter.drawPath(path)
            
            tip = QPainterPath()
            tip.moveTo(cx - 7, cy + 5)
            tip.lineTo(cx - 7, cy + 7)
            tip.lineTo(cx - 5, cy + 7)
            tip.closeSubpath()
            painter.setBrush(QBrush(icon_color))
            painter.drawPath(tip)

        elif self.icon_type == VectorIconType.HIGHLIGHTER:
            path = QPainterPath()
            path.moveTo(cx - 4, cy + 7)
            path.lineTo(cx - 4, cy + 3)
            path.lineTo(cx + 3, cy - 4)
            path.lineTo(cx + 7, cy)
            path.lineTo(cx, cy + 7)
            path.closeSubpath()
            path.moveTo(cx + 3, cy - 4)
            path.lineTo(cx + 1, cy - 6)
            path.lineTo(cx + 3, cy - 8)
            path.lineTo(cx + 5, cy - 6)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.SHAPE:
            painter.drawRect(int(cx - 8), int(cy - 8), 10, 10)
            painter.drawEllipse(int(cx - 2), int(cy - 2), 10, 10)

        elif self.icon_type == VectorIconType.ERASER:
            path = QPainterPath()
            path.moveTo(cx - 8, cy + 3)
            path.lineTo(cx - 3, cy - 5)
            path.lineTo(cx + 7, cy - 5)
            path.lineTo(cx + 2, cy + 3)
            path.closeSubpath()
            path.moveTo(cx - 8, cy + 3)
            path.lineTo(cx + 8, cy + 3)
            painter.drawPath(path)

        elif self.icon_type == VectorIconType.SIZE:
            # Slider icon
            painter.drawLine(int(cx - 8), int(cy), int(cx + 8), int(cy))
            painter.drawEllipse(int(cx - 3), int(cy - 4), 6, 6)

        elif self.icon_type == VectorIconType.PALETTE:
            # Palette icon
            painter.drawEllipse(int(cx - 8), int(cy - 8), 16, 16)
            # thumb hole
            painter.drawEllipse(int(cx + 1), int(cy + 1), 3, 3)

        elif self.icon_type == VectorIconType.UNDO:
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - 8, cy - 8, 16, 16), 30)
            path.arcTo(QRectF(cx - 8, cy - 8, 16, 16), 30, 260)
            painter.drawPath(path)
            
            arrow = QPainterPath()
            arrow.moveTo(cx - 8, cy - 3)
            arrow.lineTo(cx - 11, cy + 1)
            arrow.lineTo(cx - 8, cy + 5)
            painter.drawPath(arrow)

        elif self.icon_type == VectorIconType.REDO:
            path = QPainterPath()
            path.arcMoveTo(QRectF(cx - 8, cy - 8, 16, 16), 150)
            path.arcTo(QRectF(cx - 8, cy - 8, 16, 16), 150, -260)
            painter.drawPath(path)
            
            arrow = QPainterPath()
            arrow.moveTo(cx + 8, cy - 3)
            arrow.lineTo(cx + 11, cy + 1)
            arrow.lineTo(cx + 8, cy + 5)
            painter.drawPath(arrow)

        elif self.icon_type == VectorIconType.CLEAR:
            painter.drawRect(int(cx - 6), int(cy - 3), 12, 10)
            painter.drawLine(int(cx - 8), int(cy - 5), int(cx + 8), int(cy - 5))
            painter.drawRect(int(cx - 2), int(cy - 7), 4, 2)

        elif self.icon_type == VectorIconType.CLOSE:
            painter.drawLine(int(cx - 6), int(cy - 6), int(cx + 6), int(cy + 6))
            painter.drawLine(int(cx + 6), int(cy - 6), int(cx - 6), int(cy + 6))
            
        # Shape icons inside sub-panel
        elif self.icon_type == VectorIconType.LINE:
            painter.drawLine(int(cx - 8), int(cy + 8), int(cx + 8), int(cy - 8))
            
        elif self.icon_type == VectorIconType.ARROW:
            painter.drawLine(int(cx - 8), int(cy + 8), int(cx + 5), int(cy - 5))
            arrow = QPainterPath()
            arrow.moveTo(cx + 5, cy - 5)
            arrow.lineTo(cx + 1, cy - 5)
            arrow.lineTo(cx + 5, cy - 1)
            arrow.closeSubpath()
            painter.setBrush(QBrush(icon_color))
            painter.drawPath(arrow)
            
          # Çizim modundayken ve canvas açıkken ekranın etrafını mavi bir çerçeveyle kapla (etkin mod bildirimi)
        elif self.icon_type == VectorIconType.RECTANGLE:
            painter.drawRect(int(cx - 7), int(cy - 7), 14, 14)
            
        elif self.icon_type == VectorIconType.CIRCLE:
            painter.drawEllipse(int(cx - 7), int(cy - 7), 14, 14)


class SubPanel(QWidget):
    """Süper şık, butonların hemen üstünde beliren Fatih Kalem stili küçük yüzer çekmece"""
    def __init__(self, parent=None):
        super().__init__(None) # Parent'ı None yapıyoruz ki bağımsız float edebilsin
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # İç çerçeve tasarımı (Glassmorphic)
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 28, 0.95);
                border: 1px solid rgba(0, 255, 204, 0.4);
                border-radius: 12px;
            }
        """)
        
        # Layout container
        self.base_layout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.addWidget(self.frame)
        
        # Gölge Efekti
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
    def show_near(self, button: QWidget):
        """Panelin konumunu butonun tam üstünde ortalayarak gösterir"""
        self.adjustSize()
        btn_pos = button.mapToGlobal(QPoint(0, 0))
        
        # Paneli butonun tam ortasına hizala ve 10px yukarısında konumlandır
        x = btn_pos.x() + (button.width() - self.width()) // 2
        y = btn_pos.y() - self.height() - 10
        
        # Ekran sınırlarını aşmasını önle
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.geometry()
            if x < 10:
                x = 10
            elif x + self.width() > screen_rect.width() - 10:
                x = screen_rect.width() - self.width() - 10
                
            if y < 10:
                y = btn_pos.y() + button.height() + 10 # Ekranın üstünden taşarsa butonun altına koy
                
        self.move(x, y)
        self.show()
        self.raise_()


class ShapePanel(SubPanel):
    """Geometrik şekiller seçim paneli"""
    shape_selected = pyqtSignal(ToolMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        self.btn_line = VectorIconButton(VectorIconType.LINE, "Düz Çizgi", self)
        self.btn_arrow = VectorIconButton(VectorIconType.ARROW, "Yön Oku", self)
        self.btn_rect = VectorIconButton(VectorIconType.RECTANGLE, "Dikdörtgen", self)
        self.btn_circle = VectorIconButton(VectorIconType.CIRCLE, "Daire", self)
        
        self.btn_line.clicked.connect(lambda: self.select_shape(ToolMode.LINE))
        self.btn_arrow.clicked.connect(lambda: self.select_shape(ToolMode.ARROW))
        self.btn_rect.clicked.connect(lambda: self.select_shape(ToolMode.RECTANGLE))
        self.btn_circle.clicked.connect(lambda: self.select_shape(ToolMode.CIRCLE))
        
        layout.addWidget(self.btn_line)
        layout.addWidget(self.btn_arrow)
        layout.addWidget(self.btn_rect)
        layout.addWidget(self.btn_circle)
        
    def select_shape(self, mode: ToolMode):
        self.shape_selected.emit(mode)
        self.hide()


class SizePreview(QWidget):
    """Kalem kalınlığını canlı olarak gösteren önizleme dairesi"""
    def __init__(self, size=5, color=QColor(0, 255, 204), parent=None):
        super().__init__(parent)
        self.size = size
        self.color = color
        self.setFixedSize(40, 40)
        
    def set_size(self, size):
        self.size = size
        self.update()
        
    def set_color(self, color):
        self.color = color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan hafif kesikli kılavuz dairesi
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)
        
        # Önizleme dairesi
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        
        # Dairenin yarıçapı kalem boyutuna göre (maksimum 36px)
        r = max(2, min(36, self.size))
        cx, cy = self.width() / 2, self.height() / 2
        painter.drawEllipse(QPointF(cx, cy), r / 2, r / 2)


class SizePanel(SubPanel):
    """Tüm çizim elemanları için global kalınlık ayar sürgüsü"""
    size_changed = pyqtSignal(int)
    
    def __init__(self, initial_size=5, initial_color=QColor(0, 255, 204), parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Canlı önizleme
        self.preview = SizePreview(initial_size, initial_color, self)
        
        # Sürgü (Slider)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(1, 50)
        self.slider.setValue(initial_size)
        self.slider.setFixedWidth(110)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 255, 255, 0.2);
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00FFCC;
                border: 1px solid #00FFCC;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #00FFCC;
                border-radius: 2px;
            }
        """)
        
        # Değer metni
        self.lbl_val = QLabel(f"{initial_size}px", self)
        self.lbl_val.setFont(QFont("Inter", 9, QFont.Weight.Bold))
        self.lbl_val.setStyleSheet("color: #FFFFFF; min-width: 32px;")
        
        layout.addWidget(self.preview)
        layout.addWidget(self.slider)
        layout.addWidget(self.lbl_val)
        
        self.slider.valueChanged.connect(self.on_value_changed)
        
    def on_value_changed(self, val):
        self.lbl_val.setText(f"{val}px")
        self.preview.set_size(val)
        self.size_changed.emit(val)
        
    def set_color(self, color):
        self.preview.set_color(color)


class ColorDot(QPushButton):
    """Süper şık renk dairesi butonu, çift tıkla QColorDialog tetikler"""
    color_double_clicked = pyqtSignal(QColor)
    
    def __init__(self, color: QColor, tooltip: str, parent=None):
        super().__init__(parent)
        self.color = color
        self.setToolTip(tooltip)
        self.setFixedSize(22, 22)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Kenarlık ve Dolgu
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.color_double_clicked.emit(self.color)
            event.accept()


class ColorPanel(SubPanel):
    """Fatih Kalem stili hızlı renk ve tam palet paneli"""
    color_selected = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Hızlı renkler: Siyah (İlk Sırada), Kırmızı, Mavi, Yeşil
        self.dots = []
        quick_colors = [
            (QColor(0, 0, 0), "Siyah (Çift Tıkla Özelleştir)"),
            (QColor(255, 80, 80), "Kırmızı (Çift Tıkla Özelleştir)"),
            (QColor(80, 150, 255), "Mavi (Çift Tıkla Özelleştir)"),
            (QColor(80, 255, 150), "Yeşil (Çift Tıkla Özelleştir)")
        ]
        
        for col, tip in quick_colors:
            dot = ColorDot(col, tip, self)
            dot.clicked.connect(lambda checked, c=col: self.select_color(c))
            dot.color_double_clicked.connect(self.open_color_dialog)
            layout.addWidget(dot)
            self.dots.append(dot)
            
        # Özel Renk Butonu (Sihirli Gradyan Dairesi)
        self.btn_custom = QPushButton(self)
        self.btn_custom.setFixedSize(22, 22)
        self.btn_custom.setToolTip("Özel Renk Seç (QColorDialog)...")
        self.btn_custom.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 red, stop:0.5 green, stop:1 blue);
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 11px;
            }
            QPushButton:hover {
                border: 1px solid #00FFCC;
            }
        """)
        self.btn_custom.clicked.connect(lambda: self.open_color_dialog())
        layout.addWidget(self.btn_custom)
        
    def select_color(self, color: QColor):
        self.color_selected.emit(color)
        self.hide()
        
    def open_color_dialog(self, initial_color=None):
        init_col = initial_color if initial_color else QColor(0, 255, 204)
        color = QColorDialog.getColor(init_col, None, "Pardus Kalem - Renk Paleti")
        if color.isValid():
            self.select_color(color)


class FloatingToolbar(QWidget):
    """Masaüstünde her zaman en üstte duran, modern cam arayüze sahip
    sürüklenebilir, Fatih Kalem stili küçülebilir yatay araç kutusu.
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
        self.is_collapsed = True # Varsayılan olarak kapalı/fare modunda başlar

        # Pencere Özellikleri: Çerçevesiz, Her Zaman Üstte, Panel/Araç Penceresi
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Görsel Gölge Efekti
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Sub-Panelleri Tanımla
        self.shape_panel = ShapePanel(self)
        self.size_panel = SizePanel(self.engine.get_pen_width(), self.engine.get_color(), self)
        self.color_panel = ColorPanel(self)

        # Sub-Panel Sinyal Bağlantıları
        self.shape_panel.shape_selected.connect(self.select_shape_mode)
        self.size_panel.size_changed.connect(self.select_thickness)
        self.color_panel.color_selected.connect(self.select_color)

        # Arayüz Kurulumu
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Cam Panel Gövdesi
        self.panel = QFrame(self)
        self.panel.setObjectName("glassPanel")
        self.main_layout.addWidget(self.panel)

        # Yatay Düzen (Fatih Kalem Şeridi)
        self.panel_layout = QHBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(6, 6, 6, 6)
        self.panel_layout.setSpacing(4)

        # Tüm Bileşenleri Oluştur
        self.create_components()

        # Varsayılan Küçülme Durumunu Uygula
        self.set_collapsed_state(True)

    def create_components(self):
        # 1. Grab Handle (Sürükleme Çubuğu - Yatay Düzen Solu)
        self.grab_handle = QFrame(self.panel)
        self.grab_handle.setFixedWidth(16)
        self.grab_handle.setFixedHeight(38)
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        self.grab_handle.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
        """)
        handle_layout = QVBoxLayout(self.grab_handle)
        handle_layout.setContentsMargins(0, 0, 0, 0)
        handle_layout.setSpacing(2)
        dots = QLabel("⋮\n⋮", self.grab_handle)
        dots.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        dots.setStyleSheet("color: rgba(0, 255, 204, 0.8);")
        dots.setAlignment(Qt.AlignmentFlag.AlignCenter)
        handle_layout.addWidget(dots)

        # 2. Bubble Butonu (Yalnızca kapalı/küçültülmüş durumda çalışır)
        self.btn_bubble = VectorIconButton(VectorIconType.PEN, "Pardus Kalem: Çizim Modunu Aç", self.panel)
        self.btn_bubble.setFixedSize(40, 40)
        self.btn_bubble.clicked.connect(self.expand_toolbar)

        # 3. İşaretçi / Fare Seçim Modu
        self.btn_pointer = VectorIconButton(VectorIconType.MOUSE, "İşaretçi Modu (Masaüstü Etkileşimi)", self.panel)
        self.btn_pointer.clicked.connect(self.collapse_toolbar)

        # 4. Kalem Butonu
        self.btn_pen = VectorIconButton(VectorIconType.PEN, "Çizim Kalemi", self.panel)
        self.btn_pen.clicked.connect(lambda: self.select_mode(ToolMode.PEN))

        # 5. Fosforlu Kalem Butonu
        self.btn_highlighter = VectorIconButton(VectorIconType.HIGHLIGHTER, "Fosforlu Kalem", self.panel)
        self.btn_highlighter.clicked.connect(lambda: self.select_mode(ToolMode.HIGHLIGHTER))

        # 6. Silgi Butonu
        self.btn_eraser = VectorIconButton(VectorIconType.ERASER, "Vektörel Silgi", self.panel)
        self.btn_eraser.clicked.connect(lambda: self.select_mode(ToolMode.ERASER))

        # 7. Şekiller Butonu
        self.btn_shape = VectorIconButton(VectorIconType.SHAPE, "Geometrik Şekiller", self.panel)
        self.btn_shape.clicked.connect(self.show_shape_panel)

        # 8. Renk Butonu
        self.btn_color = VectorIconButton(VectorIconType.PALETTE, "Renk Seçimi (Çift Tıkla Palet)", self.panel)
        self.btn_color.clicked.connect(self.show_color_panel)

        # 9. Kalınlık Butonu
        self.btn_size = VectorIconButton(VectorIconType.SIZE, "Çizim Kalınlığı Ayarı", self.panel)
        self.btn_size.clicked.connect(self.show_size_panel)

        # Bölücü Çizgi
        self.separator = QFrame(self.panel)
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.12); max-width: 1px; min-height: 25px;")

        # 10. Geri Al
        self.btn_undo = VectorIconButton(VectorIconType.UNDO, "Geri Al (Ctrl+Z)", self.panel)
        self.btn_undo.clicked.connect(self.undo_requested.emit)

        # 11. İleri Al
        self.btn_redo = VectorIconButton(VectorIconType.REDO, "İleri Al (Ctrl+Y)", self.panel)
        self.btn_redo.clicked.connect(self.redo_requested.emit)

        # 12. Temizle
        self.btn_clear = VectorIconButton(VectorIconType.CLEAR, "Ekranı Temizle", self.panel)
        self.btn_clear.clicked.connect(self.clear_requested.emit)

        # 13. Kapat
        self.btn_close = VectorIconButton(VectorIconType.CLOSE, "Uygulamadan Çık", self.panel)
        self.btn_close.clicked.connect(self.close_requested.emit)

        # Panel Layout'a ekle (Sıralı yatay düzen)
        self.panel_layout.addWidget(self.btn_bubble)
        self.panel_layout.addWidget(self.grab_handle)
        self.panel_layout.addWidget(self.btn_pointer)
        self.panel_layout.addWidget(self.btn_pen)
        self.panel_layout.addWidget(self.btn_highlighter)
        self.panel_layout.addWidget(self.btn_eraser)
        self.panel_layout.addWidget(self.btn_shape)
        self.panel_layout.addWidget(self.btn_color)
        self.panel_layout.addWidget(self.btn_size)
        self.panel_layout.addWidget(self.separator)
        self.panel_layout.addWidget(self.btn_undo)
        self.panel_layout.addWidget(self.btn_redo)
        self.panel_layout.addWidget(self.btn_clear)
        self.panel_layout.addWidget(self.btn_close)

    def set_collapsed_state(self, collapsed: bool):
        self.is_collapsed = collapsed

        # Tüm sub-panelleri kapat
        self.shape_panel.hide()
        self.size_panel.hide()
        self.color_panel.hide()

        expanded_widgets = [
            self.grab_handle, self.btn_pointer, self.btn_pen, self.btn_highlighter,
            self.btn_eraser, self.btn_shape, self.btn_color, self.btn_size,
            self.separator, self.btn_undo, self.btn_redo, self.btn_clear, self.btn_close
        ]

        if collapsed:
            # Sadece bubble butonu görünsün
            for w in expanded_widgets:
                w.hide()
            self.btn_bubble.show()
            self.panel.setStyleSheet("""
                QFrame#glassPanel {
                    background-color: rgba(26, 26, 36, 0.95);
                    border: 2px solid #00FFCC;
                    border-radius: 20px;
                }
            """)
            self.panel_layout.setContentsMargins(4, 4, 4, 4)
            self.setFixedSize(48, 48)
        else:
            # Tüm araç kutusu şeridi görünsün
            self.btn_bubble.hide()
            for w in expanded_widgets:
                w.show()
            self.panel.setStyleSheet("""
                QFrame#glassPanel {
                    background-color: rgba(26, 26, 36, 0.85);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 12px;
                }
            """)
            self.panel_layout.setContentsMargins(6, 6, 6, 6)
            
            # Boyut kısıtlarını kaldır, otomatik hesaplansın
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.adjustSize()
            self.setFixedSize(self.sizeHint())

    def expand_toolbar(self):
        """Çizim moduna geçer ve araç çubuğunu genişletir"""
        self.set_collapsed_state(False)
        # Varsayılan araç: Kalem
        self.select_mode(ToolMode.PEN)

    def collapse_toolbar(self):
        """Fare moduna geçer ve araç çubuğunu kapatır"""
        self.set_collapsed_state(True)
        self.mode_changed.emit(ToolMode.MOUSE)

    def select_mode(self, mode: ToolMode):
        if mode == ToolMode.MOUSE:
            self.collapse_toolbar()
            return

        self.engine.set_active_tool(mode)

        # Buton durumlarını güncelle (aktif rengi vermek için)
        self.btn_pen.set_checked(mode == ToolMode.PEN)
        self.btn_highlighter.set_checked(mode == ToolMode.HIGHLIGHTER)
        self.btn_eraser.set_checked(mode == ToolMode.ERASER)

        # Şekillerden biri seçildiyse Shape butonunu aktif yap
        is_shape = mode in [ToolMode.LINE, ToolMode.ARROW, ToolMode.RECTANGLE, ToolMode.CIRCLE]
        self.btn_shape.set_checked(is_shape)

        self.mode_changed.emit(mode)

    def select_shape_mode(self, mode: ToolMode):
        self.select_mode(mode)

    def select_thickness(self, width: int):
        self.engine.set_pen_width(width)
        # Vurgulayıcı kalınlığı kalemin 4 katı
        self.engine.set_highlighter_width(width * 4)

    def select_color(self, color: QColor):
        self.engine.set_color(color)
        self.size_panel.set_color(color)

    # Sub-Panel Açma Kontrolleri
    def show_shape_panel(self):
        if self.shape_panel.isVisible():
            self.shape_panel.hide()
        else:
            self.size_panel.hide()
            self.color_panel.hide()
            self.shape_panel.show_near(self.btn_shape)

    def show_size_panel(self):
        if self.size_panel.isVisible():
            self.size_panel.hide()
        else:
            self.shape_panel.hide()
            self.color_panel.hide()
            self.size_panel.show_near(self.btn_size)

    def show_color_panel(self):
        if self.color_panel.isVisible():
            self.color_panel.hide()
        else:
            self.shape_panel.hide()
            self.size_panel.hide()
            self.color_panel.show_near(self.btn_color)

    # MOUSE SÜRÜKLEME (Dragging) DESTEĞİ
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.grab_handle.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
