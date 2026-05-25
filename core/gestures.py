import math
from PyQt6.QtCore import QObject, QPointF, pyqtSignal, QEvent
from PyQt6.QtGui import QTouchEvent

class TouchGestureEngine(QObject):
    """Dokunmatik ekrandan gelen raw QTouchEvent verilerini analiz eden motor.
    Tek parmak çizim, iki parmak kıstırma (zoom) ve kaydırma (pan) hareketlerini yönetir.
    """
    # Sinyaller
    zoom_triggered = pyqtSignal(float, QPointF) # (zoom_factor, center_point)
    pan_triggered = pyqtSignal(float, float) # (dx, dy)
    gesture_started = pyqtSignal()
    gesture_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.in_gesture = False
        
        # İlk dokunma durumları
        self.initial_distance = 1.0
        self.initial_midpoint = QPointF(0, 0)
        self.last_midpoint = QPointF(0, 0)

    def handle_touch_event(self, event: QTouchEvent) -> bool:
        """Gelen dokunma olayını işler. Eğer iki parmak jesti tespit edilirse True döner."""
        points = event.points()
        num_points = len(points)

        # Sadece aktif (basılı veya hareket eden) dokunma noktalarını filtrele
        active_points = [p for p in points if p.state() != QTouchEvent.TouchPointState.Released]
        num_active = len(active_points)

        if event.type() == QEvent.Type.TouchBegin:
            self.in_gesture = False
            return False

        elif event.type() == QEvent.Type.TouchUpdate:
            if num_active == 2:
                # İki parmak hareketi başladı veya devam ediyor
                p1 = active_points[0].position()
                p2 = active_points[1].position()

                # Mesafeyi hesapla (Euclidean distance)
                dx = p1.x() - p2.x()
                dy = p1.y() - p2.y()
                current_distance = math.hypot(dx, dy)
                if current_distance < 5.0:
                    current_distance = 5.0 # Sıfıra bölme hatası önleme

                # Orta noktayı hesapla
                current_midpoint = QPointF((p1.x() + p2.x()) / 2.0, (p1.y() + p2.y()) / 2.0)

                if not self.in_gesture:
                    # Jesti başlat
                    self.in_gesture = True
                    self.initial_distance = current_distance
                    self.initial_midpoint = current_midpoint
                    self.last_midpoint = current_midpoint
                    self.gesture_started.emit()
                else:
                    # Yakınlaştırma (zoom) oranını hesapla
                    zoom_factor = current_distance / self.initial_distance
                    
                    # Kaydırma (pan) değişimlerini hesapla
                    pdx = current_midpoint.x() - self.last_midpoint.x()
                    pdy = current_midpoint.y() - self.last_midpoint.y()
                    
                    # Sinyalleri gönder
                    self.zoom_triggered.emit(zoom_factor, current_midpoint)
                    self.pan_triggered.emit(pdx, pdy)
                    
                    # Son konumları güncelle (pan için relative fark alıyoruz, zoom için absolute)
                    self.last_midpoint = current_midpoint
                    
                return True # Bu olayı biz işledik, çizim olarak algılanmasını önlüyoruz.
            
            elif num_active > 2:
                # İkiden fazla parmak varsa çizimi engelle
                return True

            else:
                # Tek parmak varsa jest modunu sonlandır
                if self.in_gesture:
                    self.in_gesture = False
                    self.gesture_finished.emit()
                return False

        elif event.type() == QEvent.Type.TouchEnd:
            if self.in_gesture:
                self.in_gesture = False
                self.gesture_finished.emit()
            return False

        return False
