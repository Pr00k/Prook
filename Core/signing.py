"""
أدوات التوقيع المتقدمة - دعم APK، IPA، EXE
"""

import subprocess
import os
import shutil
from pathlib import Path
from infrastructure.logger import app_logger


class SigningManager:
    """مدير التوقيع المتقدم"""

    @staticmethod
    def sign_apk(apk_path, keystore=None, password=None):
        """توقيع ملف APK باستخدام apksigner أو jarsigner"""
        try:
            if not os.path.exists(apk_path):
                app_logger.error(f"APK file not found: {apk_path}")
                return False

            # استخدام apksigner إذا كان متاحًا
            if shutil.which("apksigner"):
                cmd = ["apksigner", "sign", "--ks", keystore or "debug.keystore",
                       "--ks-pass", f"pass:{password or 'android'}", apk_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    app_logger.info(f"Signed APK: {apk_path}")
                    return True
                else:
                    app_logger.error(f"apksigner error: {result.stderr}")
                    return False
            else:
                # استخدام jarsigner كبديل
                cmd = ["jarsigner", "-verbose", "-sigalg", "SHA1withRSA",
                       "-digestalg", "SHA1", "-keystore", keystore or "debug.keystore",
                       "-storepass", password or "android", apk_path, "alias"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    app_logger.info(f"Signed APK: {apk_path}")
                    return True
                else:
                    app_logger.error(f"jarsigner error: {result.stderr}")
                    return False
        except Exception as e:
            app_logger.error(f"Signing failed: {e}")
            return False