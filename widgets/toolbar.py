from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QLabel, QSlider, QApplication, QColorDialog,
    QBoxLayout
)
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QRectF, QPointF, QVariantAnimation, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QMouseEvent
from core.engine import ToolMode, DrawingEngine
import math

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
    SCROLL = "scroll"
    
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
        self.icon_color_override = None

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

        bg_color = QColor(255, 255, 255, 0)
        border_color = QColor(255, 255, 255, 0)

        if self.active_state:
            bg_color = QColor(0, 255, 204, 45) # Neon turkuaz yarı saydam
            border_color = QColor(0, 255, 204, 180)
        elif self.is_hovered:
            bg_color = QColor(255, 255, 255, 25) # Hafif beyaz parıltı
            border_color = QColor(255, 255, 255, 60)

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

        icon_color = QColor(255, 255, 255)
        if self.active_state or self.is_hovered:
            icon_color = QColor(0, 255, 204)

        if self.icon_type == VectorIconType.CLOSE:
            icon_color = QColor(255, 80, 80)

        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

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
            painter.drawLine(int(cx - 8), int(cy), int(cx + 8), int(cy))
            painter.drawEllipse(int(cx - 3), int(cy - 4), 6, 6)

        elif self.icon_type == VectorIconType.PALETTE:
            painter.drawEllipse(int(cx - 8), int(cy - 8), 16, 16)
            c_color = self.icon_color_override if hasattr(self, 'icon_color_override') and self.icon_color_override else QColor(0, 255, 204)
            painter.setBrush(QBrush(c_color))
            painter.drawEllipse(int(cx - 4), int(cy - 4), 8, 8)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

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

        elif self.icon_type == VectorIconType.SCROLL:
            path = QPainterPath()
            path.moveTo(cx - 3, cy - 8)
            path.lineTo(cx + 3, cy - 8)
            path.arcTo(QRectF(cx - 3, cy - 11, 6, 6), 0, 180)
            path.lineTo(cx - 3, cy + 8)
            path.arcTo(QRectF(cx - 3, cy + 5, 6, 6), 180, 180)
            path.closeSubpath()
            painter.drawPath(path)
            
            painter.setBrush(QBrush(icon_color if self.active_state else QColor(255, 255, 255, 120)))
            painter.drawRoundedRect(QRectF(cx - 2, cy - 4, 4, 8), 2, 2)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            
            arrow_up = QPainterPath()
            arrow_up.moveTo(cx - 9, cy - 2)
            arrow_up.lineTo(cx - 6, cy - 5)
            arrow_up.lineTo(cx - 3, cy - 2)
            painter.drawPath(arrow_up)
            
            arrow_down = QPainterPath()
            arrow_down.moveTo(cx - 9, cy + 2)
            arrow_down.lineTo(cx - 6, cy + 5)
            arrow_down.lineTo(cx - 3, cy + 2)
            painter.drawPath(arrow_down)

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
            
        elif self.icon_type == VectorIconType.RECTANGLE:
            painter.drawRect(int(cx - 7), int(cy - 7), 14, 14)
            
        elif self.icon_type == VectorIconType.CIRCLE:
            painter.drawEllipse(int(cx - 7), int(cy - 7), 14, 14)


