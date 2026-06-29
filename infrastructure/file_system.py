"""
عمليات الملفات - قراءة، كتابة، نسخ، حذف، التحقق من الوجود
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union
from infrastructure.logger import app_logger


class FileSystem:
    """فئة لإدارة عمليات الملفات والمجلدات"""
    
    @staticmethod
    def exists(path: Union[str, Path]) -> bool:
        return os.path.exists(path)
    
    @staticmethod
    def is_file(path: Union[str, Path]) -> bool:
        return os.path.isfile(path)
    
    @staticmethod
    def is_dir(path: Union[str, Path]) -> bool:
        return os.path.isdir(path)
    
    @staticmethod
    def read_binary(path: Union[str, Path]) -> Optional[bytes]:
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception as e:
            app_logger.error(f"Failed to read binary file {path}: {e}")
            return None
    
    @staticmethod
    def write_binary(path: Union[str, Path], data: bytes) -> bool:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            app_logger.error(f"Failed to write binary file {path}: {e}")
            return False
    
    @staticmethod
    def read_text(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            app_logger.error(f"Failed to read text file {path}: {e}")
            return None
    
    @staticmethod
    def write_text(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            app_logger.error(f"Failed to write text file {path}: {e}")
            return False
    
    @staticmethod
    def copy(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            app_logger.error(f"Failed to copy {src} to {dst}: {e}")
            return False
    
    @staticmethod
    def delete(path: Union[str, Path]) -> bool:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            app_logger.error(f"Failed to delete {path}: {e}")
            return False
    
    @staticmethod
    def size(path: Union[str, Path]) -> int:
        try:
            return os.path.getsize(path)
        except Exception:
            return 0
    
    @staticmethod
    def mkdir(path: Union[str, Path], parents: bool = True) -> bool:
        try:
            Path(path).mkdir(parents=parents, exist_ok=True)
            return True
        except Exception as e:
            app_logger.error(f"Failed to create directory {path}: {e}")
            return False