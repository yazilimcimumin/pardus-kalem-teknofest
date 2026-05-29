import enum
from PyQt6.QtGui import QColor, QPen, QBrush
from PyQt6.QtCore import Qt

class ToolMode(enum.Enum):
    MOUSE = "mouse"
    PEN = "pen"
    HIGHLIGHTER = "highlighter"
    ERASER = "eraser"
    LINE = "line"
    ARROW = "arrow"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"

class DrawingActionType(enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    CLEAR = "clear"
    ERASE_MODIFY = "erase_modify"

class DrawingAction:
    """Çizim işlemlerini geri alıp ileri alabilmek için tutan komut nesnesi"""
    def __init__(self, action_type: DrawingActionType, items):
        self.action_type = action_type
        self.items = items # Etkilenen QGraphicsItem listesi veya sözlük (ERASE_MODIFY için)

class DrawingEngine:
    """Çizim özelliklerini (renk, kalınlık vb.) ve Geri Al / İleri Al yığınını yöneten çekirdek"""
    def __init__(self):
        # Varsayılan Çizim Ayarları
        self._color = QColor(255, 0, 0) # Kırmızı
        self._pen_width = 3
        self._highlighter_width = 15
        self._active_tool = ToolMode.PEN

        # Çekirdek Yığınlar (Stacks)
        self.undo_stack = []
        self.redo_stack = []

    # Getters & Setters
    def get_color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        self._color = color

    def get_pen_width(self) -> int:
        return self._pen_width

    def set_pen_width(self, width: int):
        self._pen_width = width

    def get_highlighter_width(self) -> int:
        return self._highlighter_width

    def set_highlighter_width(self, width: int):
        self._highlighter_width = width

    def get_active_tool(self) -> ToolMode:
        return self._active_tool

    def set_active_tool(self, tool: ToolMode):
        self._active_tool = tool

    def get_pen(self, opacity: int = 255) -> QPen:
        """Geçerli araç ve ayarlara göre QPen oluşturur"""
        pen = QPen()
        color = QColor(self._color)

        if self._active_tool == ToolMode.HIGHLIGHTER:
            color.setAlpha(120) # Vurgulayıcı için yarı şeffaflık
            pen.setWidth(self._highlighter_width)
            pen.setCapStyle(Qt.PenCapStyle.SquareCap) # Düz kesim
        else:
            color.setAlpha(opacity)
            pen.setWidth(self._pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap) # Yumuşak yuvarlak köşeler
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        pen.setColor(color)
        return pen

    def get_brush(self) -> QBrush:
        """Şekil çizimlerinde yarı saydam dolgu için QBrush oluşturur"""
        if self._active_tool in [ToolMode.RECTANGLE, ToolMode.CIRCLE]:
            # İçi hafif renklendirilmiş yarı saydam brush
            fill_color = QColor(self._color)
            fill_color.setAlpha(20)
            return QBrush(fill_color)
        return QBrush(Qt.BrushStyle.NoBrush)

    # Undo / Redo Çekirdek Mantığı
    def push_action(self, action_type: DrawingActionType, items):
        """Yeni bir çizim aksiyonunu geri al yığınına ekler ve ileri al yığınını temizler"""
        if not items:
            return
        action = DrawingAction(action_type, items)
        self.undo_stack.append(action)
        self.redo_stack.clear() # Yeni çizim yapılınca ileri al yığını sıfırlanır

    def undo(self, scene) -> bool:
        """Son yapılan işlemi geri alır."""
        if not self.undo_stack:
            return False

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        if action.action_type == DrawingActionType.ADD:
            # Eklenen vektörleri sahneden çıkar
            for item in action.items:
                scene.removeItem(item)
        elif action.action_type == DrawingActionType.REMOVE:
            # Silinen vektörleri sahneye geri ekle
            for item in action.items:
                scene.addItem(item)
        elif action.action_type == DrawingActionType.CLEAR:
            # Temizlenen tüm vektörleri sahneye geri ekle
            for item in action.items:
                scene.addItem(item)
        elif action.action_type == DrawingActionType.ERASE_MODIFY:
            # Kısmi silme geri alma: eklenen yeni parçaları kaldır, silinen eski parçaları ekle
            for item in action.items.get("added", []):
                scene.removeItem(item)
            for item in action.items.get("removed", []):
                scene.addItem(item)

        return True

    def redo(self, scene) -> bool:
        """Geri alınan son işlemi ileri alır."""
        if not self.redo_stack:
            return False

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        if action.action_type == DrawingActionType.ADD:
            # Çıkarılan vektörleri sahneye geri ekle
            for item in action.items:
                scene.addItem(item)
        elif action.action_type == DrawingActionType.REMOVE:
            # Silinen vektörleri sahneden tekrar çıkar
            for item in action.items:
                scene.removeItem(item)
        elif action.action_type == DrawingActionType.CLEAR:
            # Geri getirilen tüm vektörleri sahneden tekrar çıkar
            for item in action.items:
                scene.removeItem(item)
        elif action.action_type == DrawingActionType.ERASE_MODIFY:
            # Kısmi silme ileri alma: eklenen yeni parçaları ekle, silinen eski parçaları çıkar
            for item in action.items.get("added", []):
                scene.addItem(item)
            for item in action.items.get("removed", []):
                scene.removeItem(item)

        return True
