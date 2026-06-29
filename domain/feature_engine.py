"""
محرك الميزات المتقدم - يدعم البحث الذكي عن المتغيرات
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from infrastructure.logger import app_logger
from translations.translator import Translator
from domain.analysis_engine import AnalysisEngine
from infrastructure.file_system import FileSystem


@dataclass
class Feature:
    """نموذج الميزة مع دعم الترجمة"""
    id: str
    title: str
    description: str
    category: str
    icon: str
    command: str
    version: str = "1.0"
    author: str = "Unknown"
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    parameters: Dict = field(default_factory=dict)
    arabic_title: str = ""
    arabic_description: str = ""

    def get_title(self, lang: str = "en") -> str:
        return self.arabic_title if lang == "ar" else self.title

    def get_description(self, lang: str = "en") -> str:
        return self.arabic_description if lang == "ar" else self.description


class FeatureEngine:
    """محرك الميزات المتقدم"""

    def __init__(self):
        self._features: Dict[str, List[Feature]] = {}
        self._all_features: Dict[str, Feature] = {}
        self._translator = Translator()

    def load_features(self, path: str) -> int:
        """تحميل الميزات من ملف JSON"""
        self._features.clear()
        self._all_features.clear()

        json_path = Path(path) / "features.json"
        if not json_path.exists():
            app_logger.warning(f"Features file not found: {json_path}")
            return 0

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            lang = self._translator.current_language

            for item in data:
                feature = Feature(
                    id=item.get("id", ""),
                    title=item.get("title", {}).get("en", item.get("title", "")),
                    description=item.get("description", {}).get("en", item.get("description", "")),
                    category=item.get("category", "Uncategorized"),
                    icon=item.get("icon", "📦"),
                    command=item.get("command", ""),
                    version=item.get("version", "1.0"),
                    author=item.get("author", "Unknown"),
                    enabled=item.get("enabled", True),
                    tags=item.get("tags", []),
                    parameters=item.get("parameters", {}),
                    arabic_title=item.get("title", {}).get("ar", item.get("title", "")),
                    arabic_description=item.get("description", {}).get("ar", item.get("description", ""))
                )

                if feature.category not in self._features:
                    self._features[feature.category] = []
                self._features[feature.category].append(feature)
                self._all_features[feature.id] = feature

            app_logger.info(f"Loaded {len(data)} features")
            return len(data)
        except Exception as e:
            app_logger.error(f"Failed to load features: {e}")
            return 0

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        return self._all_features.get(feature_id)

    def get_features_by_category(self, category: str) -> List[Feature]:
        return self._features.get(category, [])

    def get_categories(self) -> List[str]:
        return list(self._features.keys())

    def search_features(self, query: str) -> List[Feature]:
        results = []
        q = query.lower()
        for f in self._all_features.values():
            if q in f.title.lower() or q in f.id.lower() or q in f.description.lower():
                results.append(f)
        return results

    def search_variables_in_file(self, file_path: str) -> Dict[str, Any]:
        """
        البحث عن المتغيرات في ملف باستخدام محرك التحليل المتقدم
        """
        results = {
            "found_variables": [],
            "categories": {},
            "total": 0
        }

        # تحليل الملف
        analysis = AnalysisEngine.reverse_engineer_full(file_path)
        variables = analysis.get("variables", [])

        # تنظيم النتائج حسب التصنيف
        for var in variables:
            category = var.get("category", "unknown")
            if category not in results["categories"]:
                results["categories"][category] = []
            results["categories"][category].append(var)
            results["found_variables"].append(var)

        results["total"] = len(results["found_variables"])

        # إنشاء ميزات جديدة من المتغيرات المكتشفة
        for var in variables:
            var_name = var.get("name", "")
            arabic_name = var.get("arabic_name", var_name)
            category = var.get("category", "unknown")

            feature_id = f"mod_{var_name.lower()}"
            if feature_id not in self._all_features:
                feature = Feature(
                    id=feature_id,
                    title=var_name,
                    description=f"تعديل {arabic_name}",
                    category=f"Discovered - {category}",
                    icon=self._get_icon_for_category(category),
                    command=f"mod_{var_name.lower()}",
                    version="1.0",
                    author="Auto-Discovered",
                    enabled=False,
                    tags=[category, "auto_discovered"],
                    parameters={"target_variable": var_name},
                    arabic_title=arabic_name,
                    arabic_description=f"تعديل {arabic_name}"
                )
                self._add_feature(feature)

        return results

    def _get_icon_for_category(self, category: str) -> str:
        icons = {
            "money": "💰",
            "health": "❤️",
            "shield": "🛡️",
            "energy": "⚡",
            "ammo": "🔫",
            "exp": "⭐",
            "speed": "🏃",
            "coordinates": "📍",
            "boolean": "🔘",
            "emotions": "😊",
            "combat": "⚔️",
            "survival": "🏕️",
            "settings": "⚙️",
            "unknown": "📦"
        }
        return icons.get(category, "📦")

    def _add_feature(self, feature: Feature):
        if feature.category not in self._features:
            self._features[feature.category] = []
        self._features[feature.category].append(feature)
        self._all_features[feature.id] = feature
        app_logger.info(f"Auto-discovered feature: {feature.id}")

    def toggle_feature(self, feature_id: str) -> bool:
        f = self._all_features.get(feature_id)
        if f:
            f.enabled = not f.enabled
            return True
        return False