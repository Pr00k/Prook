"""
مؤشرات التقدم الموحدة
"""

from PyQt6.QtWidgets import QProgressBar
from ui.design_system.colors import ColorSystem


class ProokProgress(QProgressBar):
    """شريط تقدم بتنسيق موحد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background: {colors.surface};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: {colors.primary};
                border-radius: 4px;
            }}
        """)