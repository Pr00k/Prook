"""
إدارة الإعدادات - تحميل وحفظ من/إلى QSettings و config.json
"""

import os
import json
from pathlib import Path
from typing import Any
from PyQt6.QtCore import QSettings


class AppConfig:
    """فئة إدارة الإعدادات"""
    
    def __init__(self, settings: QSettings):
        self.settings = settings
        # تحديد مسار المشروع
        self.project_root = Path(__file__).parent.parent
        self._config_file = self.project_root / "config.json"
        self._data = self._load_config()
    
    def _load_config(self) -> dict:
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> dict:
        return {
            "language": "en",
            "theme": "dark",
            "font_size": 12,
            "features_path": "resources/features/",
            "mods_path": "resources/mods/",
            "languages_path": "resources/languages/",
            "icons_path": "resources/icons/",
            "logs_path": "logs/",
            "max_file_size_mb": 500,
            "auto_backup": True,
            "shield_enabled": True,
            "shield_level": "maximum",
            "encryption_key": "ProokSuite2025_SuperSecureKey!"
        }
    
    @property
    def language(self) -> str:
        return self.settings.value("language", self._data.get("language", "en"))
    
    @language.setter
    def language(self, value: str):
        self.settings.setValue("language", value)
    
    @property
    def theme(self) -> str:
        return self.settings.value("theme", self._data.get("theme", "dark"))
    
    @theme.setter
    def theme(self, value: str):
        self.settings.setValue("theme", value)
    
    @property
    def font_size(self) -> int:
        return int(self.settings.value("font_size", self._data.get("font_size", 12)))
    
    @font_size.setter
    def font_size(self, value: int):
        self.settings.setValue("font_size", value)
    
    @property
    def features_path(self) -> str:
        return str(self.project_root / self._data.get("features_path", "resources/features/"))
    
    @property
    def mods_path(self) -> str:
        return str(self.project_root / self._data.get("mods_path", "resources/mods/"))
    
    @property
    def languages_path(self) -> str:
        return str(self.project_root / self._data.get("languages_path", "resources/languages/"))
    
    @property
    def logs_path(self) -> str:
        return str(self.project_root / self._data.get("logs_path", "logs/"))
    
    @property
    def max_file_size(self) -> int:
        return self._data.get("max_file_size_mb", 500) * 1024 * 1024
    
    @property
    def auto_backup(self) -> bool:
        return self._data.get("auto_backup", True)
    
    @property
    def shield_enabled(self) -> bool:
        return self._data.get("shield_enabled", True)
    
    @property
    def shield_level(self) -> str:
        return self._data.get("shield_level", "maximum")
    
    @property
    def encryption_key(self) -> bytes:
        return self._data.get("encryption_key", "ProokSuite2025_SuperSecureKey!").encode()
    
    def save(self):
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")