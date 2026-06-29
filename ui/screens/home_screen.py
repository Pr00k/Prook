"""
الصفحة الرئيسية - ترحيب وإجراءات سريعة
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from ui.widgets.buttons import ProokButton
from ui.widgets.drop_zone import DropZone
from ui.design_system.colors import ColorSystem
from ui.design_system.typography import TypographySystem
from translations.translator import Translator


class HomeScreen(QWidget):
    file_dropped = pyqtSignal(str)
    analyze_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()
        self.typography = TypographySystem()
        self.setup_ui()
        self.retranslate_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("🚀")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 72px;")
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("Welcome to ProokSuite Pro")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(self.typography.create_font("heading_1"))
        self.title_label.setStyleSheet(f"color: {self.color_system.palette.text_primary};")
        layout.addWidget(self.title_label)

        self.desc_label = QLabel("Professional Modding & Analysis Tool")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 16px;")
        layout.addWidget(self.desc_label)

        layout.addSpacing(20)

        self.drop_zone = DropZone(self)
        self.drop_zone.file_dropped.connect(self.file_dropped.emit)
        layout.addWidget(self.drop_zone)

        layout.addSpacing(20)

        actions = QHBoxLayout()
        actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions.setSpacing(16)

        self.analyze_btn = ProokButton("Start Analysis", "🔍")
        self.analyze_btn.clicked.connect(self.analyze_requested.emit)
        actions.addWidget(self.analyze_btn)

        layout.addLayout(actions)

        self.info_label = QLabel("Drag & drop a file or click 'Start Analysis' to begin")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 12px; margin-top: 20px;")
        layout.addWidget(self.info_label)

    def retranslate_ui(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title_label.setText(self.translator.translate("Welcome to ProokSuite Pro"))
        self.desc_label.setText(self.translator.translate("Professional Modding & Analysis Tool"))
        self.analyze_btn.update_text()
        self.info_label.setText(self.translator.translate("Drag & drop a file or click 'Start Analysis' to begin"))
        self.drop_zone.update_text()