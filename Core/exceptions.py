"""
استثناءات مخصصة للتطبيق
"""


class ProokException(Exception):
    """الاستثناء الأساسي للتطبيق"""
    pass


class FileOperationError(ProokException):
    """خطأ في عمليات الملفات"""
    pass


class AnalysisError(ProokException):
    """خطأ في تحليل الملفات"""
    pass


class ModError(ProokException):
    """خطأ في إدارة المودات"""
    pass


class ConfigError(ProokException):
    """خطأ في الإعدادات"""
    pass