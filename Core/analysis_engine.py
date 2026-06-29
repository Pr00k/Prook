"""
محرك تحليل الملفات المتقدم - دعم APK, APKS, IPA, PE, ELF, Ren'Py, Unity, IL2CPP
مع البحث المباشر عن القيم التعديلية والتحليل العميق
"""

import os
import io
import re
import math
import json
import struct
import hashlib
import zipfile
import tempfile
import shutil
import plistlib
import subprocess
import base64
from typing import List, Dict, Tuple, Optional, Any
from infrastructure.logger import app_logger
from infrastructure.file_system import FileSystem

# -------------------------------------------------------------------
# المكتبات الاختيارية - يتم استيرادها مع معالجة الأخطاء
# -------------------------------------------------------------------
try:
    import pefile
    HAS_PEFILE = True
except ImportError:
    HAS_PEFILE = False

try:
    import capstone
    HAS_CAPSTONE = True
except ImportError:
    HAS_CAPSTONE = False

try:
    from elftools.elf.elffile import ELFFile
    HAS_ELF = True
except ImportError:
    HAS_ELF = False

try:
    from androguard.core.apk import APK
    HAS_ANDROGUARD = True
    app_logger.info("androguard loaded successfully")
except ImportError:
    HAS_ANDROGUARD = False
    app_logger.warning("androguard not installed. Install: pip install androguard")

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class AnalysisEngine:
    """
    محرك تحليل الملفات المتقدم - يدعم جميع الصيغ مع البحث المباشر عن القيم التعديلية
    """

    # قائمة المتغيرات الشاملة (600+ كلمة)
    COMMON_VARIABLES = [
        "gold", "money", "coins", "cash", "gems", "diamonds",
        "health", "hp", "life", "shield", "armor", "defense",
        "energy", "mana", "mp", "ammo", "bullet", "clip",
        "experience", "exp", "xp", "level", "rank", "prestige",
        "skillpoints", "talentpoints", "upgrade", "progress",
        "speed", "jump", "gravity", "agility", "dexterity",
        "cooldown", "cd", "duration", "timer", "regen",
        "position", "x", "y", "z", "location", "teleport",
        "godmode", "invisible", "stealth", "flymode", "noclip",
        "unlimitedhealth", "unlimitedammo", "unlimitedenergy",
        "purchase", "buy", "price", "cost", "iap", "reward",
        "ad", "video", "hunger", "thirst", "fatigue", "sleep",
        "attack", "damage", "critical", "dodge", "accuracy",
        "strength", "intelligence", "wisdom", "luck", "charisma",
        "love", "hate", "trust", "respect", "fear", "anger",
        "volume", "brightness", "resolution", "fps", "graphics",
        "unity", "mono", "il2cpp", "renpy", "rpyc", "unreal",
        "save", "data", "config", "settings", "profile", "user",
        "score", "points", "token", "credit", "wallet", "bank",
        "vitality", "stamina", "endurance", "rage", "focus",
        "regen", "heal", "revive", "respawn", "infinite",
        "unlock", "all", "max", "min", "base", "current",
        "default", "temp", "new", "old", "value", "amount",
        "count", "num", "rate", "timer", "time", "duration",
        "delay", "cost", "price", "sell", "buy", "multiplier"
    ]

    PREFIXES = ["m_", "f_", "i_", "b_", "cur_", "max_", "min_", "base_",
                "total_", "current_", "default_", "temp_", "new_", "old_",
                "g_", "s_", "k_", "n_", "v_", "p_", "c_"]
    SUFFIXES = ["_value", "_amount", "_count", "_points", "_num", "_max",
                "_min", "_level", "_rate", "_regen", "_timer", "_time",
                "_duration", "_delay", "_cost", "_price", "_sell", "_buy",
                "_multiplier", "_ratio", "_percent", "_scale", "_modifier",
                "_boost", "_buff", "_debuff", "_stat", "_score", "_rank"]

    STRING_PATTERNS = [
        rb'"([^"]{4,})"',
        rb"'([^']{4,})'",
        rb'([A-Za-z0-9_]{4,})\s*=',
        rb'\b(health|hp|gold|money|coins|gems|ammo|xp|level|shield|energy|mana|purchase|reward|ad|iap|godmode|speed|jump|gravity)\b',
        rb'([A-Z][a-z]+[A-Z][a-z]+)',
        rb'[a-z]+_[a-z]+',
    ]

    TARGET_VALUES = {
        "gold": [9999, 99999, 999999, 9999999],
        "money": [9999, 99999, 999999, 9999999],
        "coins": [9999, 99999, 999999],
        "health": [9999, 99999, 999999],
        "hp": [9999, 99999, 999999],
        "ammo": [999, 9999, 99999],
        "level": [99, 999, 9999],
        "xp": [99999, 999999, 9999999],
        "experience": [99999, 999999, 9999999],
        "score": [99999, 999999, 9999999],
        "points": [99999, 999999, 9999999],
        "speed": [50.0, 100.0, 999.0],
        "jump": [50.0, 100.0, 999.0],
        "gravity": [0.1, 0.0, -0.1],
        "damage": [9999, 99999, 999999],
        "cooldown": [0.0, 0.1, 1.0],
        "duration": [9999.0, 99999.0],
        "godmode": [1],
        "invisible": [1],
        "unlimited": [1],
        "infinite": [1],
        "noclip": [1],
        "fly": [1],
        "freeze": [1],
        "purchase": [1],
        "isPurchased": [1],
        "price": [0],
        "cost": [0],
        "reward": [99999, 999999],
        "ad": [1],
        "love": [100, 999],
        "trust": [100, 999],
        "respect": [100, 999],
        "hate": [0, 1],
    }

    @staticmethod
    def analyze_file(file_path: str) -> Dict:
        """التحليل الشامل للملف مع البحث المباشر عن القيم التعديلية"""
        results = {
            "file_path": file_path,
            "size": 0,
            "entropy": 0.0,
            "strings": [],
            "variables": {},
            "hacking_values": {},
            "direct_binary_values": [],
            "hidden_numeric_values": {},
            "encrypted_values": [],
            "suspicious_patterns": [],
            "pointer_patterns": [],
            "crypto_analysis": {
                "detected_constants": [],
                "high_entropy_blocks": [],
                "potential_keys_or_tokens": []
            },
            "is_encrypted": False,
            "is_compressed": False,
            "file_type": "غير معروف",
            "file_format": "غير معروفة",
            "sections": [],
            "imports": [],
            "exports": [],
            "hash_md5": "",
            "hash_sha256": "",
            "pe_info": {},
            "elf_info": {},
            "apk_info": {},
            "ipa_info": {},
            "decrypted_data": b'',
            "auto_hex_patches": [],
            "auto_memory_mods": [],
            "auto_asm_scripts": [],
            "found_values": {},
            "score": 0,
            "game_engine": "غير معروف",
            "detected_mods": [],
            "all_strings_found": 0,
            "analysis_depth": "advanced",
            "error": None,
            "assembly_analysis": [],
            "aob_patterns": [],
            "anti_debug_detected": [],
            "obfuscation_detected": False,
            "protection_type": "None",
            "files_scanned": 0,
            "files_analyzed": [],
            "il2cpp_offsets": {}
        }

        try:
            app_logger.info(f"Starting analysis on: {file_path}")

            # إذا كان المسار مجلداً، نقوم بمسح جميع الملفات فيه
            if os.path.isdir(file_path):
                app_logger.info(f"Scanning directory: {file_path}")
                return AnalysisEngine._scan_directory(file_path)

            # قراءة الملف
            data = FileSystem.read_binary(file_path)
            if not data:
                results["error"] = "فشل قراءة الملف"
                app_logger.error("Failed to read file")
                return results

            results["size"] = len(data)
            results["hash_md5"] = hashlib.md5(data).hexdigest()
            results["hash_sha256"] = hashlib.sha256(data).hexdigest()
            results["entropy"] = AnalysisEngine._calculate_entropy(data)
            if results["entropy"] > 7.5:
                results["is_encrypted"] = True

            # تحديد نوع الملف
            file_format, file_type = AnalysisEngine._detect_format_and_type(data, file_path)
            results["file_format"] = file_format
            results["file_type"] = file_type
            app_logger.info(f"Detected format: {file_format}")

            # جمع النصوص
            all_strings = []

            # ========== معالجة APK / APKS ==========
            if file_format in ["APK", "APKS", "APKX", "XAPK"] or file_path.endswith(('.apk', '.apks', '.apkx', '.xapk')):
                app_logger.info("Analyzing Android bundle...")
                android_results = AnalysisEngine._analyze_android_bundle(file_path)
                all_strings.extend(android_results.get("strings", []))
                results["apk_info"] = android_results.get("apk_info", {})
                results["files_analyzed"] = android_results.get("files_analyzed", [])
                results["files_scanned"] = len(results["files_analyzed"])
                app_logger.info(f"Android bundle: extracted {len(android_results.get('strings', []))} strings from {results['files_scanned']} files")

            # ========== معالجة IPA ==========
            elif file_format == "IPA":
                ipa_results = AnalysisEngine._analyze_ipa(file_path)
                all_strings.extend(ipa_results.get("strings", []))
                results["ipa_info"] = ipa_results.get("ipa_info", {})

            # ========== معالجة PE ==========
            elif file_format == "PE":
                all_strings.extend(AnalysisEngine._extract_strings(data))
                if HAS_PEFILE:
                    results["pe_info"] = AnalysisEngine._analyze_pe(data)

            # ========== معالجة ELF ==========
            elif file_format in ["ELF", "SO"]:
                all_strings.extend(AnalysisEngine._extract_strings(data))
                if HAS_ELF:
                    results["elf_info"] = AnalysisEngine._analyze_elf(data)

            # ========== معالجة Ren'Py ==========
            elif file_format == "Ren'Py":
                rpy_results = AnalysisEngine._analyze_renpy(file_path)
                all_strings.extend(rpy_results.get("strings", []))

            # ========== معالجة Unity ==========
            elif file_format == "Unity":
                unity_results = AnalysisEngine._analyze_unity(data)
                all_strings.extend(unity_results.get("strings", []))

            # ========== معالجة عامة ==========
            else:
                all_strings.extend(AnalysisEngine._extract_strings(data))

            # تنظيف النصوص
            all_strings = list(set(all_strings))
            results["strings"] = all_strings[:3000]
            results["all_strings_found"] = len(all_strings)

            # ========== البحث عن المتغيرات والقيم ==========
            results["variables"] = AnalysisEngine._search_variables_smart(all_strings)
            results["hacking_values"] = AnalysisEngine._search_hacking_values(all_strings)

            # ========== البحث المباشر عن القيم التعديلية ==========
            results["direct_binary_values"] = AnalysisEngine._search_direct_binary_values(data)

            # ========== البحث عن القيم المخفية ==========
            results["hidden_numeric_values"] = AnalysisEngine._search_hidden_numeric_values(data)

            # ========== البحث عن القيم المشفرة ==========
            results["encrypted_values"] = AnalysisEngine._search_encrypted_values(data)

            # ========== البحث عن الأنماط المشبوهة ==========
            results["suspicious_patterns"] = AnalysisEngine._search_suspicious_patterns(data)

            # ========== البحث عن أنماط المؤشرات ==========
            results["pointer_patterns"] = AnalysisEngine._search_pointer_patterns(data)

            # ========== تحليل التشفير ==========
            results["crypto_analysis"]["detected_constants"] = AnalysisEngine._detect_crypto_constants(data)
            results["crypto_analysis"]["high_entropy_blocks"] = AnalysisEngine._analyze_high_entropy_blocks(data)
            results["crypto_analysis"]["potential_keys_or_tokens"] = AnalysisEngine._extract_crypto_strings_and_base64(all_strings)

            # ========== كشف المودات والمحرك ==========
            results["detected_mods"] = AnalysisEngine._detect_available_mods(results["variables"])
            results["game_engine"] = AnalysisEngine._detect_game_engine(all_strings, file_path)

            # ========== كشف الحماية ==========
            results["anti_debug_detected"] = AnalysisEngine._detect_anti_debug(data, all_strings)
            results["obfuscation_detected"] = AnalysisEngine._detect_obfuscation(data)
            results["protection_type"] = AnalysisEngine._detect_protection(data, all_strings)
            results["aob_patterns"] = AnalysisEngine._find_aob_patterns(data)

            # ========== التعديلات المقترحة ==========
            results["auto_hex_patches"] = AnalysisEngine._find_hex_patches(data)
            results["auto_memory_mods"] = AnalysisEngine._find_memory_mods(all_strings)

            if HAS_CAPSTONE:
                results["assembly_analysis"] = AnalysisEngine._analyze_assembly_features(data, file_format)

            # ========== حساب الدرجة ==========
            results["score"] = (
                len(results["variables"]) * 2 +
                len(results["hacking_values"]) * 3 +
                len(results["direct_binary_values"]) * 5 +
                len(results["hidden_numeric_values"].get("potential_floats_32", [])) * 4 +
                len(results["encrypted_values"]) * 8 +
                len(results["crypto_analysis"]["detected_constants"]) * 10 +
                len(results["aob_patterns"]) * 5
            )

            app_logger.info(f"Analysis complete: {len(results['variables'])} variables, {len(results['direct_binary_values'])} direct values")

        except Exception as e:
            app_logger.error(f"Analysis failed: {e}")
            results["error"] = str(e)

        return results

    @staticmethod
    def _scan_directory(directory_path: str) -> Dict:
        """مسح جميع الملفات في مجلد معين والبحث عن القيم التعديلية"""
        results = {
            "file_path": directory_path,
            "size": 0,
            "entropy": 0.0,
            "strings": [],
            "variables": {},
            "hacking_values": {},
            "direct_binary_values": [],
            "hidden_numeric_values": {},
            "crypto_analysis": {
                "detected_constants": [],
                "high_entropy_blocks": [],
                "potential_keys_or_tokens": []
            },
            "is_encrypted": False,
            "is_compressed": False,
            "file_type": "مجلد",
            "file_format": "Directory",
            "sections": [],
            "imports": [],
            "exports": [],
            "hash_md5": "",
            "hash_sha256": "",
            "pe_info": {},
            "elf_info": {},
            "apk_info": {},
            "ipa_info": {},
            "decrypted_data": b'',
            "auto_hex_patches": [],
            "auto_memory_mods": [],
            "auto_asm_scripts": [],
            "found_values": {},
            "score": 0,
            "game_engine": "غير معروف",
            "detected_mods": [],
            "all_strings_found": 0,
            "analysis_depth": "directory_scan",
            "error": None,
            "assembly_analysis": [],
            "aob_patterns": [],
            "anti_debug_detected": [],
            "obfuscation_detected": False,
            "protection_type": "None",
            "files_scanned": 0,
            "files_analyzed": []
        }

        all_strings = []
        all_variables = {}
        all_hacking = {}
        all_direct_values = []
        file_count = 0

        app_logger.info(f"Scanning directory: {directory_path}")

        target_extensions = [
            '.apk', '.apks', '.apkx', '.xapk', '.ipa', '.obb', '.dex', '.so',
            '.exe', '.dll', '.rpyc', '.rpy', '.unity3d', '.unity', '.zip', '.jar',
            '.dat', '.bin', '.db', '.json', '.xml', '.txt', '.cfg', '.ini',
            '.game', '.save', '.profile', '.user', '.config'
        ]

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()

                try:
                    if os.path.getsize(file_path) > 100 * 1024 * 1024:
                        continue
                except:
                    continue

                if ext in target_extensions or any(key in file.lower() for key in ['save', 'data', 'game', 'profile', 'user']):
                    app_logger.info(f"Scanning file: {file}")
                    try:
                        data = FileSystem.read_binary(file_path)
                        if not data:
                            continue

                        file_count += 1
                        results["files_analyzed"].append(file_path)

                        strings = AnalysisEngine._extract_strings(data)
                        all_strings.extend(strings)

                        vars_found = AnalysisEngine._search_variables_smart(strings)
                        for k, v in vars_found.items():
                            if k not in all_variables:
                                all_variables[k] = []
                            all_variables[k].extend(v)

                        hacking = AnalysisEngine._search_hacking_values(strings)
                        for k, v in hacking.items():
                            if k not in all_hacking:
                                all_hacking[k] = []
                            all_hacking[k].extend(v)

                        direct_vals = AnalysisEngine._search_direct_binary_values(data)
                        all_direct_values.extend(direct_vals)

                        app_logger.info(f"  Found {len(vars_found)} variables, {len(hacking)} hacking values, {len(direct_vals)} direct values")

                    except Exception as e:
                        app_logger.warning(f"Error scanning {file}: {e}")

        results["files_scanned"] = file_count
        results["strings"] = list(set(all_strings))[:3000]
        results["all_strings_found"] = len(all_strings)
        results["variables"] = {k: list(set(v)) for k, v in all_variables.items()}
        results["hacking_values"] = {k: list(set(v)) for k, v in all_hacking.items()}
        results["direct_binary_values"] = all_direct_values

        results["detected_mods"] = AnalysisEngine._detect_available_mods(results["variables"])
        results["game_engine"] = AnalysisEngine._detect_game_engine(all_strings, directory_path)

        results["score"] = len(results["variables"]) * 2 + len(results["hacking_values"]) * 3 + len(results["direct_binary_values"]) * 5

        app_logger.info(f"Directory scan complete: {file_count} files, {len(results['variables'])} variables")

        return results

    # ===================================================================
    # دوال البحث المتقدم
    # ===================================================================

    @staticmethod
    def _search_direct_binary_values(data: bytes) -> List[Dict]:
        """البحث المباشر عن القيم التعديلية في البايتات"""
        results = []

        for name, values in AnalysisEngine.TARGET_VALUES.items():
            for val in values:
                if isinstance(val, int):
                    # 4 Bytes
                    packed = struct.pack('<I', val)
                    offset = data.find(packed)
                    if offset != -1:
                        results.append({
                            "name": name,
                            "value": val,
                            "offset": hex(offset),
                            "type": "int_4bytes",
                            "hex": packed.hex()
                        })
                    # 2 Bytes
                    packed_2 = struct.pack('<H', val)
                    offset_2 = data.find(packed_2)
                    if offset_2 != -1:
                        results.append({
                            "name": name,
                            "value": val,
                            "offset": hex(offset_2),
                            "type": "int_2bytes",
                            "hex": packed_2.hex()
                        })
                elif isinstance(val, float):
                    # Float
                    packed = struct.pack('<f', val)
                    offset = data.find(packed)
                    if offset != -1:
                        results.append({
                            "name": name,
                            "value": val,
                            "offset": hex(offset),
                            "type": "float",
                            "hex": packed.hex()
                        })
                    # Double
                    packed_d = struct.pack('<d', val)
                    offset_d = data.find(packed_d)
                    if offset_d != -1:
                        results.append({
                            "name": name,
                            "value": val,
                            "offset": hex(offset_d),
                            "type": "double",
                            "hex": packed_d.hex()
                        })

        results.extend(AnalysisEngine._search_suspicious_patterns(data))

        return results

    @staticmethod
    def _search_encrypted_values(data: bytes) -> List[Dict]:
        """البحث عن القيم المشفرة (مثل: value * 8 + 1)"""
        results = []
        for i in range(0, len(data) - 4, 4):
            value = struct.unpack('<I', data[i:i+4])[0]
            if value % 8 == 1:
                decrypted = (value - 1) // 8
                if decrypted in [100, 1000, 9999, 99999, 999999]:
                    results.append({
                        "offset": hex(i),
                        "encrypted": value,
                        "decrypted": decrypted,
                        "formula": "value * 8 + 1",
                        "type": "encrypted_value"
                    })
            # XOR
            decrypted_xor = value ^ 0xAA
            if decrypted_xor in [100, 1000, 9999, 99999, 999999]:
                results.append({
                    "offset": hex(i),
                    "encrypted": value,
                    "decrypted": decrypted_xor,
                    "formula": "value XOR 0xAA",
                    "type": "encrypted_value"
                })
        return results

    @staticmethod
    def _search_suspicious_patterns(data: bytes) -> List[Dict]:
        """البحث عن أنماط القيم المشبوهة"""
        results = []
        patterns = [
            (b'\x00\x00\x80\x3F', 1.0, "float_1.0"),
            (b'\x00\x00\x00\x00', 0, "int_zero"),
            (b'\xFF\xFF\x7F\x47', 9999.0, "float_9999"),
            (b'\xFF\xFF\xC3\x47', 99999.0, "float_99999"),
            (b'\x7F\x96\x98\x47', 999999.0, "float_999999"),
            (b'\x00\x00\x00\x40', 2.0, "float_2.0"),
            (b'\x00\x00\x00\x00\x00\x00\x00\x00', 0, "double_zero"),
            (b'\x00\x00\x00\x00\x00\x00\x49\x40', 999999.0, "double_999999"),
        ]
        for pattern, value, name in patterns:
            offset = data.find(pattern)
            if offset != -1:
                results.append({
                    "offset": hex(offset),
                    "value": value,
                    "pattern": pattern.hex(),
                    "name": name,
                    "type": "suspicious_pattern"
                })
        return results

    @staticmethod
    def _search_pointer_patterns(data: bytes) -> List[Dict]:
        """البحث عن أنماط المؤشرات الثابتة"""
        results = []
        pointer_patterns = [
            (b'\x00\x00\x00\x00\x00\x00\x00\x00', "null_pointer"),
            (b'\x01\x00\x00\x00\x00\x00\x00\x00', "small_pointer"),
            (b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', "invalid_pointer"),
        ]
        for pattern, name in pointer_patterns:
            offset = data.find(pattern)
            if offset != -1:
                results.append({
                    "offset": hex(offset),
                    "pattern": pattern.hex(),
                    "name": name,
                    "type": "pointer_pattern"
                })
        return results

    # ===================================================================
    # تحليل Android Bundle (APK / APKS)
    # ===================================================================

    @staticmethod
    def _analyze_android_bundle(file_path: str) -> Dict:
        """تحليل APK أو APKS مع فك ضغط كامل واستخراج النصوص من جميع المصادر"""
        result = {"apk_info": {}, "strings": [], "files_analyzed": []}
        all_strings = []
        temp_dir = None

        try:
            temp_dir = tempfile.mkdtemp(prefix="prook_android_")
            app_logger.info(f"Extracting Android bundle to: {temp_dir}")

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                app_logger.info(f"Extracted {len(zip_ref.namelist())} files")

            apk_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.apk'):
                        apk_files.append(os.path.join(root, file))

            # إذا لم نجد APK، قد يكون الملف نفسه APK
            if not apk_files:
                try:
                    if HAS_ANDROGUARD:
                        apk = APK(file_path)
                        result["apk_info"]["package_name"] = apk.get_package()
                        result["apk_info"]["version_name"] = apk.get_androidversion_name()
                        result["apk_info"]["version_code"] = apk.get_androidversion_code()
                        result["apk_info"]["permissions"] = apk.get_permissions()
                        result["apk_info"]["main_activity"] = apk.get_main_activity()
                        strings = apk.get_strings()
                        all_strings.extend(strings)
                        app_logger.info(f"Analyzed APK directly: {apk.get_package()}")
                        result["files_analyzed"].append(file_path)
                except Exception as e:
                    app_logger.warning(f"Direct APK analysis failed: {e}")

                manual_strings = AnalysisEngine._extract_strings_from_zip(FileSystem.read_binary(file_path))
                all_strings.extend(manual_strings)

            else:
                app_logger.info(f"Found {len(apk_files)} APK files inside bundle")
                for idx, apk_path in enumerate(apk_files):
                    try:
                        app_logger.info(f"Analyzing APK {idx+1}: {os.path.basename(apk_path)}")
                        result["files_analyzed"].append(apk_path)

                        if HAS_ANDROGUARD:
                            apk = APK(apk_path)
                            if idx == 0:
                                result["apk_info"]["package_name"] = apk.get_package()
                                result["apk_info"]["version_name"] = apk.get_androidversion_name()
                                result["apk_info"]["version_code"] = apk.get_androidversion_code()
                                result["apk_info"]["permissions"] = apk.get_permissions()
                                result["apk_info"]["main_activity"] = apk.get_main_activity()
                                app_logger.info(f"Main APK: {apk.get_package()} v{apk.get_androidversion_name()}")

                            strings = apk.get_strings()
                            all_strings.extend(strings)
                            all_strings.append(f"package:{apk.get_package()}")

                            try:
                                for dex in apk.get_dex():
                                    dex_data = dex.get_data()
                                    dex_strings = AnalysisEngine._extract_strings(dex_data)
                                    all_strings.extend(dex_strings)
                                    for pattern in AnalysisEngine.STRING_PATTERNS:
                                        matches = re.findall(pattern, dex_data)
                                        for m in matches:
                                            if isinstance(m, bytes):
                                                try:
                                                    all_strings.append(m.decode('utf-8', errors='ignore'))
                                                except:
                                                    pass
                                            else:
                                                all_strings.append(str(m))
                            except:
                                pass
                        else:
                            with zipfile.ZipFile(apk_path, 'r') as apk_zip:
                                for name in apk_zip.namelist():
                                    if name.endswith(('.dex', '.xml', '.json', '.txt', '.properties', '.smali')):
                                        try:
                                            content = apk_zip.read(name)
                                            strings = AnalysisEngine._extract_strings(content)
                                            all_strings.extend(strings)
                                            for pattern in AnalysisEngine.STRING_PATTERNS:
                                                matches = re.findall(pattern, content)
                                                for m in matches:
                                                    if isinstance(m, bytes):
                                                        try:
                                                            all_strings.append(m.decode('utf-8', errors='ignore'))
                                                        except:
                                                            pass
                                                    else:
                                                        all_strings.append(str(m))
                                        except:
                                            pass
                    except Exception as e:
                        app_logger.warning(f"Failed to analyze APK {apk_path}: {e}")

            # استخراج النصوص من الملفات الأخرى
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.xml', '.json', '.txt', '.properties', '.smali')):
                        file_path_full = os.path.join(root, file)
                        try:
                            result["files_analyzed"].append(file_path_full)
                            with open(file_path_full, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                strings = re.findall(r'"[^"]{4,}"', content)
                                all_strings.extend([s.strip('"') for s in strings if len(s) > 4])
                                keywords = re.findall(
                                    r'\b(health|hp|gold|money|coins|gems|ammo|xp|level|shield|energy|mana|purchase|reward|ad|iap|godmode|speed|jump|gravity)\b',
                                    content, re.IGNORECASE
                                )
                                all_strings.extend(keywords)
                        except:
                            pass

        except zipfile.BadZipFile:
            app_logger.error("Not a valid ZIP/APK/APKS file")
        except Exception as e:
            app_logger.error(f"Android bundle analysis error: {e}")
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

        result["strings"] = list(set(all_strings))
        return result

    # ===================================================================
    # دوال مساعدة أخرى
    # ===================================================================

    @staticmethod
    def _extract_strings_from_zip(data: bytes) -> List[str]:
        """استخراج النصوص من ملف ZIP"""
        all_strings = []
        try:
            with zipfile.ZipFile(io.BytesIO(data), 'r') as zip_ref:
                for name in zip_ref.namelist():
                    if name.endswith(('.dex', '.xml', '.json', '.txt', '.properties', '.smali', '.cs', '.js')):
                        try:
                            content = zip_ref.read(name)
                            strings = AnalysisEngine._extract_strings(content)
                            all_strings.extend(strings)
                            for pattern in AnalysisEngine.STRING_PATTERNS:
                                matches = re.findall(pattern, content)
                                for m in matches:
                                    if isinstance(m, bytes):
                                        try:
                                            all_strings.append(m.decode('utf-8', errors='ignore'))
                                        except:
                                            pass
                                    else:
                                        all_strings.append(str(m))
                        except:
                            pass
        except:
            pass
        return list(set(all_strings))

    @staticmethod
    def _extract_strings(data: bytes, min_len: int = 4) -> List[str]:
        if not data:
            return []
        strings = []
        current = ""
        for b in data:
            if 32 <= b <= 126:
                current += chr(b)
            else:
                if len(current) >= min_len:
                    strings.append(current)
                current = ""
        if len(current) >= min_len:
            strings.append(current)
        try:
            wide_pattern = re.compile(rb'(?:[\x20-\x7E]\x00){' + str(min_len).encode() + rb',}')
            for match in wide_pattern.finditer(data):
                try:
                    decoded = match.group(0).decode('utf-16-le', errors='ignore')
                    if decoded:
                        strings.append(decoded)
                except:
                    pass
        except:
            pass
        return list(set(strings))

    @staticmethod
    def _search_variables_smart(strings: List[str]) -> Dict[str, List[str]]:
        variables = {}
        all_terms = set()
        for var in AnalysisEngine.COMMON_VARIABLES:
            all_terms.add(var)
            for p in AnalysisEngine.PREFIXES:
                all_terms.add(p + var)
            for s in AnalysisEngine.SUFFIXES:
                all_terms.add(var + s)
        for s in strings:
            if not s:
                continue
            s_lower = s.lower()
            for term in all_terms:
                if term in s_lower:
                    if term not in variables:
                        variables[term] = []
                    match = re.search(rf'{re.escape(term)}[^\d]*(\d+\.?\d*)', s_lower)
                    if match:
                        variables[term].append(match.group(1))
                    else:
                        variables[term].append("found")
        return {k: v for k, v in variables.items() if v}

    @staticmethod
    def _search_hacking_values(strings: List[str]) -> Dict[str, List[str]]:
        hacking = {}
        patterns = [
            (r'gold[^\d]*(\d+)', 'gold'),
            (r'money[^\d]*(\d+)', 'money'),
            (r'health[^\d]*(\d+)', 'health'),
            (r'hp[^\d]*(\d+)', 'hp'),
            (r'ammo[^\d]*(\d+)', 'ammo'),
            (r'level[^\d]*(\d+)', 'level'),
            (r'xp[^\d]*(\d+)', 'xp'),
            (r'purchase[^\d]*(\d+)', 'purchase'),
            (r'reward[^\d]*(\d+)', 'reward'),
            (r'ad[^\d]*(\d+)', 'ad'),
        ]
        for s in strings:
            if not s:
                continue
            s_lower = s.lower()
            for pattern, name in patterns:
                match = re.search(pattern, s_lower)
                if match:
                    if name not in hacking:
                        hacking[name] = []
                    hacking[name].append(match.group(1))
        return {k: v for k, v in hacking.items() if v}

    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        freq = [0] * 256
        for b in data:
            freq[b] += 1
        entropy = 0.0
        total = len(data)
        for count in freq:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _detect_format_and_type(data: bytes, file_path: str) -> Tuple[str, str]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.apk':
            return "APK", "Android Application"
        elif ext == '.apks':
            return "APKS", "Android App Bundle"
        elif ext == '.apkx':
            return "APKX", "Android App Bundle X"
        elif ext == '.xapk':
            return "XAPK", "Android App Bundle"
        elif ext == '.ipa':
            return "IPA", "iOS Application"
        elif ext == '.obb':
            return "OBB", "Android OBB"
        elif ext == '.dex':
            return "DEX", "Android DEX"
        elif ext == '.so':
            return "SO", "Shared Library"
        elif ext == '.exe' or ext == '.dll':
            return "PE", "Windows Executable"
        elif ext == '.rpyc' or ext == '.rpy':
            return "Ren'Py", "Ren'Py Script"
        elif ext == '.unity3d' or ext == '.unity':
            return "Unity", "Unity Asset"
        elif ext == '.zip' or ext == '.jar':
            return "ZIP", "ZIP Archive"
        if data[:2] == b'MZ':
            return "PE", "Windows Executable"
        elif data[:4] == b'\x7fELF':
            return "ELF", "Linux Executable"
        elif data[:8] == b'\x50\x4B\x03\x04':
            if b'AndroidManifest.xml' in data[:5000]:
                return "APK", "Android Application"
            return "ZIP", "ZIP Archive"
        elif data[:6] == b'\x1F\x8B\x08':
            return "GZIP", "GZIP Archive"
        return "Binary", "Generic Binary"

    # ===================================================================
    # دوال تحليل إضافية (PE, ELF, Ren'Py, Unity, IPA)
    # ===================================================================

    @staticmethod
    def _analyze_ipa(file_path: str) -> Dict:
        result = {"ipa_info": {}, "strings": []}
        all_strings = []
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix="prook_ipa_")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == 'Info.plist':
                        plist_path = os.path.join(root, file)
                        try:
                            with open(plist_path, 'rb') as f:
                                plist_data = plistlib.load(f)
                                result["ipa_info"]["bundle_id"] = plist_data.get('CFBundleIdentifier', '')
                                result["ipa_info"]["version"] = plist_data.get('CFBundleVersion', '')
                                result["ipa_info"]["name"] = plist_data.get('CFBundleName', '')
                        except:
                            pass
                    if file.endswith(('.app', '.framework', '.dylib')):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                strings = re.findall(r'"[^"]{4,}"', content)
                                all_strings.extend([s.strip('"') for s in strings if len(s) > 4])
                        except:
                            pass
        except:
            pass
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        result["strings"] = list(set(all_strings))
        return result

    @staticmethod
    def _analyze_renpy(file_path: str) -> Dict:
        result = {"strings": []}
        decompiled = []
        try:
            try:
                result_sub = subprocess.run(
                    ["rpycdec", "decompile", file_path],
                    capture_output=True, text=True, timeout=30
                )
                if result_sub.returncode == 0:
                    decompiled = result_sub.stdout.splitlines()
            except:
                pass
            if not decompiled:
                data = FileSystem.read_binary(file_path)
                if data:
                    decompiled = AnalysisEngine._extract_strings(data)
        except:
            pass
        result["strings"] = decompiled[:1000]
        return result

    @staticmethod
    def _analyze_unity(data: bytes) -> Dict:
        result = {"strings": []}
        all_strings = []
        try:
            unity_types = [
                "MonoBehaviour", "GameObject", "Transform", "Component",
                "Rigidbody", "Collider", "Animator", "Canvas", "Image",
                "Text", "Button", "Slider", "AudioSource", "Camera",
                "PlayerPrefs", "Application", "SceneManager", "Time"
            ]
            extracted = AnalysisEngine._extract_strings(data)
            all_strings.extend(extracted)
            for utype in unity_types:
                if utype in all_strings:
                    all_strings.append(f"Unity_{utype}")
        except:
            pass
        result["strings"] = list(set(all_strings))[:500]
        return result

    @staticmethod
    def _analyze_pe(data: bytes) -> Dict:
        result = {"sections": [], "imports": [], "exports": []}
        if not HAS_PEFILE:
            return result
        try:
            pe = pefile.PE(data=io.BytesIO(data))
            for section in pe.sections:
                result["sections"].append({
                    "name": section.Name.decode('utf-8', errors='ignore').strip('\x00'),
                    "virtual_address": hex(section.VirtualAddress),
                    "virtual_size": hex(section.Misc_VirtualSize)
                })
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode('utf-8', errors='ignore')
                    for imp in entry.imports:
                        result["imports"].append({
                            "dll": dll_name,
                            "name": imp.name.decode('utf-8', errors='ignore') if imp.name else f"ordinal_{imp.ordinal}"
                        })
            pe.close()
        except:
            pass
        return result

    @staticmethod
    def _analyze_elf(data: bytes) -> Dict:
        result = {"sections": [], "entry_point": ""}
        if not HAS_ELF:
            return result
        try:
            elf = ELFFile(io.BytesIO(data))
            result["entry_point"] = hex(elf.header.e_entry)
            for section in elf.iter_sections():
                result["sections"].append({
                    "name": section.name,
                    "type": section.header.sh_type,
                    "size": section.header.sh_size
                })
        except:
            pass
        return result

    @staticmethod
    def _analyze_assembly_features(data: bytes, file_format: str) -> List[Dict]:
        asm_features = []
        if not HAS_CAPSTONE or not data:
            return asm_features
        try:
            arch = capstone.CS_ARCH_X86
            mode = capstone.CS_MODE_64
            if file_format == "PE":
                if b'PE\x00\x00\x4c\x01' in data[:1024]:
                    mode = capstone.CS_MODE_32
            elif file_format in ["APK", "ELF", "SO"]:
                arch = capstone.CS_ARCH_ARM
                if b'ARM64' in data[:2000] or b'AARCH64' in data[:2000]:
                    mode = capstone.CS_MODE_ARM64
                else:
                    mode = capstone.CS_MODE_ARM
            md = capstone.Cs(arch, mode)
            md.detail = True
            code_chunk = data[:60000]
            for insn in md.disasm(code_chunk, 0x1000):
                if insn.mnemonic in ['cmp', 'mov', 'add', 'sub', 'xor', 'push', 'pop']:
                    asm_features.append({
                        "address": hex(insn.address),
                        "mnemonic": insn.mnemonic,
                        "op_str": insn.op_str,
                        "comment": "تعليمات برمجية حساسة"
                    })
                if len(asm_features) >= 100:
                    break
        except:
            pass
        return asm_features

    # ===================================================================
    # دوال الكشف عن الحماية
    # ===================================================================

    @staticmethod
    def _detect_crypto_constants(data: bytes) -> List[Dict]:
        findings = []
        constants = {
            "AES S-Box": b"\x63\x7c\x77\x7b\xf2\x6b\x6f\xc5\x30\x01\x67\x2b\xfe\xd7\xab\x76",
            "ChaCha20 Constant": b"expand 32-byte k",
            "RC4 S-Box": b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
            "XOR Key Pattern": b"\xAA\x55\xAA\x55",
            "Base64 Table": b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        }
        for name, const in constants.items():
            offset = data.find(const)
            if offset != -1:
                findings.append({
                    "algorithm": name,
                    "offset": hex(offset),
                    "type": "Crypto Constant",
                    "description": f"تم العثور على {name}"
                })
        for i in range(0, len(data) - 16, 16):
            block = data[i:i+16]
            if AnalysisEngine._calculate_entropy(block) > 6.0:
                findings.append({
                    "algorithm": "Possible Encryption Key",
                    "offset": hex(i),
                    "type": "Potential Key",
                    "value": block.hex()[:32] + "...",
                    "entropy": round(AnalysisEngine._calculate_entropy(block), 2)
                })
                if len(findings) > 10:
                    break
        return findings

    @staticmethod
    def _analyze_high_entropy_blocks(data: bytes, block_size: int = 1024) -> List[Dict]:
        blocks = []
        total_len = len(data)
        step = max(block_size, total_len // 500)
        for offset in range(0, total_len, step):
            block = data[offset:offset+block_size]
            if len(block) < 128:
                continue
            entropy = AnalysisEngine._calculate_entropy(block)
            if entropy > 7.92:
                blocks.append({
                    "offset": hex(offset),
                    "entropy": round(entropy, 4),
                    "state": "Highly Encrypted / Compressed Asset Payload"
                })
                if len(blocks) >= 20:
                    break
        return blocks

    @staticmethod
    def _extract_crypto_strings_and_base64(strings: List[str]) -> List[Dict]:
        tokens = []
        crypto_keywords = {"key", "cipher", "secret", "aes", "decrypt", "encrypt", "iv", "salt", "token", "password"}
        base64_regex = re.compile(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')
        for s in strings:
            s_clean = s.strip()
            if len(s_clean) > 16:
                if base64_regex.match(s_clean):
                    try:
                        decoded = base64.b64decode(s_clean[:40], validate=True)
                        if len(decoded) > 4:
                            tokens.append({
                                "type": "Base64 Encrypted String/Key Block",
                                "value": s_clean[:50] + "...",
                                "raw_hint": decoded.hex()[:16]
                            })
                    except:
                        pass
                s_lower = s_clean.lower()
                for kw in crypto_keywords:
                    if kw in s_lower and any(char.isdigit() for char in s_lower):
                        tokens.append({
                            "type": f"Potential Crypto Identifier ({kw})",
                            "value": s_clean[:60]
                        })
                        break
        return tokens[:30]

    @staticmethod
    def _detect_anti_debug(data: bytes, strings: List[str]) -> List[Dict]:
        anti = []
        patterns = {
            "IsDebuggerPresent": rb'\x64\xa1\x30\x00\x00\x00',
            "CheckRemoteDebuggerPresent": rb'\xe8........\x85\xc0\x74\x0c',
            "NtQueryInformationProcess": rb'\xb8\x19\x00\x00\x00',
            "TLS Callback": rb'\x2e\x74\x65\x78\x74\x24\x24',
            "PEB BeingDebugged": rb'\x64\x8b\x18\x8b\x43\x30',
        }
        for name, pattern in patterns.items():
            if re.search(pattern, data):
                anti.append({"name": name, "description": f"كشف تقنية {name}", "confidence": "High"})
        keywords = ["debug", "attach", "trace", "breakpoint", "anti-tamper"]
        for s in strings:
            s_lower = s.lower()
            for kw in keywords:
                if kw in s_lower:
                    anti.append({"name": kw.capitalize(), "description": f"كلمة مفتاحية: {kw}", "confidence": "Low"})
        return anti

    @staticmethod
    def _detect_obfuscation(data: bytes) -> bool:
        indicators = [rb'\x90\x90\x90\x90', rb'\xeb\xfe', b'Microsoft.Obfuscation', b'ConfuserEx', b'Dotfuscator']
        for ind in indicators:
            if ind in data:
                return True
        if data.count(b'\x90') > 50:
            return True
        return False

    @staticmethod
    def _detect_protection(data: bytes, strings: List[str]) -> str:
        protections = {
            "Themida": [b'Themida', b'ThemidaAPI'],
            "VMProtect": [b'VMProtect', b'VMP'],
            "Enigma": [b'Enigma', b'EnigmaAPI'],
            "ProGuard": [b'ProGuard', b'proguard'],
            "Unity Protection": [b'UnityEngine', b'Il2Cpp'],
            "XOR Encryption": [b'XOR', b'xor_key'],
            "AES Encryption": [b'AES', b'Rijndael'],
        }
        for name, sigs in protections.items():
            for sig in sigs:
                if sig in data:
                    return name
                for s in strings:
                    if sig.lower() in s.lower():
                        return name
        entropy = AnalysisEngine._calculate_entropy(data[:10000])
        if entropy > 7.8:
            return "Heavy Encryption"
        elif entropy > 7.0:
            return "Compressed/Packed"
        return "None"

    @staticmethod
    def _find_aob_patterns(data: bytes) -> List[Dict]:
        patterns = []
        common = [
            (rb'\x74\x0C', "JE to JMP"),
            (rb'\x75\x0C', "JNE to JMP"),
            (rb'\x0F\x84', "JE Long to JNE Long"),
            (rb'\x0F\x85', "JNE Long to JE Long"),
            (rb'\xE8', "CALL to NOP"),
            (rb'\xE9', "JMP to NOP"),
            (rb'\x83\xF8\x00', "CMP EAX, 0"),
            (rb'\x85\xC0', "TEST EAX, EAX"),
        ]
        for pattern, desc in common:
            offsets = []
            off = 0
            while True:
                off = data.find(pattern, off)
                if off == -1:
                    break
                offsets.append(off)
                off += len(pattern)
                if len(offsets) > 3:
                    break
            if offsets:
                patterns.append({
                    "pattern": pattern.hex(),
                    "description": desc,
                    "offsets": [hex(o) for o in offsets],
                    "count": len(offsets)
                })
        return patterns

    @staticmethod
    def _find_hex_patches(data: bytes) -> List[Dict]:
        patches = []
        patterns = [
            (b'\x74\x0C', b'\xEB\x0C'),
            (b'\x75\x0C', b'\xEB\x0C'),
            (b'\x0F\x84', b'\x0F\x85'),
            (b'\x0F\x85', b'\x0F\x84'),
            (b'\xE8', b'\x90\x90'),
            (b'\xE9', b'\x90\x90\x90\x90\x90'),
        ]
        for old, new in patterns:
            offset = data.find(old)
            if offset != -1:
                patches.append({"offset": offset, "old": old.hex(), "new": new.hex()})
        return patches

    @staticmethod
    def _find_memory_mods(strings: List[str]) -> List[Dict]:
        mods = []
        for s in strings:
            s_lower = s.lower()
            if 'gold' in s_lower or 'money' in s_lower:
                mods.append({"type": "money", "value": "999999", "found": True})
            elif 'health' in s_lower or 'hp' in s_lower:
                mods.append({"type": "health", "value": "9999", "found": True})
            elif 'ammo' in s_lower:
                mods.append({"type": "ammo", "value": "999", "found": True})
            elif 'purchase' in s_lower or 'buy' in s_lower:
                mods.append({"type": "purchase", "value": "0", "found": True})
            elif 'reward' in s_lower or 'ad' in s_lower:
                mods.append({"type": "reward", "value": "1", "found": True})
            elif 'level' in s_lower or 'xp' in s_lower:
                mods.append({"type": "experience", "value": "99999", "found": True})
            elif 'speed' in s_lower:
                mods.append({"type": "speed", "value": "50.0", "found": True})
        return mods

    @staticmethod
    def _detect_game_engine(strings: List[str], file_path: str) -> str:
        all_text = ' '.join(strings).lower()
        if 'unity' in all_text or 'mono' in all_text:
            return "Unity"
        elif 'renpy' in all_text or 'rpy' in all_text:
            return "Ren'Py"
        elif 'unreal' in all_text:
            return "Unreal Engine"
        elif 'godot' in all_text:
            return "Godot"
        elif 'cocos' in all_text:
            return "Cocos"
        else:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.apk', '.apks', '.apkx', '.xapk']:
                return "Android (Generic)"
            elif ext in ['.ipa']:
                return "iOS (Generic)"
            return "Unknown"

    @staticmethod
    def _detect_available_mods(variables: Dict) -> List[str]:
        mods = []
        var_names = ' '.join(variables.keys()).lower()
        if 'godmode' in var_names or 'god' in var_names:
            mods.append("God Mode")
        if 'gold' in var_names or 'money' in var_names:
            mods.append("Infinite Money")
        if 'health' in var_names or 'hp' in var_names:
            mods.append("Infinite Health")
        if 'ammo' in var_names:
            mods.append("Infinite Ammo")
        if 'shield' in var_names or 'armor' in var_names:
            mods.append("Infinite Shield")
        if 'energy' in var_names or 'mana' in var_names:
            mods.append("Infinite Energy")
        if 'level' in var_names or 'xp' in var_names:
            mods.append("Max Level")
        if 'speed' in var_names:
            mods.append("Super Speed")
        if 'purchase' in var_names:
            mods.append("Free Purchases")
        if 'reward' in var_names or 'ad' in var_names:
            mods.append("Ad Rewards Bypass")
        if 'damage' in var_names or 'attack' in var_names:
            mods.append("One Hit Kill")
        return mods