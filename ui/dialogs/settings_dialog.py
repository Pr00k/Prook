"""
نافذة الإعدادات - نسخة منفصلة (اختيارية)
"""

from PyQt6.QtWidgets import QDialog
from ui.screens.settings_screen import SettingsScreen


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(600, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.settings_screen = SettingsScreen(self)
        layout.addWidget(self.settings_screen)