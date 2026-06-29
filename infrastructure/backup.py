"""
إدارة النسخ الاحتياطي للملفات
"""

from pathlib import Path
from infrastructure.file_system import FileSystem
from infrastructure.logger import app_logger


class BackupManager:
    """إنشاء واستعادة النسخ الاحتياطية"""
    
    @staticmethod
    def create_backup(file_path: str) -> bool:
        """إنشاء نسخة احتياطية من الملف (file_path.bak)"""
        try:
            backup_path = file_path + ".bak"
            return FileSystem.copy(file_path, backup_path)
        except Exception as e:
            app_logger.error(f"Backup creation failed for {file_path}: {e}")
            return False
    
    @staticmethod
    def restore_backup(file_path: str) -> bool:
        """استعادة النسخة الاحتياطية"""
        try:
            backup_path = file_path + ".bak"
            if not FileSystem.exists(backup_path):
                app_logger.warning(f"Backup file not found: {backup_path}")
                return False
            return FileSystem.copy(backup_path, file_path)
        except Exception as e:
            app_logger.error(f"Backup restoration failed for {file_path}: {e}")
            return False