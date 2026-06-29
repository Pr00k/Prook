"""
مدير السمات - تطبيق السمات على التطبيق
"""

from PyQt6.QtWidgets import QApplication, QWidget
from ui.design_system.colors import ColorSystem, DARK_PALETTE, LIGHT_PALETTE
from infrastructure.logger import app_logger


class ThemeManager:
    def __init__(self, theme: str = "dark"):
        self._current_theme = theme
        self.color_system = ColorSystem()
        self.color_system.set_theme(theme)
    
    def apply_theme(self, widget=None):
        target = widget or QApplication.instance()
        if target is None:
            return
        colors = self.color_system.palette
        style = self._generate_style(colors)
        target.setStyleSheet(style)
        app_logger.info(f"Theme applied: {self._current_theme}")
    
    def _generate_style(self, colors) -> str:
        return f"""
            QMainWindow, QWidget {{
                background-color: {colors.background};
                color: {colors.text_primary};
            }}
            QLabel {{
                color: {colors.text_primary};
            }}
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
            QPushButton:pressed {{
                background-color: {colors.primary_pressed};
            }}
            QPushButton:disabled {{
                background-color: {colors.text_disabled};
                color: {colors.text_secondary};
            }}
            QLineEdit, QTextEdit, QListWidget, QComboBox {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors.primary};
            }}
            QListWidget::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            QTabWidget::pane {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {colors.background};
                color: {colors.text_secondary};
                padding: 8px 16px;
                border: 1px solid {colors.border};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors.surface};
                color: {colors.text_primary};
            }}
            QScrollBar:vertical {{
                background: {colors.surface};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.text_disabled};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.text_secondary};
            }}
            QStatusBar {{
                background-color: {colors.surface};
                color: {colors.text_secondary};
                border-top: 1px solid {colors.border};
            }}
            QMenuBar {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border-bottom: 1px solid {colors.border};
            }}
            QMenuBar::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            QMenu {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            QGroupBox {{
                border: 1px solid {colors.border};
                border-radius: 6px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: {colors.text_secondary};
            }}
        """
    
    def set_theme(self, theme: str):
        if theme != self._current_theme:
            self._current_theme = theme
            self.color_system.set_theme(theme)
            self.apply_theme()
    
    @property
    def current_theme(self) -> str:
        return self._current_theme
    
    def toggle_theme(self):
        new = "light" if self._current_theme == "dark" else "dark"
        self.set_theme(new)
        return new