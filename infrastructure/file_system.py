"""
عمليات الملفات - قراءة، كتابة، نسخ، حذف، التحقق من الوجود
مع دعم النسخ الاحتياطي والتوثيق والتوقيع عبر infrastructure.audit
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union
from infrastructure.logger import app_logger
from infrastructure.audit import Audit
from infrastructure.crypto import CryptoEngine


class FileSystem:
    """فئة لإدارة عمليات الملفات والمجلدات مع دعم audit (backup + signing)
    """

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
    def write_binary(path: Union[str, Path], data: bytes, user: str = "local") -> bool:
        try:
            # ensure parent exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            # compute before hash if file exists
            before_hash = None
            if Path(path).exists():
                try:
                    before_data = Path(path).read_bytes()
                    before_hash = CryptoEngine.sha256(before_data)
                except Exception:
                    before_hash = None

            # backup existing file
            try:
                Audit.backup_file(str(path))
            except Exception as e:
                app_logger.warning(f"Audit backup failed (non-fatal) for {path}: {e}")

            # write the new file
            with open(path, 'wb') as f:
                f.write(data)

            # compute after hash
            try:
                after_hash = CryptoEngine.sha256(data)
            except Exception:
                after_hash = None

            # attempt signing
            try:
                sig, pub = Audit.sign_file_if_possible(str(path), after_hash)
            except Exception as e:
                app_logger.error(f"Signing attempt failed for {path}: {e}")
                sig, pub = None, None

            # log change
            try:
                Audit.log_change(str(path), action="write_binary", user=user, before_hash=before_hash, after_hash=after_hash, signature=sig, public_key_pem=pub)
            except Exception as e:
                app_logger.error(f"Failed to record audit log for {path}: {e}")

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
    def write_text(path: Union[str, Path], content: str, encoding: str = 'utf-8', user: str = "local") -> bool:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            # compute before hash if exists
            before_hash = None
            if Path(path).exists():
                try:
                    before_data = Path(path).read_bytes()
                    before_hash = CryptoEngine.sha256(before_data)
                except Exception:
                    before_hash = None

            # backup existing file
            try:
                Audit.backup_file(str(path))
            except Exception as e:
                app_logger.warning(f"Audit backup failed (non-fatal) for {path}: {e}")

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            # compute after hash
            try:
                after_hash = CryptoEngine.sha256(content.encode(encoding))
            except Exception:
                after_hash = None

            # attempt signing
            try:
                sig, pub = Audit.sign_file_if_possible(str(path), after_hash)
            except Exception as e:
                app_logger.error(f"Signing attempt failed for {path}: {e}")
                sig, pub = None, None

            # log change
            try:
                Audit.log_change(str(path), action="write_text", user=user, before_hash=before_hash, after_hash=after_hash, signature=sig, public_key_pem=pub)
            except Exception as e:
                app_logger.error(f"Failed to record audit log for {path}: {e}")

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
