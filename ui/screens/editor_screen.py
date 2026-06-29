"""
شاشة المحرر - تحرير الإعدادات والنصوص
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from ui.widgets.buttons import ProokSuccessButton
from ui.design_system.colors import ColorSystem
from translations.translator import Translator


class EditorScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()
        self.setup_ui()
        self.retranslate_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.title_label = QLabel("✏️ Editor")
        self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color_system.palette.text_primary};")
        layout.addWidget(self.title_label)

        self.editor = QTextEdit()
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, monospace;
                font-size: 13px;
                min-height: 300px;
            }}
        """)
        self.editor.setText("Edit configuration or scripts here...")
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = ProokSuccessButton("Save", "💾")
        self.save_btn.clicked.connect(self.save_content)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def save_content(self):
        content = self.editor.toPlainText()
        QMessageBox.information(self, self.translator.translate("Success"),
                                self.translator.translate("Content saved successfully!"))

    def retranslate_ui(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title_label.setText(self.translator.translate("✏️ Editor"))
        self.save_btn.update_text()
        current = self.editor.toPlainText()
        if current == "Edit configuration or scripts here...":
            self.editor.setText(self.translator.translate("Edit configuration or scripts here..."))