"""
نظام تسجيل متقدم مع دعم الملفات والواجهة
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


class LogSignal(QObject):
    new_log = pyqtSignal(str, str)  # level, message


class QtHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.signal = LogSignal()
    
    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        self.signal.new_log.emit(level, msg)


def setup_logging(log_file: str = None):
    """إعداد نظام التسجيل"""
    # تحديد مسار المشروع
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if log_file is None:
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    else:
        log_file = Path(log_file)
    
    # تنظيف المعالجات القديمة
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Qt
    qt_handler = QtHandler()
    qt_handler.setLevel(logging.INFO)
    qt_handler.setFormatter(formatter)
    root_logger.addHandler(qt_handler)
    
    # كونسول
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.info("=== Logging started ===")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


app_logger = get_logger("ProokSuite")