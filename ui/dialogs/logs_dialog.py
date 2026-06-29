"""
نافذة السجلات
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from ui.widgets.buttons import ProokButton, ProokDangerButton


class LogsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logs")
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        layout.addWidget(self.log_text)
        
        btn_layout = QHBoxLayout()
        refresh_btn = ProokButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_logs)
        clear_btn = ProokDangerButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        self.load_logs()
    
    def load_logs(self):
        try:
            with open("workspace/logs/app.log", 'r', encoding='utf-8') as f:
                self.log_text.setText(f.read())
        except Exception:
            self.log_text.setText("No logs found.")
    
    def clear_logs(self):
        open("workspace/logs/app.log", 'w').close()
        self.log_text.clear()