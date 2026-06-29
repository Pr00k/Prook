"""
مفتاح انزلاقي (Toggle Switch) بتصميم عصري
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QBrush, QMouseEvent


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._offset = 0.0
        self.setFixedSize(50, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._animation = QPropertyAnimation(self, b"offset")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = rect.height() / 2

        if self._checked:
            bg_color = QColor(34, 197, 94)
        else:
            bg_color = QColor(150, 150, 150)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        dot_radius = rect.height() / 2 - 3
        dot_x = 3 + self._offset
        dot_y = 3
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QRect(int(dot_x), int(dot_y), int(dot_radius * 2), int(dot_radius * 2)))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
            self.toggled.emit(self._checked)

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self._animate()

    def isChecked(self):
        return self._checked

    def _animate(self):
        target = self.width() - self.height() + 3 if self._checked else 0
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(target)
        self._animation.start()

    @pyqtProperty(float)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()