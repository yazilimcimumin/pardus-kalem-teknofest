import math
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPointF, QRectF, QEvent, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap, QColor, QTransform, QMouseEvent, QTouchEvent
from core.engine import ToolMode, DrawingEngine, DrawingActionType
from core.gestures import TouchGestureEngine

class CanvasOverlay(QGraphicsView):
    """Tam ekran çizim katmanı. QGraphicsView/QGraphicsScene mimarisini kullanarak
    vektörel ve performanslı çizim, yakınlaştırma (zoom) ve kaydırma (pan) sunar.
    """
    def __init__(self, engine: DrawingEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        # Pencere Özellikleri (Tool pencere tipi Wayland/X11 altında stays-on-top ve şeffaflık için en kararlısıdır)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        # Scrollbarları Gizle
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Görünüm Performans & Kalite Ayarları
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Sahneyi Oluştur (Scene)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Dokunma ve Jest Ayarları
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.gesture_engine = TouchGestureEngine(self)
        self.gesture_engine.zoom_triggered.connect(self.on_gesture_zoom)
        self.gesture_engine.pan_triggered.connect(self.on_gesture_pan)
        self.gesture_engine.gesture_started.connect(self.on_gesture_start)
        self.gesture_engine.gesture_finished.connect(self.on_gesture_finish)

        # Arka Plan Ekran Görüntüsü Elemanı
        self.background_item = QGraphicsPixmapItem()
        self.background_item.setZValue(-100) # En arkada durması için
        self.scene.addItem(self.background_item)

        # Çizim Değişkenleri
        self.current_item = None
        self.start_point = QPointF(0, 0)
        self.active_stroke_items = [] # Tek bir çizim hareketindeki silinen veya eklenenler
        
        # Kamera / Zoom Değişkenleri
        self.current_zoom = 1.0
        self.initial_transform = QTransform()
        self.is_panning = False

        # Şık Yakınlaştırma HUD Göstergesi (Floating Pill)
        self.hud_label = QLabel(self)
        self.hud_label.setStyleSheet("""
            background-color: rgba(30, 30, 40, 0.85);
            color: #00FFCC;
            border: 1px solid rgba(0, 255, 204, 0.3);
            border-radius: 12px;
            padding: 6px 14px;
            font-family: 'Outfit', 'Inter', sans-serif;
            font-weight: bold;
            font-size: 13px;
        """)
        self.hud_label.setText("Yüzde: 100%")
        self.hud_label.adjustSize()
        self.hud_label.hide() # Varsayılan olarak gizli (100% iken)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(QRectF(self.rect()))
        # HUD Göstergesini sağ üst köşeye konumlandır
        self.hud_label.move(self.width() - self.hud_label.width() - 20, 20)

    # Ekran Dondurma (Screenshot) Fonksiyonu
    def freeze_screen(self, toolbar, callback=None):
        """Mevcut ekranın yüksek çözünürlüklü ekran görüntüsünü alır, arka plana yükler ve canvas'ı gösterir"""
        # Ekran görüntüsünde araç çubuğunun çıkmaması için geçici olarak gizle
        toolbar.hide()
        
        # Kompozitörün (Wayland/X11) pencereyi gizlemeyi tamamlaması için kısa bir gecikme ver (120ms)
        def _do_grab():
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screenshot = screen.grabWindow(0)
                self.background_item.setPixmap(screenshot)
                self.background_item.show()
            else:
                self.background_item.hide()
            
            # Canvas'ı ve araç çubuğunu göster/öne çıkar
            self.show()
            self.raise_()
            
            toolbar.show()
            toolbar.raise_()
            
            if callback:
                callback()
                
        QTimer.singleShot(120, _do_grab)

    def unfreeze_screen(self):
        """Arka plan görüntüsünü temizler ve şeffaf moda döner"""
        self.background_item.setPixmap(QPixmap())
        self.background_item.hide()
        self.reset_view()
        self.hide()

    # Görünüm Kontrolü
    def reset_view(self):
        """Kamera dönüşümlerini ve zoom oranını sıfırlar"""
        self.setTransform(QTransform())
        self.current_zoom = 1.0
        self.hud_label.hide()

    def update_hud(self):
        """HUD zoom değerini günceller ve gösterir/gizler"""
        percentage = int(self.current_zoom * 100)
        self.hud_label.setText(f"🔍 Yakınlaştırma: {percentage}%")
        self.hud_label.adjustSize()
        self.hud_label.move(self.width() - self.hud_label.width() - 20, 20)
        
        if percentage != 100:
            self.hud_label.show()
        else:
            self.hud_label.hide()

    # JEST ALICILARI (TouchGestureEngine Sinyal Bağlantıları)
    def on_gesture_start(self):
        self.is_panning = True
        self.initial_transform = self.transform()
        if self.current_item:
            # Çizim yarıda kaldıysa iptal et veya temizle
            self.scene.removeItem(self.current_item)
            self.current_item = None

    def on_gesture_zoom(self, zoom_factor, center):
        # Zoom sınırları koyalım (%50 ile %800 arası)
        old_zoom = self.transform().m11()
        new_zoom = old_zoom * zoom_factor
        if new_zoom < 0.5:
            zoom_factor = 0.5 / old_zoom
        elif new_zoom > 8.0:
            zoom_factor = 8.0 / old_zoom

        # Belirlenen merkeze göre sahneyi ölçekle
        scene_pos = self.mapToScene(center.toPoint())
        self.scale(zoom_factor, zoom_factor)
        
        # Ölçekleme sonrası kaymayı düzelt
        new_center = self.mapFromScene(scene_pos)
        delta = new_center - center.toPoint()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

        self.current_zoom = self.transform().m11()
        self.update_hud()

    def on_gesture_pan(self, dx, dy):
        # Görünümü kaydır
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(dx))
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(dy))

    def on_gesture_finish(self):
        # Çok kısa bir süre çizim yapılmasını engellemek için gecikme ekleyelim
        QTimer.singleShot(100, self.finish_pan_lock)

    def finish_pan_lock(self):
        self.is_panning = False

    # DOKUNMATİK EKTRAN GİRİŞ YÖNETİMİ
    def event(self, event: QEvent) -> bool:
        if event.type() in [QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd]:
            # Touch event dokunmatik jest motoruna iletilir
            is_gesture = self.gesture_engine.handle_touch_event(event)
            if is_gesture:
                return True
        return super().event(event)

    # MARE YÖNETİMİ (Mouse Press, Move, Release)
    def mousePressEvent(self, event: QMouseEvent):
        if self.is_panning:
            return

        # Çizim modunda değilsek veya sol tık dışında bir şeye tıklanmışsa işlem yapma
        if self.engine.get_active_tool() == ToolMode.MOUSE or event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        # Sahnede tıklandığı koordinatı al (Ölçeklemeye göre hesaplanır)
        self.start_point = self.mapToScene(event.position().toPoint())
        tool = self.engine.get_active_tool()
        
        self.active_stroke_items.clear()

        # KALEM VE VURGULAYICI
        if tool in [ToolMode.PEN, ToolMode.HIGHLIGHTER]:
            path = QPainterPath()
            path.moveTo(self.start_point)
            
            # Yeni bir path elemanı ekle
            self.current_item = QGraphicsPathItem()
            self.current_item.setPath(path)
            self.current_item.setPen(self.engine.get_pen())
            self.scene.addItem(self.current_item)
            self.active_stroke_items.append(self.current_item)

        # ŞEKİLLER (ÇİZGİ)
        elif tool == ToolMode.LINE:
            self.current_item = QGraphicsLineItem(self.start_point.x(), self.start_point.y(), self.start_point.x(), self.start_point.y())
            self.current_item.setPen(self.engine.get_pen())
            self.scene.addItem(self.current_item)
            self.active_stroke_items.append(self.current_item)

        # ŞEKİLLER (OK)
        elif tool == ToolMode.ARROW:
            self.current_item = QGraphicsPathItem()
            self.current_item.setPen(self.engine.get_pen())
            self.scene.addItem(self.current_item)
            self.active_stroke_items.append(self.current_item)

        # ŞEKİLLER (DİKDÖRTGEN)
        elif tool == ToolMode.RECTANGLE:
            self.current_item = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
            self.current_item.setPen(self.engine.get_pen())
            self.current_item.setBrush(self.engine.get_brush())
            self.scene.addItem(self.current_item)
            self.active_stroke_items.append(self.current_item)

        # ŞEKİLLER (DAİRE)
        elif tool == ToolMode.CIRCLE:
            self.current_item = QGraphicsEllipseItem(QRectF(self.start_point, self.start_point))
            self.current_item.setPen(self.engine.get_pen())
            self.current_item.setBrush(self.engine.get_brush())
            self.scene.addItem(self.current_item)
            self.active_stroke_items.append(self.current_item)

        # SİLGİ (Eraser)
        elif tool == ToolMode.ERASER:
            self.erase_at(self.start_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning or not self.current_item and self.engine.get_active_tool() != ToolMode.ERASER:
            return

        current_point = self.mapToScene(event.position().toPoint())
        tool = self.engine.get_active_tool()

        # KALEM VE VURGULAYICI (Path Güncelleme)
        if tool in [ToolMode.PEN, ToolMode.HIGHLIGHTER]:
            path = self.current_item.path()
            path.lineTo(current_point)
            self.current_item.setPath(path)

        # DÜZ ÇİZGİ
        elif tool == ToolMode.LINE:
            self.current_item.setLine(self.start_point.x(), self.start_point.y(), current_point.x(), current_point.y())

        # OK (Arrow)
        elif tool == ToolMode.ARROW:
            arrow_path = self.get_arrow_path(self.start_point, current_point)
            self.current_item.setPath(arrow_path)

        # DİKDÖRTGEN
        elif tool == ToolMode.RECTANGLE:
            rect = QRectF(self.start_point, current_point).normalized()
            self.current_item.setRect(rect)

        # DAİRE
        elif tool == ToolMode.CIRCLE:
            rect = QRectF(self.start_point, current_point).normalized()
            self.current_item.setRect(rect)

        # SİLGİ
        elif tool == ToolMode.ERASER:
            self.erase_at(current_point)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.is_panning:
            return

        tool = self.engine.get_active_tool()
        
        # Çizim tamamlandıysa Undo/Redo yığınına ekle
        if self.current_item:
            self.engine.push_action(DrawingActionType.ADD, self.active_stroke_items.copy())
            self.current_item = None
            
        elif tool == ToolMode.ERASER and self.active_stroke_items:
            # Silgiyle kaldırılan tüm çizgileri tek bir silme eylemi olarak kaydet
            self.engine.push_action(DrawingActionType.REMOVE, self.active_stroke_items.copy())

        self.active_stroke_items.clear()
        super().mouseReleaseEvent(event)

    # Vektörel Silgi Mantığı (Collision Detection)
    def erase_at(self, scene_pos: QPointF):
        """Silgi koordinatına temas eden tüm vektör çizimleri sahneden kaldırır"""
        # Çizim boyutunun 4 katı büyüklüğünde dinamik silgi boyutu (kullanımı aşırı kolaylaştırır)
        global_size = self.engine.get_pen_width()
        eraser_size = max(20, global_size * 4)
        
        # Silgi etki alanını temsil eden kareyi oluştur
        erase_rect = QRectF(
            scene_pos.x() - eraser_size/2,
            scene_pos.y() - eraser_size/2,
            eraser_size,
            eraser_size
        )
        
        # Bu alana temas eden sahne elemanlarını bul
        items = self.scene.items(erase_rect)
        for item in items:
            # Arka plan ekran görüntüsünü veya zaten silinmiş elemanları silme
            if item == self.background_item or item in self.active_stroke_items:
                continue
            
            # Sadece vektörel çizim elemanlarını sil
            if isinstance(item, (QGraphicsPathItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem)):
                self.scene.removeItem(item)
                self.active_stroke_items.append(item) # Undo için kaydet

    # Ok Çizim Matematik Asistanı
    def get_arrow_path(self, start: QPointF, end: QPointF) -> QPainterPath:
        """Düzgün bir ok işareti çizen vektör yolu üretir"""
        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)
        
        # Yön açısını hesapla
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        angle = math.atan2(dy, dx)
        
        # Ok başı boyutları
        arrow_size = 15.0
        arrow_angle = math.pi / 6.0 # 30 derece
        
        # Ok başının iki yan kanadını hesapla
        p1 = end - QPointF(
            arrow_size * math.cos(angle - arrow_angle),
            arrow_size * math.sin(angle - arrow_angle)
        )
        p2 = end - QPointF(
            arrow_size * math.cos(angle + arrow_angle),
            arrow_size * math.sin(angle + arrow_angle)
        )
        
        # Ok başını yola ekle
        path.moveTo(end)
        path.lineTo(p1)
        path.lineTo(p2)
        path.lineTo(end)
        
        return path

    # Hızlı Ekran Temizleme
    def clear_canvas(self):
        """Tüm vektörel çizimleri temizler ve temizleme işlemini geri alınabilir kaydeder"""
        cleared_items = []
        
        # Sahnede bulunan tüm çizim elemanlarını bul
        for item in self.scene.items():
            if item == self.background_item:
                continue
            if isinstance(item, (QGraphicsPathItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem)):
                self.scene.removeItem(item)
                cleared_items.append(item)
                
        if cleared_items:
            # Temizleme aksiyonunu geri alınabilir olarak ekle
            self.engine.push_action(DrawingActionType.CLEAR, cleared_items)

    def paintEvent(self, event):
        # Önce varsayılan sahne çizimini yap
        super().paintEvent(event)
        
        # Çizim modundayken ve canvas açıkken ekranın etrafını mavi bir çerçeveyle kapla (etkin mod bildirimi)
        if self.engine.get_active_tool() != ToolMode.MOUSE and self.isVisible():
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Glowing mavi çerçeve kalemi
            pen = QPen(QColor(0, 102, 255, 220), 4) # 4px kalınlığında parlak mavi
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Kenarlıklardan 2px içeride olacak şekilde tam ekran çerçevesini çiz
            painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
