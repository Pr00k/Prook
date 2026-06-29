"""
منطقة السحب والإفلات للملفات
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from ui.design_system.colors import ColorSystem
from translations.translator import Translator


class DropZone(QWidget):
    """منطقة السحب والإفلات"""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()

        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setup_ui()
        self.set_drop_state(False)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("📁")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.icon_label)

        self.text_label = QLabel(self.translator.translate("Drag & drop a file here"))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 14px;")
        layout.addWidget(self.text_label)

        self.desc_label = QLabel(self.translator.translate("or click to browse"))
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 12px;")
        layout.addWidget(self.desc_label)

        # إضافة أنواع الملفات المدعومة
        self.supported_label = QLabel("APK • IPA • APK • SO • DEX • PE • ELF")
        self.supported_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.supported_label.setStyleSheet(f"color: {self.color_system.palette.text_disabled}; font-size: 10px; margin-top: 8px;")
        layout.addWidget(self.supported_label)

    def set_drop_state(self, is_hover: bool):
        colors = self.color_system.palette
        border_color = colors.primary if is_hover else colors.border
        bg = colors.surface_raised if is_hover else colors.surface
        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                border: 2px dashed {border_color};
                border-radius: 12px;
            }}
        """)
        self.icon_label.setText("📂" if is_hover else "📁")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_drop_state(True)

    def dragLeaveEvent(self, event):
        self.set_drop_state(False)

    def dropEvent(self, event: QDropEvent):
        self.set_drop_state(False)
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                self.file_dropped.emit(file_path)
                self.text_label.setText(f"📄 {file_path.split('/')[-1]}")

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.translate("Select a file"),
            "",
            self.translator.translate("All Files (*.*)")
        )
        if file_path:
            self.file_dropped.emit(file_path)
            self.text_label.setText(f"📄 {file_path.split('/')[-1]}")

    def update_text(self):
        """تحديث النصوص بعد تغيير اللغة"""
        self.text_label.setText(self.translator.translate("Drag & drop a file here"))
        self.desc_label.setText(self.translator.translate("or click to browse"))
        self.supported_label.setText(self.translator.translate("APK • IPA • APK • SO • DEX • PE • ELF"))