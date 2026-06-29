"""
خيارات منع الباند المتقدمة - حماية ديناميكية
"""

import random
import time
import hashlib
from infrastructure.logger import app_logger


class AntiBanManager:
    """مدير منع الباند المتقدم"""

    def __init__(self):
        self.enabled = False
        self.level = "Maximum"
        self.spoof_id = False
        self.hide_mods = False
        self.obfuscate = False

    def enable(self):
        self.enabled = True
        app_logger.info("Anti-Ban enabled")

    def disable(self):
        self.enabled = False
        app_logger.info("Anti-Ban disabled")

    def set_level(self, level: str):
        self.level = level
        app_logger.info(f"Anti-Ban level set to: {level}")

    def spoof_account_id(self, real_id: str) -> str:
        if not self.enabled or not self.spoof_id:
            return real_id
        fake_id = hashlib.sha256((real_id + str(time.time())).encode()).hexdigest()[:16]
        app_logger.info(f"Spoofed ID: {real_id} -> {fake_id}")
        return fake_id

    def hide_modification(self, modification: dict) -> dict:
        if not self.enabled or not self.hide_mods:
            return modification
        fake_keys = ["timestamp", "checksum", "random_data"]
        for key in fake_keys:
            modification[key] = random.randint(1000, 9999)
        app_logger.info("Modification hidden")
        return modification

    def obfuscate_value(self, value: int) -> int:
        if not self.enabled or not self.obfuscate:
            return value
        mask = random.randint(1, 255)
        obfuscated = value ^ mask
        app_logger.info(f"Value obfuscated: {value} -> {obfuscated}")
        return obfuscated

    def deobfuscate_value(self, obfuscated: int, mask: int) -> int:
        return obfuscated ^ mask