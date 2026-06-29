"""
فئة التطبيق الرئيسية
"""

import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QTimer

from ui.theme.theme_manager import ThemeManager
from ui.widgets.sidebar import Sidebar
from ui.widgets.status_bar import StatusBar
from ui.screens.home_screen import HomeScreen
from ui.screens.mods_screen import ModsScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.analyzer_screen import AnalyzerScreen
from translations.translator import Translator
from core.config import AppConfig
from domain.feature_engine import FeatureEngine
from domain.mod_engine import ModEngine
from domain.analysis_engine import AnalysisEngine
from infrastructure.logger import app_logger


class Application(QMainWindow):
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    analysis_completed = pyqtSignal(str, dict)

    def __init__(self, settings: QSettings):
        super().__init__()
        self.settings = settings
        self.config = AppConfig(settings)

        # تحديد مسار المشروع
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)

        self.translator = Translator()
        self.translator.set_language(self.config.language)
        self.theme_manager = ThemeManager(self.config.theme)
        self.feature_engine = FeatureEngine()
        self.mod_engine = ModEngine()
        self.analysis_engine = AnalysisEngine()

        self.last_analysis_results = None

        self.setup_ui()
        self.setup_connections()
        self.load_initial_data()

        self.apply_theme()
        self.apply_translation()

        self.status_changed.emit("جاهز")
        app_logger.info("Application initialized")

    def setup_ui(self):
        self.setWindowTitle("ProokSuite Pro")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(self.content_stack)

        self.home_screen = HomeScreen(self)
        self.mods_screen = ModsScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.analyzer_screen = AnalyzerScreen(self)

        self.analyzer_screen.analysis_completed.connect(self.analysis_completed)
        self.home_screen.analyze_requested.connect(lambda: self.content_stack.setCurrentIndex(3))

        self.content_stack.addWidget(self.home_screen)      # 0
        self.content_stack.addWidget(self.mods_screen)      # 1
        self.content_stack.addWidget(self.settings_screen)  # 2
        self.content_stack.addWidget(self.analyzer_screen)  # 3

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        self.content_stack.setCurrentIndex(0)
        self.sidebar.set_active("home")

    def setup_connections(self):
        self.sidebar.navigation_requested.connect(self.navigate_to)
        self.language_changed.connect(self.on_language_changed)
        self.theme_changed.connect(self.on_theme_changed)
        self.status_changed.connect(self.status_bar.set_message)

    def load_initial_data(self):
        # تحميل بمسارات نسبية من المشروع
        features_path = self.project_root / "resources" / "features"
        mods_path = self.project_root / "resources" / "mods"
        self.feature_engine.load_features(str(features_path))
        self.mod_engine.load_mods(str(mods_path))

    def navigate_to(self, page: str):
        pages = {"home": 0, "mods": 1, "settings": 2, "analyzer": 3}
        if page in pages:
            self.content_stack.setCurrentIndex(pages[page])
            self.sidebar.set_active(page)

    def apply_theme(self):
        self.theme_manager.apply_theme(self)

    def apply_translation(self):
        self.translator.apply_to_widget(self)
        self.sidebar.update_text()
        self.status_bar.update_text()
        self.home_screen.retranslate_ui()
        self.mods_screen.retranslate_ui()
        self.settings_screen.retranslate_ui()
        self.analyzer_screen.retranslate_ui()

    def on_language_changed(self, lang: str):
        self.config.language = lang
        self.translator.set_language(lang)
        self.apply_translation()

    def on_theme_changed(self, theme: str):
        self.config.theme = theme
        self.apply_theme()

    def closeEvent(self, event):
        self.settings.sync()
        app_logger.info("Application closed")
        event.accept()