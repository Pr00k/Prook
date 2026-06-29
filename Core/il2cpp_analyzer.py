"""
محرك تحليل IL2CPP - استخراج العناوين والهياكل من ألعاب Unity
"""

import os
import json
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from infrastructure.logger import app_logger
from infrastructure.file_system import FileSystem


class IL2CPPAnalyzer:
    """تحليل ألعاب Unity IL2CPP"""

    @staticmethod
    def dump_il2cpp(libil2cpp_path: str, metadata_path: str, output_dir: str) -> bool:
        """
        تشغيل Il2CppDumper لاستخراج هياكل IL2CPP
        
        Args:
            libil2cpp_path: مسار ملف libil2cpp.so
            metadata_path: مسار ملف global-metadata.dat
            output_dir: مجلد الإخراج
        
        Returns:
            نجاح أو فشل العملية
        """
        try:
            # البحث عن Il2CppDumper في المسار
            dumper_path = IL2CPPAnalyzer._find_il2cppdumper()
            if not dumper_path:
                app_logger.error("Il2CppDumper not found. Please install it.")
                return False

            # إنشاء مجلد الإخراج
            os.makedirs(output_dir, exist_ok=True)

            # تشغيل Il2CppDumper
            cmd = [
                dumper_path,
                libil2cpp_path,
                metadata_path,
                output_dir
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                app_logger.info(f"Il2CppDumper completed successfully. Output: {output_dir}")
                return True
            else:
                app_logger.error(f"Il2CppDumper failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            app_logger.error("Il2CppDumper timed out")
            return False
        except Exception as e:
            app_logger.error(f"Il2CppDumper error: {e}")
            return False

    @staticmethod
    def _find_il2cppdumper() -> Optional[str]:
        """البحث عن Il2CppDumper في النظام"""
        # قائمة المسارات المحتملة
        possible_paths = [
            "Il2CppDumper.exe",
            "Il2CppDumper",
            "Il2CppDumper/Il2CppDumper.exe",
            "tools/Il2CppDumper/Il2CppDumper.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # البحث في PATH
        import shutil
        dumper = shutil.which("Il2CppDumper")
        if dumper:
            return dumper
        
        return None

    @staticmethod
    def extract_offsets_from_dump(dump_dir: str) -> Dict[str, int]:
        """
        استخراج الإزاحات من ملفات dump.cs و script.json
        
        Args:
            dump_dir: مجلد الإخراج من Il2CppDumper
        
        Returns:
            قاموس باسم الدالة والإزاحة
        """
        offsets = {}
        
        # قراءة script.json
        script_json_path = os.path.join(dump_dir, "script.json")
        if os.path.exists(script_json_path):
            try:
                with open(script_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # استخراج الإزاحات من script.json
                    for method in data.get("methods", []):
                        name = method.get("name", "")
                        offset = method.get("offset", 0)
                        if offset and name:
                            offsets[name] = int(offset, 16) if isinstance(offset, str) else offset
            except Exception as e:
                app_logger.warning(f"Error reading script.json: {e}")

        # قراءة dump.cs (البحث عن العناوين)
        dump_cs_path = os.path.join(dump_dir, "dump.cs")
        if os.path.exists(dump_cs_path):
            try:
                with open(dump_cs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # البحث عن أنماط الإزاحات
                    pattern = r'// Offset: 0x([0-9A-Fa-f]+)\s+.*?(\w+)\s*\('
                    matches = re.findall(pattern, content, re.DOTALL)
                    for offset_hex, func_name in matches:
                        offsets[func_name] = int(offset_hex, 16)
            except Exception as e:
                app_logger.warning(f"Error reading dump.cs: {e}")

        app_logger.info(f"Extracted {len(offsets)} offsets from {dump_dir}")
        return offsets

    @staticmethod
    def extract_il2cpp_strings(libil2cpp_path: str) -> List[str]:
        """استخراج النصوص من libil2cpp.so"""
        strings = []
        try:
            data = FileSystem.read_binary(libil2cpp_path)
            if data:
                # استخراج النصوص باستخدام الدالة الموجودة
                from core.analysis_engine import AnalysisEngine
                strings = AnalysisEngine._extract_strings(data)
        except Exception as e:
            app_logger.error(f"Error extracting strings from libil2cpp: {e}")
        return strings