"""
محرر Hex المتقدم - مشابه لـ HxD و IMHex
"""

from typing import List, Tuple, Optional, Dict
from infrastructure.logger import app_logger
from infrastructure.file_system import FileSystem


class HexEditor:
    """محرر Hex المتقدم"""

    def __init__(self):
        self.data = b''
        self.file_path = None
        self.modified = False
        self.undo_stack = []
        self.redo_stack = []

    def open_file(self, file_path: str) -> bool:
        """فتح ملف للتحرير"""
        try:
            self.data = FileSystem.read_binary(file_path)
            if self.data is None:
                return False
            self.file_path = file_path
            self.modified = False
            self.undo_stack = []
            self.redo_stack = []
            app_logger.info(f"Opened file: {file_path} ({len(self.data)} bytes)")
            return True
        except Exception as e:
            app_logger.error(f"Failed to open file: {e}")
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """حفظ الملف"""
        try:
            path = file_path or self.file_path
            if not path:
                return False
            result = FileSystem.write_binary(path, self.data)
            if result:
                self.modified = False
                app_logger.info(f"Saved file: {path}")
            return result
        except Exception as e:
            app_logger.error(f"Failed to save file: {e}")
            return False

    def get_hex_view(self, offset: int = 0, length: int = 256) -> Dict:
        """الحصول على عرض Hex للملف"""
        if not self.data:
            return {"offset": 0, "hex": "", "ascii": "", "total": 0}

        end = min(offset + length, len(self.data))
        chunk = self.data[offset:end]

        hex_lines = []
        ascii_lines = []
        for i in range(0, len(chunk), 16):
            line = chunk[i:i+16]
            hex_part = ' '.join(f'{b:02X}' for b in line)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in line)
            hex_lines.append(f"{offset+i:08X}  {hex_part:<48}  {ascii_part}")
            ascii_lines.append(ascii_part)

        return {
            "offset": offset,
            "hex": '\n'.join(hex_lines),
            "ascii": '\n'.join(ascii_lines),
            "total": len(self.data),
            "bytes": chunk
        }

    def search_hex(self, pattern: str) -> List[int]:
        """البحث عن نمط Hex"""
        try:
            pattern_bytes = bytes.fromhex(pattern.replace(' ', ''))
            offsets = []
            for i in range(len(self.data) - len(pattern_bytes) + 1):
                if self.data[i:i+len(pattern_bytes)] == pattern_bytes:
                    offsets.append(i)
            return offsets
        except Exception as e:
            app_logger.error(f"Search failed: {e}")
            return []

    def search_text(self, text: str, encoding: str = 'ascii') -> List[int]:
        """البحث عن نص"""
        try:
            pattern = text.encode(encoding)
            offsets = []
            for i in range(len(self.data) - len(pattern) + 1):
                if self.data[i:i+len(pattern)] == pattern:
                    offsets.append(i)
            return offsets
        except Exception as e:
            app_logger.error(f"Search failed: {e}")
            return []

    def replace_hex(self, old_pattern: str, new_pattern: str) -> int:
        """استبدال نمط Hex"""
        try:
            old_bytes = bytes.fromhex(old_pattern.replace(' ', ''))
            new_bytes = bytes.fromhex(new_pattern.replace(' ', ''))
            count = 0
            i = 0
            while i <= len(self.data) - len(old_bytes):
                if self.data[i:i+len(old_bytes)] == old_bytes:
                    self.data = self.data[:i] + new_bytes + self.data[i+len(old_bytes):]
                    count += 1
                    i += len(new_bytes)
                else:
                    i += 1
            if count > 0:
                self.modified = True
            return count
        except Exception as e:
            app_logger.error(f"Replace failed: {e}")
            return 0

    def patch_at_offset(self, offset: int, new_bytes: bytes) -> bool:
        """تعديل بايتات في موقع محدد"""
        try:
            if offset + len(new_bytes) > len(self.data):
                return False
            self.undo_stack.append((offset, self.data[offset:offset+len(new_bytes)]))
            self.data = self.data[:offset] + new_bytes + self.data[offset+len(new_bytes):]
            self.modified = True
            app_logger.info(f"Patched {len(new_bytes)} bytes at offset {hex(offset)}")
            return True
        except Exception as e:
            app_logger.error(f"Patch failed: {e}")
            return False

    def undo(self) -> bool:
        """التراجع عن التعديل الأخير"""
        if not self.undo_stack:
            return False
        offset, old_data = self.undo_stack.pop()
        self.redo_stack.append((offset, self.data[offset:offset+len(old_data)]))
        self.data = self.data[:offset] + old_data + self.data[offset+len(old_data):]
        self.modified = True
        return True

    def redo(self) -> bool:
        """إعادة التعديل"""
        if not self.redo_stack:
            return False
        offset, data = self.redo_stack.pop()
        self.undo_stack.append((offset, self.data[offset:offset+len(data)]))
        self.data = self.data[:offset] + data + self.data[offset+len(data):]
        self.modified = True
        return True