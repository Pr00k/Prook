"""
أزرار مخصصة بأحجام وألوان متناسقة
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from ui.design_system.colors import ColorSystem
from translations.translator import Translator


class ProokButton(QPushButton):
    """زر أساسي موحد"""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(text, parent)
        self._original_text = text
        self._icon = icon
        self.setFixedHeight(36)
        self.setMinimumWidth(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_text()

        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QPushButton {{
                background: {colors.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {colors.primary_hover};
            }}
            QPushButton:pressed {{
                background: {colors.primary_pressed};
            }}
            QPushButton:disabled {{
                background: {colors.text_disabled};
                color: {colors.text_secondary};
            }}
        """)

    def update_text(self):
        """تحديث النص مع الترجمة"""
        translator = Translator()
        translated = translator.translate(self._original_text)
        if self._icon:
            self.setText(f"{self._icon} {translated}")
        else:
            self.setText(translated)


class ProokSuccessButton(ProokButton):
    """زر نجاح (أخضر)"""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(text, icon, parent)
        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QPushButton {{
                background: {colors.success};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {colors.success};
                opacity: 0.9;
            }}
        """)
        self.update_text()


class ProokDangerButton(ProokButton):
    """زر خطر (أحمر)"""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(text, icon, parent)
        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QPushButton {{
                background: {colors.error};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {colors.error};
                opacity: 0.9;
            }}
        """)
        self.update_text()