"""
نظام الألوان المتكامل للسمات الداكنة والفاتحة
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorPalette:
    background: str
    surface: str
    surface_raised: str
    text_primary: str
    text_secondary: str
    text_disabled: str
    primary: str
    primary_hover: str
    primary_pressed: str
    secondary: str
    secondary_hover: str
    success: str
    warning: str
    error: str
    info: str
    border: str
    border_focus: str
    shadow: str


DARK_PALETTE = ColorPalette(
    background="#0a0a0f",
    surface="#14141a",
    surface_raised="#1e1e2e",
    text_primary="#e8e8e8",
    text_secondary="#888899",
    text_disabled="#555566",
    primary="#3b82f6",
    primary_hover="#2563eb",
    primary_pressed="#1d4ed8",
    secondary="#8b5cf6",
    secondary_hover="#7c3aed",
    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#06b6d4",
    border="#2a2a3a",
    border_focus="#3b82f6",
    shadow="rgba(0,0,0,0.4)"
)

LIGHT_PALETTE = ColorPalette(
    background="#f0f2f5",
    surface="#ffffff",
    surface_raised="#f8f9fa",
    text_primary="#1a1a1a",
    text_secondary="#666677",
    text_disabled="#9999aa",
    primary="#3b82f6",
    primary_hover="#2563eb",
    primary_pressed="#1d4ed8",
    secondary="#8b5cf6",
    secondary_hover="#7c3aed",
    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#06b6d4",
    border="#d1d5db",
    border_focus="#3b82f6",
    shadow="rgba(0,0,0,0.1)"
)


class ColorSystem:
    _instance = None
    _current_theme = "dark"
    _palettes = {"dark": DARK_PALETTE, "light": LIGHT_PALETTE}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_theme(self, theme: str):
        if theme in self._palettes:
            self._current_theme = theme
    
    @property
    def palette(self) -> ColorPalette:
        return self._palettes.get(self._current_theme, DARK_PALETTE)
    
    def get(self, color_name: str) -> str:
        return getattr(self.palette, color_name, "#ffffff")