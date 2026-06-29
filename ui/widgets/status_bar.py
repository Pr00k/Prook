"""
شريط الحالة - يعرض الرسائل والتقدم
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from ui.design_system.colors import ColorSystem
from translations.translator import Translator


class StatusBar(QStatusBar):
    """شريط الحالة المتقدم"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()

        self.setStyleSheet(f"""
            QStatusBar {{
                background: {self.color_system.palette.surface};
                color: {self.color_system.palette.text_secondary};
                border-top: 1px solid {self.color_system.palette.border};
                padding: 2px 8px;
            }}
        """)

        self.status_label = QLabel("Ready")
        self.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)

        self.info_label = QLabel("v2.0.0")
        self.addPermanentWidget(self.info_label)

    def set_message(self, message: str, duration: int = 0):
        self.status_label.setText(self.translator.translate(message))
        if duration > 0:
            QTimer.singleShot(duration, lambda: self.status_label.setText(self.translator.translate("Ready")))

    def show_progress(self, value: int, max_value: int = 100):
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(value)

    def hide_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def update_text(self):
        """تحديث النصوص بعد تغيير اللغة"""
        current = self.status_label.text()
        if current:
            self.status_label.setText(self.translator.translate(current))