"""
الشريط الجانبي - أزرار التنقل
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from ui.design_system.colors import ColorSystem
from translations.translator import Translator


class SidebarButton(QPushButton):
    """زر الشريط الجانبي"""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(parent)
        self._original_text = text
        self._icon = icon
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_text()

        colors = ColorSystem().palette
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {colors.text_secondary};
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {colors.surface_raised};
                color: {colors.text_primary};
            }}
            QPushButton:checked {{
                background: {colors.primary};
                color: white;
            }}
        """)

    def update_text(self):
        translator = Translator()
        translated = translator.translate(self._original_text)
        if self._icon:
            self.setText(f"  {self._icon}  {translated}")
        else:
            self.setText(translated)

    def set_active(self, active: bool):
        self.setChecked(active)


class Sidebar(QWidget):
    """الشريط الجانبي الرئيسي"""

    navigation_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()

        self.setFixedWidth(220)
        self.nav_buttons = {}
        self.setup_ui()
        self.update_text()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        self.logo = QLabel("🚀 ProokSuite")
        self.logo.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {self.color_system.palette.text_primary};
            padding: 8px 0 16px 0;
        """)
        layout.addWidget(self.logo)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {self.color_system.palette.border}; max-height: 1px;")
        layout.addWidget(line)

        items = [
            ("home", "🏠", "Home"),
            ("mods", "🛠️", "Mods"),
            ("analyzer", "🔍", "Analyzer"),
            ("settings", "⚙️", "Settings"),
        ]
        for key, icon, label in items:
            btn = SidebarButton(label, icon)
            btn.clicked.connect(lambda checked, k=key: self._on_nav_click(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()

        # إضافة الإحصائيات
        self._create_stats_section(layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"background: {self.color_system.palette.border}; max-height: 1px; margin-top: 16px;")
        layout.addWidget(line2)

        exit_btn = SidebarButton("Exit", "🚪")
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #ef4444;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #ef4444;
                color: white;
            }}
        """)
        exit_btn.clicked.connect(self._on_exit_click)
        layout.addWidget(exit_btn)

    def _create_stats_section(self, layout):
        """إنشاء قسم الإحصائيات"""
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 10, 0, 0)
        stats_layout.setSpacing(6)

        title = QLabel("📊 Statistics")
        title.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 11px; font-weight: bold;")
        stats_layout.addWidget(title)

        # إحصائيات تجريبية
        self.files_count_label = QLabel("Files: 0")
        self.files_count_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 11px;")
        stats_layout.addWidget(self.files_count_label)

        self.mods_count_label = QLabel("Mods: 0")
        self.mods_count_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 11px;")
        stats_layout.addWidget(self.mods_count_label)

        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 11px;")
        stats_layout.addWidget(self.score_label)

        layout.addWidget(stats_container)

    def update_stats(self, files_count: int = 0, mods_count: int = 0, score: int = 0):
        """تحديث الإحصائيات"""
        if hasattr(self, 'files_count_label'):
            self.files_count_label.setText(f"Files: {files_count}")
        if hasattr(self, 'mods_count_label'):
            self.mods_count_label.setText(f"Mods: {mods_count}")
        if hasattr(self, 'score_label'):
            self.score_label.setText(f"Score: {score}")

    def _on_nav_click(self, key: str):
        self.navigation_requested.emit(key)

    def _on_exit_click(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'close'):
                parent.close()
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None

    def set_active(self, page: str):
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page)

    def update_text(self):
        for btn in self.nav_buttons.values():
            btn.update_text()
        self.logo.setText("🚀 " + self.translator.translate("ProokSuite"))