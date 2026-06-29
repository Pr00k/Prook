"""
الويدجت الأساسية للتطبيق
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class BaseWidget(QWidget):
    """ويدجت أساسية مع إعدادات افتراضية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)