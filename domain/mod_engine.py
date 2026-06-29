"""
محرك إدارة المودات
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from infrastructure.logger import app_logger


@dataclass
class Mod:
    id: str
    name: str
    description: str
    version: str
    author: str
    enabled: bool = False
    category: str = "General"


class ModEngine:
    """يدير المودات المحملة"""
    
    def __init__(self):
        self._mods: Dict[str, Mod] = {}
        self._active_mods: List[str] = []
    
    def load_mods(self, path: str) -> int:
        """تحميل المودات من مجلد (محاكاة)"""
        # في نسخة حقيقية، نقرأ من ملفات
        app_logger.info(f"Loading mods from {path}")
        return 0
    
    def get_mod(self, mod_id: str) -> Optional[Mod]:
        return self._mods.get(mod_id)
    
    def get_all_mods(self) -> List[Mod]:
        return list(self._mods.values())
    
    def get_active_mods(self) -> List[Mod]:
        return [self._mods[mid] for mid in self._active_mods if mid in self._mods]
    
    def activate_mod(self, mod_id: str) -> bool:
        if mod_id in self._mods and mod_id not in self._active_mods:
            self._active_mods.append(mod_id)
            self._mods[mod_id].enabled = True
            app_logger.info(f"Mod activated: {mod_id}")
            return True
        return False
    
    def deactivate_mod(self, mod_id: str) -> bool:
        if mod_id in self._active_mods:
            self._active_mods.remove(mod_id)
            if mod_id in self._mods:
                self._mods[mod_id].enabled = False
            app_logger.info(f"Mod deactivated: {mod_id}")
            return True
        return False
    
    def add_mod(self, mod: Mod) -> bool:
        if mod.id not in self._mods:
            self._mods[mod.id] = mod
            return True
        return False