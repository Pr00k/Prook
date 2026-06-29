"""
نظام الخطوط - أنماط النصوص الموحدة
"""

from dataclasses import dataclass
from PyQt6.QtGui import QFont


@dataclass
class TextStyle:
    family: str
    size: int
    weight: int
    letter_spacing: int = 0
    line_height: float = 1.5


class TypographySystem:
    STYLES = {
        "heading_1": TextStyle("Segoe UI", 28, QFont.Weight.Bold),
        "heading_2": TextStyle("Segoe UI", 22, QFont.Weight.Bold),
        "heading_3": TextStyle("Segoe UI", 18, QFont.Weight.Bold),
        "heading_4": TextStyle("Segoe UI", 16, QFont.Weight.Bold),
        "body_large": TextStyle("Segoe UI", 14, QFont.Weight.Normal),
        "body": TextStyle("Segoe UI", 12, QFont.Weight.Normal),
        "body_small": TextStyle("Segoe UI", 10, QFont.Weight.Normal),
        "button": TextStyle("Segoe UI", 12, QFont.Weight.Medium),
        "code": TextStyle("Consolas", 11, QFont.Weight.Normal),
    }
    
    def get_style(self, name: str) -> TextStyle:
        return self.STYLES.get(name, self.STYLES["body"])
    
    def create_font(self, name: str) -> QFont:
        style = self.get_style(name)
        return QFont(style.family, style.size, style.weight)