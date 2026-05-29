import math
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPointF, QRectF, QEvent, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap, QColor, QTransform, QMouseEvent, QTouchEvent, QPen, QBrush
from core.engine import ToolMode, DrawingEngine, DrawingActionType
from core.gestures import TouchGestureEngine


class _InternalGraphicsView(QGraphicsView):
    """Şeffaf arka planlı iç QGraphicsView — doğrudan pencere olarak kullanılmaz,
    CanvasOverlay QWidget'ının içine gömülür."""

    def __init__(self, engine: DrawingEngine, parent_overlay, parent_widget=None):
        super().__init__(parent_widget)
        self.engine = engine
        self.parent_overlay = parent_overlay

        # ── Şeffaflık — QGraphicsView'ın kendi arka planını boyamasını engelle ──
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")

        # Viewport seviyesi
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.viewport().setAutoFillBackground(False)
        self.viewport().setStyleSheet("background: transparent;")

        # Scrollbarları Gizle
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Görünüm Performans & Kalite Ayarları
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Çerçeve (frame) yok
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

    def drawBackground(self, painter, rect):
        """Varsayılan arka plan boyamasını tamamen devre dışı bırak —
        ayrıproje/drawing_canvas.py'deki CompositionMode_Source stratejisi."""
        painter.save()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(rect, Qt.GlobalColor.transparent)
        painter.restore()

    def paintEvent(self, event):
        super().paintEvent(event)

        # Çizim modundayken ekranın etrafını mavi çerçeveyle kapla
        if self.engine.get_active_tool() != ToolMode.MOUSE and self.parent_overlay.isVisible():
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(0, 102, 255, 220), 4)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
            painter.end()


