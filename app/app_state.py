"""
إدارة الحالة العامة للتطبيق
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class AppState:
    """حالة التطبيق العامة"""
    current_file: Optional[str] = None
    current_file_size: int = 0
    current_file_entropy: float = 0.0
    features: Dict[str, Any] = field(default_factory=dict)
    mods: Dict[str, Any] = field(default_factory=dict)
    active_mods: list = field(default_factory=list)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    extracted_strings: list = field(default_factory=list)
    found_values: Dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    theme: str = "dark"
    font_size: int = 12
    is_processing: bool = False
    error_message: Optional[str] = None


class StateManager(QObject):
    """مدير الحالة - يبث التغييرات"""
    state_changed = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self._state = AppState()
    
    def get(self, key: str, default=None):
        return getattr(self._state, key, default)
    
    def set(self, key: str, value: Any):
        if hasattr(self._state, key):
            old = getattr(self._state, key)
            if old != value:
                setattr(self._state, key, value)
                self.state_changed.emit(key, value)
        else:
            raise AttributeError(f"Invalid state key: {key}")
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.set(key, value)
    
    @property
    def state(self) -> AppState:
        return self._state