class SubPanel(QWidget):
    """Süper şık, butonların yanında beliren Fatih Kalem stili küçük yüzer çekmece"""
    def __init__(self, parent=None):
        super().__init__(None)
        # Canvas'ın (X11Bypass) üstünde kalması için aynı pencere bayrağını kullanıyoruz
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 28, 0.95);
                border: 1px solid rgba(0, 255, 204, 0.4);
                border-radius: 12px;
            }
        """)
        
        self.base_layout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.addWidget(self.frame)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
    def show_near(self, button: QWidget):
        """Panelin konumunu butonun yan tarafında (ekranın konumuna göre soluna veya sağına) hizalayarak gösterir"""
        self.adjustSize()
        btn_pos = button.mapToGlobal(QPoint(0, 0))
        
        screen = QApplication.primaryScreen()
        x = btn_pos.x() - self.width() - 10
        y = btn_pos.y() + (button.height() - self.height()) // 2
        
        if screen:
            screen_rect = screen.geometry()
            # Eğer buton ekranın sol yarısındaysa paneli sağında göster
            if btn_pos.x() < screen_rect.width() / 2:
                x = btn_pos.x() + button.width() + 10
            
            # Ekran dikey sınır kontrolü
            if y < 10:
                y = 10
            elif y + self.height() > screen_rect.height() - 10:
                y = screen_rect.height() - self.height() - 10
                
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
        
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.PenStyle.DashLine))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        
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
        
        self.preview = SizePreview(initial_size, initial_color, self)
        
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
        
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.color_double_clicked.emit(self.color)
            event.accept()


class ColorPanel(SubPanel):
    """Özel renk paleti — X11Bypass pencereler altında tıklanabilir renkler sunar"""
    color_selected = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QGridLayout
        
        grid = QGridLayout(self.frame)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setSpacing(4)
        
        # 16 hazır renk paleti (4x4 ızgara)
        palette = [
            # Satır 1: Temel renkler
            QColor(0, 0, 0),         # Siyah
            QColor(255, 255, 255),    # Beyaz
            QColor(220, 50, 50),      # Kırmızı
            QColor(50, 120, 255),     # Mavi
            # Satır 2: Doğa tonları
            QColor(40, 200, 80),      # Yeşil
            QColor(255, 200, 0),      # Sarı
            QColor(255, 130, 0),      # Turuncu
            QColor(160, 50, 220),     # Mor
            # Satır 3: Pastel tonlar
            QColor(255, 150, 180),    # Pembe
            QColor(0, 220, 200),      # Turkuaz
            QColor(100, 80, 60),      # Kahve
            QColor(128, 128, 128),    # Gri
            # Satır 4: Neon / canlı tonlar
            QColor(0, 255, 100),      # Neon yeşil
            QColor(255, 50, 150),     # Magenta
            QColor(0, 180, 255),      # Gök mavi
            QColor(255, 255, 100),    # Limon
        ]
        
        self.dots = []
        for i, color in enumerate(palette):
            dot = ColorDot(color, color.name(), self)
            dot.setFixedSize(26, 26)
            dot.clicked.connect(lambda checked, c=color: self.select_color(c))
            grid.addWidget(dot, i // 4, i % 4)
            self.dots.append(dot)
        
    def select_color(self, color: QColor):
        self.color_selected.emit(color)
        self.hide()


class EraserPanel(SubPanel):
    """Silgi alt paneli. Vektörel silgi modunu seçer ve
    Tümü Sil, Geri Al, İleri Al işlemlerini barındırır.
    """
    undo_clicked = pyqtSignal()
    redo_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        self.btn_undo = VectorIconButton(VectorIconType.UNDO, "Geri Al (Ctrl+Z)", self)
        self.btn_redo = VectorIconButton(VectorIconType.REDO, "İleri Al (Ctrl+Y)", self)
        self.btn_clear = VectorIconButton(VectorIconType.CLEAR, "Tümünü Sil", self)
        self.btn_close = VectorIconButton(VectorIconType.CLOSE, "Uygulamadan Çık", self)
        
        self.btn_undo.clicked.connect(self.undo_clicked.emit)
        self.btn_redo.clicked.connect(self.redo_clicked.emit)
        self.btn_clear.clicked.connect(self.clear_clicked.emit)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        
        layout.addWidget(self.btn_undo)
        layout.addWidget(self.btn_redo)
        layout.addWidget(self.btn_clear)
        layout.addWidget(self.btn_close)


class ScrollbarWidget(QWidget):
    valueChanged = pyqtSignal(float) # Emits value between -1.0 and 1.0
    released = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(32)
        self.value = 0.0 # -1.0 (top) to 1.0 (bottom)
        self.is_dragging = False
        self.is_hovered = False
        self.drag_start_y = 0
        self.drag_start_value = 0.0
        self.is_simulating = False
        self.last_warp_time = 0.0
        self.setMouseTracking(True)
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        
    def mousePressEvent(self, event):
        if self.is_simulating:
            event.ignore()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_y = event.position().y()
            self.drag_start_value = self.value
            
            h = self.height()
            thumb_h = 40
            travel = h - thumb_h
            if travel > 0:
                click_y = event.position().y()
                target_val = (click_y - h/2) / (travel / 2)
                self.value = max(-1.0, min(1.0, target_val))
                self.drag_start_value = self.value
                self.drag_start_y = click_y
                self.valueChanged.emit(self.value)
                self.update()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.is_simulating:
            event.ignore()
            return
        if self.is_dragging:
            h = self.height()
            thumb_h = 40
            travel = h - thumb_h
            if travel > 0:
                dy = event.position().y() - self.drag_start_y
                delta_val = dy / (travel / 2)
                self.value = max(-1.0, min(1.0, self.drag_start_value + delta_val))
                self.valueChanged.emit(self.value)
                self.update()
            event.accept()
        else:
            self.update()
            
    def mouseReleaseEvent(self, event):
        if self.is_simulating:
            event.ignore()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.released.emit()
            event.accept()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        cx = w / 2
        
        # 1. Draw track line (thin capsule)
        track_w = 6
        track_h = h - 20
        track_color = QColor(255, 255, 255, 30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(QRectF(cx - track_w/2, 10, track_w, track_h), track_w/2, track_w/2)
        
        # 2. Draw thumb
        thumb_w = 16
        thumb_h = 40
        travel = h - thumb_h
        thumb_center_y = h/2 + self.value * (travel / 2)
        thumb_rect = QRectF(cx - thumb_w/2, thumb_center_y - thumb_h/2, thumb_w, thumb_h)
        
        if self.is_dragging:
            thumb_color = QColor(0, 255, 204) # Glow turquoise
        elif self.is_hovered:
            thumb_color = QColor(0, 255, 204, 200)
        else:
            thumb_color = QColor(255, 255, 255, 180)
            
        painter.setBrush(QBrush(thumb_color))
        painter.drawRoundedRect(thumb_rect, thumb_w/2, thumb_w/2)
        
        painter.setPen(QPen(QColor(26, 26, 36), 2))
        painter.drawLine(int(cx - 4), int(thumb_center_y), int(cx + 4), int(thumb_center_y))


class HoverScrollButton(QPushButton):
    """Üzerine gelindiğinde (hover) veya tıklandığında kaydırma tetikleyen buton"""
    hovered = pyqtSignal(bool)
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self.hovered.emit(True)
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hovered.emit(False)


class ScrollbarPanel(SubPanel):
    """Büyük kaydırma çubuğu paneli. Sürüklemeye duyarlı kaydırma simülasyonu sunar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 28, 0.95);
                border: 1px solid rgba(0, 255, 204, 0.4);
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(6)
        
        # Büyük kaydırma çubuğu widget'ı
        self.scrollbar = ScrollbarWidget(self)
        self.scrollbar.setFixedHeight(200)
        layout.addWidget(self.scrollbar)
        
        # pynput mouse controller
        from pynput.mouse import Controller as MouseController
        self.mouse_controller = MouseController()
        
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(50) # 50ms tetikleme
        self.scroll_timer.timeout.connect(self.perform_scroll)
        
        self.scrollbar.valueChanged.connect(self.on_value_changed)
        self.scrollbar.released.connect(self.on_released)
        
    def on_value_changed(self, value):
        if value != 0.0:
            if not self.scroll_timer.isActive():
                self.scroll_timer.start()
        else:
            self.scroll_timer.stop()
            
    def on_released(self):
        # Kaydırma çubuğu bırakıldığında değeri yavaşça sıfırla ve durdur
        self.scrollbar.value = 0.0
        self.scrollbar.update()
        self.scroll_timer.stop()
        
    def perform_scroll(self):
        val = self.scrollbar.value
        # Stop timer if value is negligible
        if abs(val) < 0.05:
            self.scroll_timer.stop()
            return
        
        # Dynamic scroll step (1‑4 clicks depending on distance from centre)
        dy = max(1, int(abs(val) * 4))
        button = 4 if val < 0 else 5  # 4 = wheel up, 5 = wheel down
        
        self.scrollbar.is_simulating = True
        try:
            import subprocess
            # 1. Capture current cursor position (where the user is dragging)
            orig_pos = self.mouse_controller.position
            # 2. Move cursor away from the panel (e.g., 250px left, staying on screen)
            target_x = max(10, orig_pos[0] - 250)
            target_y = orig_pos[1]
            self.mouse_controller.position = (target_x, target_y)
            # 3. Send scroll event to the now‑focused window (the document behind)
            subprocess.run(
                ["xdotool", "click", "--delay", "5", str(button), str(dy)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # 4. Restore cursor back to the user's finger position
            self.mouse_controller.position = orig_pos
            # Keep UI responsive
            QApplication.processEvents()
        except Exception as e:
            print(f"Scroll tetikleme hatası: {e}")
        finally:
            self.scrollbar.is_simulating = False


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

        # Pencere Özellikleri: Çerçevesiz, Her Zaman Üstte, Pencere Yöneticisini Baypas Et (Tıklanabilirlik için)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
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
        self.eraser_panel = EraserPanel(self)
        self.scrollbar_panel = ScrollbarPanel(self)

        # Sub-Panel Sinyal Bağlantıları
        self.shape_panel.shape_selected.connect(self.select_shape_mode)
        self.size_panel.size_changed.connect(self.select_thickness)
        self.color_panel.color_selected.connect(self.select_color)
        
        self.eraser_panel.undo_clicked.connect(self.undo_requested.emit)
        self.eraser_panel.redo_clicked.connect(self.redo_requested.emit)
        self.eraser_panel.clear_clicked.connect(self.clear_requested.emit)
        self.eraser_panel.close_clicked.connect(self.close_requested.emit)

        # Arayüz Kurulumu
        self.init_ui()
        self.btn_color.icon_color_override = self.engine.get_color()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Cam Panel Gövdesi
        self.panel = QFrame(self)
        self.panel.setObjectName("glassPanel")
        self.main_layout.addWidget(self.panel)

        # Tamamen dikey yerleşim kullanıyoruz
        self.panel_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.panel)
        self.panel_layout.setContentsMargins(6, 6, 6, 6)
        self.panel_layout.setSpacing(4)

        # Tüm Bileşenleri Oluştur
        self.create_components()

        # Varsayılan Küçülme Durumunu Uygula
        self.set_collapsed_state(True)

    def create_components(self):
        # 1. Grab Handle (Sürükleme Çubuğu - Dikey Düzen Üstü)
        self.grab_handle = QFrame(self.panel)
        self.grab_handle.setFixedWidth(40)
        self.grab_handle.setFixedHeight(35)
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        self.grab_handle.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
            }
        """)
        handle_layout = QVBoxLayout(self.grab_handle)
        handle_layout.setContentsMargins(2, 2, 2, 2)
        handle_layout.setSpacing(1)
        
        lbl_pardus = QLabel("Pardus", self.grab_handle)
        lbl_pardus.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        lbl_pardus.setStyleSheet("color: #00FFCC; background: transparent;")
        lbl_pardus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_pardus.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        lbl_kalem = QLabel("Kalem", self.grab_handle)
        lbl_kalem.setFont(QFont("Outfit", 8, QFont.Weight.Bold))
        lbl_kalem.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent;")
        lbl_kalem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_kalem.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        handle_layout.addWidget(lbl_pardus)
        handle_layout.addWidget(lbl_kalem)

        # Collapsed durumdayken görünecek "Pardus Kalem" yazısı
        self.lbl_collapsed_brand = QWidget(self.panel)
        self.lbl_collapsed_brand.setStyleSheet("background: transparent;")
        brand_layout = QVBoxLayout(self.lbl_collapsed_brand)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(1)
        
        lbl_c_pardus = QLabel("Pardus", self.lbl_collapsed_brand)
        lbl_c_pardus.setFont(QFont("Outfit", 7, QFont.Weight.Bold))
        lbl_c_pardus.setStyleSheet("color: #00FFCC; background: transparent;")
        lbl_c_pardus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_pardus.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        lbl_c_kalem = QLabel("Kalem", self.lbl_collapsed_brand)
        lbl_c_kalem.setFont(QFont("Outfit", 7, QFont.Weight.Bold))
        lbl_c_kalem.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent;")
        lbl_c_kalem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_kalem.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        brand_layout.addWidget(lbl_c_pardus)
        brand_layout.addWidget(lbl_c_kalem)

        # 2. Bubble Butonu (Yalnızca kapalı/küçültülmüş durumda çalışır - Çizimi açar)
        self.btn_bubble = VectorIconButton(VectorIconType.PEN, "Çizim Modunu Aç", self.panel)
        self.btn_bubble.setFixedSize(40, 40)
        self.btn_bubble.clicked.connect(self.expand_toolbar)

        # 3. Kaydırma Çubuğu Yardımcısı Butonu (Yalnızca kapalı/küçültülmüş durumda çalışır)
        self.btn_scroll_toggle = VectorIconButton(VectorIconType.SCROLL, "Kaydırma Yardımcısı", self.panel)
        self.btn_scroll_toggle.setFixedSize(40, 40)
        self.btn_scroll_toggle.clicked.connect(self.toggle_scrollbar_panel)

        # 4. İşaretçi / Fare Seçim Modu (Yedek)
        self.btn_pointer = VectorIconButton(VectorIconType.MOUSE, "İşaretçi Modu", self.panel)
        self.btn_pointer.clicked.connect(self.collapse_toolbar)

        # 5. Kalem Butonu
        self.btn_pen = VectorIconButton(VectorIconType.PEN, "Çizim Kalemi", self.panel)
        self.btn_pen.clicked.connect(self.on_pen_clicked)

        # 6. Fosforlu Kalem Butonu (Yedek)
        self.btn_highlighter = VectorIconButton(VectorIconType.HIGHLIGHTER, "Fosforlu Kalem", self.panel)
        self.btn_highlighter.clicked.connect(lambda: self.select_mode(ToolMode.HIGHLIGHTER))

        # 7. Silgi Butonu
        self.btn_eraser = VectorIconButton(VectorIconType.ERASER, "Vektörel Silgi", self.panel)
        self.btn_eraser.clicked.connect(self.on_eraser_clicked)

        # 8. Şekiller Butonu
        self.btn_shape = VectorIconButton(VectorIconType.SHAPE, "Geometrik Şekiller", self.panel)
        self.btn_shape.clicked.connect(self.show_shape_panel)

        # 9. Renk Butonu (Yedek)
        self.btn_color = VectorIconButton(VectorIconType.PALETTE, "Renk Seçimi", self.panel)
        self.btn_color.clicked.connect(self.show_color_panel)

        # 10. Kalınlık Butonu
        self.btn_size = VectorIconButton(VectorIconType.SIZE, "Çizim Kalınlığı Ayarı", self.panel)
        self.btn_size.clicked.connect(self.show_size_panel)

        # Bölücü Çizgi (Yedek)
        self.separator = QFrame(self.panel)
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.12); max-width: 1px; min-height: 25px;")

        # 11. Geri Al (Yedek)
        self.btn_undo = VectorIconButton(VectorIconType.UNDO, "Geri Al", self.panel)
        self.btn_undo.clicked.connect(self.undo_requested.emit)

        # 12. İleri Al (Yedek)
        self.btn_redo = VectorIconButton(VectorIconType.REDO, "İleri Al", self.panel)
        self.btn_redo.clicked.connect(self.redo_requested.emit)

        # 13. Temizle (Yedek)
        self.btn_clear = VectorIconButton(VectorIconType.CLEAR, "Ekranı Temizle", self.panel)
        self.btn_clear.clicked.connect(self.clear_requested.emit)

        # 14. Kapat (Yedek)
        self.btn_close = VectorIconButton(VectorIconType.CLOSE, "Kapat", self.panel)
        self.btn_close.clicked.connect(self.close_requested.emit)

        # Panel Layout'a ekle (Sıralı ekleme, visibility kontrolü ile gösterilecekler belirlenecek)
        self.panel_layout.addWidget(self.lbl_collapsed_brand)
        self.panel_layout.addWidget(self.btn_bubble)
        self.panel_layout.addWidget(self.btn_scroll_toggle)
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
        self.eraser_panel.hide()
        self.scrollbar_panel.hide()
        self.btn_scroll_toggle.set_checked(False)

        # Görünürlük grupları
        collapsed_widgets = [self.btn_bubble, self.btn_scroll_toggle]
        expanded_widgets = [
            self.grab_handle, self.btn_pen, self.btn_eraser, self.btn_color, self.btn_size, self.btn_shape
        ]
        extra_widgets = [
            self.btn_pointer, self.btn_highlighter, self.separator,
            self.btn_undo, self.btn_redo, self.btn_clear, self.btn_close
        ]

        # Extra butonları tamamen gizli tut (Fatih Kalem stili sade arayüz için)
        for w in extra_widgets:
            w.hide()

        if collapsed:
            # Dikey yerleşim
            self.panel_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            
            for w in expanded_widgets:
                w.hide()
            for w in collapsed_widgets:
                w.show()
            self.lbl_collapsed_brand.show()
                
            self.panel.setStyleSheet("""
                QFrame#glassPanel {
                    background-color: rgba(26, 26, 36, 0.95);
                    border: 2px solid #00FFCC;
                    border-radius: 20px;
                }
            """)
            self.panel_layout.setContentsMargins(4, 8, 4, 8)
            self.panel_layout.setSpacing(4)
            self.setFixedSize(48, 126) # "Pardus Kalem" etiketi (30px) + İki adet 40x40 buton (80px) + boşluklar
        else:
            # Genişletilmiş durumda da dikey yerleşim
            self.panel_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            
            self.lbl_collapsed_brand.hide()
            for w in collapsed_widgets:
                w.hide()
            for w in expanded_widgets:
                w.show()
                
            self.panel.setStyleSheet("""
                QFrame#glassPanel {
                    background-color: rgba(26, 26, 36, 0.85);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 12px;
                }
            """)
            self.panel_layout.setContentsMargins(4, 4, 4, 4)
            self.panel_layout.setSpacing(4)
            
            # Boyut kısıtlarını kaldır ve otomatik sığdır
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.adjustSize()
            self.setFixedSize(self.sizeHint())

    def expand_toolbar(self):
        """Çizim moduna geçer ve araç çubuğunu genişletir"""
        self.set_collapsed_state(False)
        self.select_mode(ToolMode.PEN)

    def collapse_toolbar(self):
        """Fare moduna geçer ve araç çubuğunu kapatır"""
        self.set_collapsed_state(True)
        self.mode_changed.emit(ToolMode.MOUSE)

    def on_pen_clicked(self):
        # Kalem seçiliyken tekrar basılırsa çizim modunu kapatıp dikey menüye döner
        if self.engine.get_active_tool() == ToolMode.PEN:
            self.collapse_toolbar()
        else:
            self.select_mode(ToolMode.PEN)

    def on_eraser_clicked(self):
        self.select_mode(ToolMode.ERASER)
        self.show_eraser_panel()

    def select_mode(self, mode: ToolMode):
        if mode == ToolMode.MOUSE:
            self.collapse_toolbar()
            return

        self.engine.set_active_tool(mode)

        # Buton durumlarını güncelle
        self.btn_pen.set_checked(mode == ToolMode.PEN)
        self.btn_eraser.set_checked(mode == ToolMode.ERASER)

        # Şekillerden biri aktifse Şekil butonunu işaretle
        is_shape = mode in [ToolMode.LINE, ToolMode.ARROW, ToolMode.RECTANGLE, ToolMode.CIRCLE]
        self.btn_shape.set_checked(is_shape)

        self.mode_changed.emit(mode)

    def select_shape_mode(self, mode: ToolMode):
        self.select_mode(mode)

    def select_thickness(self, width: int):
        self.engine.set_pen_width(width)
        self.engine.set_highlighter_width(width * 4)

    def select_color(self, color: QColor):
        self.engine.set_color(color)
        self.size_panel.set_color(color)
        self.btn_color.icon_color_override = color
        self.btn_color.update()

    # Sub-Panel Kontrolleri
    def toggle_scrollbar_panel(self):
        if self.scrollbar_panel.isVisible():
            self.scrollbar_panel.hide()
            self.btn_scroll_toggle.set_checked(False)
        else:
            self.shape_panel.hide()
            self.size_panel.hide()
            self.color_panel.hide()
            self.eraser_panel.hide()
            self.scrollbar_panel.show_near(self.btn_scroll_toggle)
            self.btn_scroll_toggle.set_checked(True)

    def show_shape_panel(self):
        if self.shape_panel.isVisible():
            self.shape_panel.hide()
        else:
            self.size_panel.hide()
            self.color_panel.hide()
            self.eraser_panel.hide()
            self.scrollbar_panel.hide()
            self.shape_panel.show_near(self.btn_shape)

    def show_size_panel(self):
        if self.size_panel.isVisible():
            self.size_panel.hide()
        else:
            self.shape_panel.hide()
            self.color_panel.hide()
            self.eraser_panel.hide()
            self.scrollbar_panel.hide()
            self.size_panel.show_near(self.btn_size)

    def show_color_panel(self):
        if self.color_panel.isVisible():
            self.color_panel.hide()
        else:
            self.shape_panel.hide()
            self.size_panel.hide()
            self.eraser_panel.hide()
            self.scrollbar_panel.hide()
            self.color_panel.show_near(self.btn_color)

    def show_eraser_panel(self):
        if self.eraser_panel.isVisible():
            self.eraser_panel.hide()
        else:
            self.shape_panel.hide()
            self.size_panel.hide()
            self.color_panel.hide()
            self.scrollbar_panel.hide()
            self.eraser_panel.show_near(self.btn_eraser)

    # Sürükleme desteği
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.grab_handle.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            # Sürükleme başladığında açık panelleri gizle
            self.shape_panel.hide()
            self.size_panel.hide()
            self.color_panel.hide()
            self.eraser_panel.hide()
            self.scrollbar_panel.hide()
            self.btn_scroll_toggle.set_checked(False)
            
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.grab_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
