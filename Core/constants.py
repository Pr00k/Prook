"""
الثوابت العامة المستخدمة في جميع أنحاء التطبيق
"""

from enum import Enum, auto


class AppMode(Enum):
    HOME = auto()
    MODS = auto()
    SETTINGS = auto()
    ANALYZER = auto()
    EDITOR = auto()


class ModStatus(Enum):
    READY = "ready"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class AnalysisType(Enum):
    ENTROPY = "entropy"
    STRINGS = "strings"
    REVERSE = "reverse"
    FULL = "full"


class ThemeType(Enum):
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


# ثوابت التصميم
SPACING_SMALL = 4
SPACING_MEDIUM = 8
SPACING_LARGE = 16
SPACING_XLARGE = 24

FONT_SIZE_SMALL = 10
FONT_SIZE_MEDIUM = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_XLARGE = 18

CORNER_RADIUS_SMALL = 4
CORNER_RADIUS_MEDIUM = 8
CORNER_RADIUS_LARGE = 12

# ثوابت الأداء
THREAD_POOL_SIZE = 4
PROGRESS_UPDATE_INTERVAL = 100