class CanvasOverlay(QWidget):
    """Tam ekran çizim katmanı. Şeffaf QWidget sarmalayıcısı içinde
    QGraphicsView/QGraphicsScene mimarisi barındırır.

    ayrıproje/drawing_window.py + drawing_canvas.py stratejisi:
    QWidget (şeffaf pencere) → QGraphicsView (şeffaf child)
    """
    def __init__(self, engine: DrawingEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        # ── Pencere Bayrakları (ayrıproje/drawing_overlay.py ile aynı) ──
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )

        # ── QWidget Seviyesi Şeffaflık (ayrıproje/drawing_canvas.py ile birebir) ──
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")

        # ── İç Düzen ──
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── İç QGraphicsView ──
        self.view = _InternalGraphicsView(engine, self, self)
        layout.addWidget(self.view)

        # ── Sahne ──
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.view.setScene(self.scene)

        # Dokunma ve Jest Ayarları
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.gesture_engine = TouchGestureEngine(self.view)
        self.gesture_engine.zoom_triggered.connect(self.on_gesture_zoom)
        self.gesture_engine.pan_triggered.connect(self.on_gesture_pan)
        self.gesture_engine.gesture_started.connect(self.on_gesture_start)
        self.gesture_engine.gesture_finished.connect(self.on_gesture_finish)

        # Arka Plan Ekran Görüntüsü Elemanı
        self.background_item = QGraphicsPixmapItem()
        self.background_item.setZValue(-100)  # En arkada durması için
        self.scene.addItem(self.background_item)

        # Çizim Değişkenleri
        self.current_item = None
        self.start_point = QPointF(0, 0)
        self.active_stroke_items = []  # Tek bir çizim hareketindeki silinen veya eklenenler
        self.erase_removed_items = []  # Kısmi silme için silinen orijinal elemanlar
        self.erase_added_items = []    # Kısmi silme için eklenen yeni elemanlar

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
        self.hud_label.hide()  # Varsayılan olarak gizli (100% iken)

        # ── Fare olaylarını view'dan yakala ──
        self.view.viewport().installEventFilter(self)

    def paintEvent(self, event):
        """ayrıproje/drawing_canvas.py ile birebir aynı strateji:
        CompositionMode_Source ile şeffaf temizle, sonra çocukları çiz."""
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.end()
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(QRectF(self.rect()))
        # HUD Göstergesini sağ üst köşeye konumlandır
        self.hud_label.move(self.width() - self.hud_label.width() - 20, 20)

    # ── Ekran Dondurma (Screenshot) Fonksiyonu ──
    def freeze_screen(self, toolbar, callback=None):
        """Arka planı tamamen şeffaf tutarak çizim katmanını gösterir (ayrıproje stratejisi)"""
        from PyQt6.QtWidgets import QApplication

        # Arka plan resmini sakla/gizle, doğrudan şeffaf ekran üzerine çiziyoruz
        self.background_item.hide()
        self.scene.update()

        # Canvas'ı göster ve öne çıkar
        self.show()
        self.raise_()
        QApplication.processEvents()

        toolbar.show()
        toolbar.raise_()

        if callback:
            callback()

    def unfreeze_screen(self):
        """Çizim modunu kapatıp şeffaf katmanı gizler"""
        self.background_item.hide()
        self.reset_view()
        self.hide()

    # ── Görünüm Kontrolü ──
    def reset_view(self):
        """Kamera dönüşümlerini ve zoom oranını sıfırlar"""
        self.view.setTransform(QTransform())
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

    # ── JEST ALICILARI (TouchGestureEngine Sinyal Bağlantıları) ──
    def on_gesture_start(self):
        self.is_panning = True
        self.initial_transform = self.view.transform()
        if self.current_item:
            # Çizim yarıda kaldıysa iptal et veya temizle
            self.scene.removeItem(self.current_item)
            self.current_item = None

    def on_gesture_zoom(self, zoom_factor, center):
        # Zoom sınırları koyalım (%50 ile %800 arası)
        old_zoom = self.view.transform().m11()
        new_zoom = old_zoom * zoom_factor
        if new_zoom < 0.5:
            zoom_factor = 0.5 / old_zoom
        elif new_zoom > 8.0:
            zoom_factor = 8.0 / old_zoom

        # Belirlenen merkeze göre sahneyi ölçekle
        scene_pos = self.view.mapToScene(center.toPoint())
        self.view.scale(zoom_factor, zoom_factor)

        # Ölçekleme sonrası kaymayı düzelt
        new_center = self.view.mapFromScene(scene_pos)
        delta = new_center - center.toPoint()
        self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() + delta.x())
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() + delta.y())

        self.current_zoom = self.view.transform().m11()
        self.update_hud()

    def on_gesture_pan(self, dx, dy):
        # Görünümü kaydır
        self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() - int(dx))
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() - int(dy))

    def on_gesture_finish(self):
        # Çok kısa bir süre çizim yapılmasını engellemek için gecikme ekleyelim
        QTimer.singleShot(100, self.finish_pan_lock)

    def finish_pan_lock(self):
        self.is_panning = False

    # ── DOKUNMATİK EKRAN GİRİŞ YÖNETİMİ ──
    def eventFilter(self, obj, event):
        """View'ın viewport'undan gelen fare olaylarını yakala ve çizim mantığına yönlendir"""
        if obj is self.view.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                self._handle_mouse_press(event)
                return True
            elif event.type() == QEvent.Type.MouseMove:
                self._handle_mouse_move(event)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._handle_mouse_release(event)
                return True
            elif event.type() in [QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd]:
                is_gesture = self.gesture_engine.handle_touch_event(event)
                if is_gesture:
                    return True
        return super().eventFilter(obj, event)

    # ── FARE YÖNETİMİ (Mouse Press, Move, Release) ──
    def _handle_mouse_press(self, event):
        if self.is_panning:
            return

        # Çizim modunda değilsek veya sol tık dışında bir şeye tıklanmışsa işlem yapma
        if self.engine.get_active_tool() == ToolMode.MOUSE or event.button() != Qt.MouseButton.LeftButton:
            return

        # Sahnede tıklandığı koordinatı al (Ölçeklemeye göre hesaplanır)
        self.start_point = self.view.mapToScene(event.position().toPoint())
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
            self.erase_removed_items.clear()
            self.erase_added_items.clear()
            self.erase_at(self.start_point)

    def _handle_mouse_move(self, event):
        if self.is_panning or (not self.current_item and self.engine.get_active_tool() != ToolMode.ERASER):
            return

        current_point = self.view.mapToScene(event.position().toPoint())
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

    def _handle_mouse_release(self, event):
        if self.is_panning:
            return

        tool = self.engine.get_active_tool()

        # Çizim tamamlandıysa Undo/Redo yığınına ekle
        if self.current_item:
            self.engine.push_action(DrawingActionType.ADD, self.active_stroke_items.copy())
            self.current_item = None

        elif tool == ToolMode.ERASER:
            # Kısmi silme işlemini tek bir geri alınabilir aksiyon olarak kaydet
            if self.erase_removed_items or self.erase_added_items:
                self.engine.push_action(DrawingActionType.ERASE_MODIFY, {
                    "removed": self.erase_removed_items.copy(),
                    "added": self.erase_added_items.copy()
                })
            self.erase_removed_items.clear()
            self.erase_added_items.clear()

        self.active_stroke_items.clear()

    # ── Noktasal Silgi Mantığı (Kısmi Yol Silme) ──
    def erase_at(self, scene_pos: QPointF):
        """Silgi koordinatına temas eden çizim parçalarını kısmi olarak siler.
        QPainterPath elemanlarında sadece dokunulan segment silinir, geri kalan korunur."""
        global_size = self.engine.get_pen_width()
        eraser_size = max(20, global_size * 4)

        erase_rect = QRectF(
            scene_pos.x() - eraser_size / 2,
            scene_pos.y() - eraser_size / 2,
            eraser_size,
            eraser_size
        )

        items = self.scene.items(erase_rect)
        for item in items:
            if item == self.background_item:
                continue
            # Orijinal silinmiş elemanları tekrar işlemeye gerek yok
            if item in self.erase_removed_items:
                continue

            if isinstance(item, QGraphicsPathItem):
                self._partial_erase_path(item, scene_pos, eraser_size)
            elif isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem)):
                # Şekil elemanlarını doğrudan kaldır (bölünemez)
                self.scene.removeItem(item)
                if item in self.erase_added_items:
                    self.erase_added_items.remove(item)
                else:
                    self.erase_removed_items.append(item)

    def _partial_erase_path(self, item: QGraphicsPathItem, center: QPointF, eraser_size: float):
        """QPainterPath elemanını silgi noktasından böler.
        Silginin dokunmadığı segmentleri yeni path elemanları olarak sahneye geri ekler."""
        path = item.path()
        pen = item.pen()

        # Path'in tüm noktalarını çıkar
        points = []
        for i in range(path.elementCount()):
            el = path.elementAt(i)
            points.append(QPointF(el.x, el.y))

        if len(points) < 2:
            self.scene.removeItem(item)
            if item in self.erase_added_items:
                self.erase_added_items.remove(item)
            else:
                self.erase_removed_items.append(item)
            return

        # Noktaları segmentlere ayır: silginin dokunmadığı ardışık noktalar birer segment oluşturur
        eraser_radius_sq = (eraser_size / 2) ** 2
        segments = []
        current_segment = []

        for pt in points:
            dx = pt.x() - center.x()
            dy = pt.y() - center.y()
            dist_sq = dx * dx + dy * dy

            if dist_sq <= eraser_radius_sq:
                # Bu nokta silgi alanında — mevcut segmenti bitir
                if len(current_segment) >= 2:
                    segments.append(current_segment)
                current_segment = []
            else:
                current_segment.append(pt)

        if len(current_segment) >= 2:
            segments.append(current_segment)

        # Orijinal veya geçici elemanı sahneden kaldır
        self.scene.removeItem(item)
        if item in self.erase_added_items:
            self.erase_added_items.remove(item)
        else:
            self.erase_removed_items.append(item)

        # Kalan segmentlerden yeni path elemanları oluştur
        for seg in segments:
            new_path = QPainterPath()
            new_path.moveTo(seg[0])
            for pt in seg[1:]:
                new_path.lineTo(pt)

            new_item = QGraphicsPathItem()
            new_item.setPath(new_path)
            new_item.setPen(pen)
            self.scene.addItem(new_item)
            self.erase_added_items.append(new_item)

    # ── Ok Çizim Matematik Asistanı ──
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
        arrow_angle = math.pi / 6.0  # 30 derece

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

    # ── Hızlı Ekran Temizleme ──
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
