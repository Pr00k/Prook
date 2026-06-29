"""
نافذة "حول البرنامج"
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from ui.widgets.buttons import ProokButton


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ProokSuite Pro")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel("🚀")
        logo.setStyleSheet("font-size: 64px;")
        layout.addWidget(logo)
        
        title = QLabel("ProokSuite Pro")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        version = QLabel("Version 2.0.0")
        version.setStyleSheet("color: #888899;")
        layout.addWidget(version)
        
        desc = QLabel("Professional Modding & Analysis Tool\n\n© 2025 ProokSuite. All rights reserved.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        close_btn = ProokButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)