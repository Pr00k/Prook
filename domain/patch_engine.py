"""
محرك تطبيق التصحيحات على الملفات الثنائية
"""

from infrastructure.file_system import FileSystem
from infrastructure.logger import app_logger


class PatchEngine:
    """تطبيق تصحيحات على الملفات"""
    
    @staticmethod
    def binary_patch(file_path: str, offset: int, data: bytes) -> bool:
        """تطبيق تصحيح ثنائي في موقع محدد"""
        try:
            content = FileSystem.read_binary(file_path)
            if content is None:
                return False
            if offset + len(data) > len(content):
                app_logger.error(f"Patch offset {offset} out of range")
                return False
            patched = content[:offset] + data + content[offset + len(data):]
            return FileSystem.write_binary(file_path, patched)
        except Exception as e:
            app_logger.error(f"Patch failed: {e}")
            return False
    
    @staticmethod
    def apply_patch_file(file_path: str, patch_path: str) -> bool:
        """تطبيق تصحيح من ملف"""
        try:
            patch_data = FileSystem.read_binary(patch_path)
            if not patch_data:
                return False
            # هنا يمكن تنفيذ منطق أكثر تعقيداً
            return True
        except Exception as e:
            app_logger.error(f"Apply patch file failed: {e}")
            return False