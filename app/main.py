#!/usr/bin/env python3
"""
نقطة الدخول الرئيسية للتطبيق
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QFont, QColor
from app.application import Application
from infrastructure.logger import setup_logging, app_logger


def main():
    setup_logging()
    app_logger.info("=== ProokSuite Pro Starting ===")

    app = QApplication(sys.argv)
    app.setApplicationName("ProokSuite Pro")
    app.setOrganizationName("ProokSuite")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    splash = QSplashScreen()
    splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    splash.setStyleSheet("""
        QSplashScreen {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0a0f, stop:1 #1a1a2e);
            color: #e0e0e0;
            border-radius: 12px;
        }
    """)
    splash.showMessage("🚀 جاري تحميل ProokSuite Pro...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor("#3b82f6"))
    splash.show()
    app.processEvents()

    settings = QSettings("ProokSuite", "ProokSuite")
    window = Application(settings)

    splash.showMessage("✅ جاهز!", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor("#22c55e"))
    app.processEvents()
    QTimer.singleShot(300, splash.close)
    QTimer.singleShot(300, window.show)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()