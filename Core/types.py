"""
تعريفات الأنواع المستخدمة في التطبيق
"""

from typing import Any, Dict, List, Optional, Union, Callable, Tuple

# أنواع البيانات الأساسية
DataDict = Dict[str, Any]
StringList = List[str]
OptionalString = Optional[str]
OptionalInt = Optional[int]
OptionalFloat = Optional[float]
Callback = Callable[..., Any]