"""
قوائم مخصصة بتنسيق موحد
"""

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from ui.design_system.colors import ColorSystem


class ProokList(QListWidget):
    """قائمة بتنسيق موحد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QListWidget {{
                background: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 6px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background: {colors.primary};
                color: white;
            }}
            QListWidget::item:hover {{
                background: {colors.surface_raised};
            }}
        """)