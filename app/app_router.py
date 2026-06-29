"""
مدير التنقل بين الصفحات
"""

from typing import Dict, Callable


class AppRouter:
    """يدير الانتقال بين الشاشات"""
    
    def __init__(self):
        self._routes: Dict[str, Callable] = {}
    
    def register(self, name: str, callback: Callable):
        self._routes[name] = callback
    
    def navigate(self, name: str, **kwargs):
        if name in self._routes:
            self._routes[name](**kwargs)
        else:
            raise ValueError(f"Route '{name}' not found")