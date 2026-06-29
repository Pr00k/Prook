"""
بطاقات الميزات - عرض الميزات بشكل منظم
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from ui.design_system.colors import ColorSystem
from ui.design_system.typography import TypographySystem


class FeatureCard(QFrame):
    """بطاقة تعرض ميزة واحدة"""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, feature, parent=None):
        super().__init__(parent)
        self.feature_id = feature.id
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.surface_raised};
                border: 1px solid {colors.border};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {colors.primary};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # أيقونة
        icon_label = QLabel(feature.icon)
        icon_label.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon_label)
        
        # معلومات
        info_layout = QVBoxLayout()
        title = QLabel(feature.title)
        title.setStyleSheet(f"color: {colors.text_primary}; font-weight: bold; font-size: 14px;")
        info_layout.addWidget(title)
        
        desc = QLabel(feature.description)
        desc.setStyleSheet(f"color: {colors.text_secondary}; font-size: 11px;")
        desc.setWordWrap(True)
        info_layout.addWidget(desc)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # حالة التفعيل
        status = QLabel("✅" if feature.enabled else "❌")
        status.setStyleSheet("font-size: 16px;")
        layout.addWidget(status)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.feature_id)