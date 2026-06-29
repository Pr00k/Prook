"""
نظام الترجمة المتقدم - Singleton
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from PyQt6.QtWidgets import QWidget, QApplication
from infrastructure.logger import app_logger


class Translator:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._current_language = "en"
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
        self._initialized = True

    def _load_translations(self):
        # تحديد مسار المشروع
        project_root = Path(__file__).parent.parent
        lang_path = project_root / "resources" / "languages"
        
        if not lang_path.exists():
            app_logger.warning(f"Languages folder not found: {lang_path}")
            self._translations["en"] = {}
            return
        for file in lang_path.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang = data.get("language", file.stem)
                    self._translations[lang] = data.get("translations", {})
                    app_logger.info(f"Loaded language: {lang}")
            except Exception as e:
                app_logger.error(f"Failed to load {file}: {e}")
        if "en" not in self._translations:
            self._translations["en"] = {}
        if "ar" not in self._translations:
            self._translations["ar"] = {}

    def set_language(self, lang: str):
        if lang in self._translations:
            self._current_language = lang
            app_logger.info(f"Language set to: {lang}")
        else:
            app_logger.warning(f"Language {lang} not found, using 'en'")
            self._current_language = "en"

    def translate(self, text: str) -> str:
        if not text:
            return text
        if self._current_language == "en":
            return text
        translations = self._translations.get(self._current_language, {})
        if text in translations:
            return translations[text]
        return text

    def apply_to_widget(self, widget: QWidget):
        if hasattr(widget, 'text'):
            original = widget.text()
            if original:
                translated = self.translate(original)
                if translated != original:
                    widget.setText(translated)
        if hasattr(widget, 'placeholderText'):
            original = widget.placeholderText()
            if original:
                translated = self.translate(original)
                if translated != original:
                    widget.setPlaceholderText(translated)
        if hasattr(widget, 'windowTitle'):
            original = widget.windowTitle()
            if original:
                translated = self.translate(original)
                if translated != original:
                    widget.setWindowTitle(translated)
        if hasattr(widget, 'toolTip'):
            original = widget.toolTip()
            if original:
                translated = self.translate(original)
                if translated != original:
                    widget.setToolTip(translated)
        for child in widget.children():
            if isinstance(child, QWidget):
                self.apply_to_widget(child)

    def apply_to_all(self):
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                self.apply_to_widget(widget)

    @property
    def current_language(self) -> str:
        return self._current_language

    @property
    def available_languages(self) -> List[str]:
        return list(self._translations.keys())