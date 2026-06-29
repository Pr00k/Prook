"""
أدوات الحماية المتقدمة - تشفير، تشويش، حماية من الكشف
"""

import hashlib
import base64
import random
import string
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from infrastructure.logger import app_logger


class SecurityManager:
    """مدير الحماية المتقدم"""

    @staticmethod
    def generate_obfuscated_id() -> str:
        """توليد معرف مشوش لمنع التتبع"""
        timestamp = str(int(time.time() * 1000))
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        obfuscated = hashlib.sha256((timestamp + random_part).encode()).hexdigest()[:32]
        return obfuscated

    @staticmethod
    def encrypt_data(data: bytes, password: str) -> bytes:
        """تشفير البيانات باستخدام Fernet (AES)"""
        try:
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            return f.encrypt(data)
        except Exception as e:
            app_logger.error(f"Encryption failed: {e}")
            return data

    @staticmethod
    def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
        """فك تشفير البيانات"""
        try:
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            return f.decrypt(encrypted_data)
        except Exception as e:
            app_logger.error(f"Decryption failed: {e}")
            return encrypted_data

    @staticmethod
    def hide_modifications(data: bytes) -> bytes:
        """إخفاء التعديلات في البيانات"""
        random_bytes = bytes(random.randint(0, 255) for _ in range(16))
        return random_bytes + data + random_bytes

    @staticmethod
    def unhide_modifications(hidden_data: bytes) -> bytes:
        """استعادة البيانات الأصلية بعد الإخفاء"""
        return hidden_data[16:-16] if len(hidden_data) > 32 else hidden_data