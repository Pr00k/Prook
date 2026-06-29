"""
معلومات النظام وتشغيل الأوامر الخارجية
"""

import subprocess
import platform
import psutil
from infrastructure.logger import app_logger


class SystemManager:
    """إدارة النظام والمعلومات"""
    
    @staticmethod
    def get_os() -> str:
        return platform.system()
    
    @staticmethod
    def get_os_version() -> str:
        return platform.version()
    
    @staticmethod
    def get_cpu_count() -> int:
        return psutil.cpu_count()
    
    @staticmethod
    def get_memory_total() -> int:
        return psutil.virtual_memory().total
    
    @staticmethod
    def get_memory_available() -> int:
        return psutil.virtual_memory().available
    
    @staticmethod
    def run_command(command: str, args: str = "") -> bool:
        """تشغيل أمر خارجي مع حماية من حقن الأوامر"""
        if any(c in command for c in [';', '&', '|', '`', '$']):
            app_logger.error(f"Command injection detected: {command}")
            return False
        try:
            result = subprocess.run(f"{command} {args}", shell=True, check=False)
            return result.returncode == 0
        except Exception as e:
            app_logger.error(f"Command execution error: {e}")
            return False
    
    @staticmethod
    def get_process_by_name(name: str):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == name.lower():
                return proc
        return None