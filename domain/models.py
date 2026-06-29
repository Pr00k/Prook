"""
نماذج البيانات المستخدمة في التطبيق
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Feature:
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


@dataclass
class Mod:
    id: str
    name: str
    description: str
    version: str
    author: str
    enabled: bool = False
    category: str = "General"


@dataclass
class AnalysisResult:
    file_path: str
    size: int
    entropy: float
    strings: List[str]
    variables: Dict[str, List[str]]
    is_encrypted: bool = False
    is_compressed: bool = False