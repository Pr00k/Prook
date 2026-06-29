"""
محرك التصحيح السداسي - دعم Platinmods-MemoryPatch و KittyMemory
"""

import os
import struct
import tempfile
import subprocess
from typing import List, Dict, Optional, Tuple
from infrastructure.logger import app_logger
from infrastructure.file_system import FileSystem


class MemoryPatcher:
    """محرك التصحيح السداسي المتقدم"""

    @staticmethod
    def generate_platinmods_patch(library: str, offset: str, new_bytes: str) -> str:
        return """
#include "Platinmods/PlatinmodsMemoryPatch.h"

void apply_platinmods_patch() {{
    pid_t pid = Platinmods::getPid("com.example.game");
    Platinmods::MemoryPatch patch = Platinmods::MemoryPatch(
        pid, 
        "{library}", 
        "{offset}", 
        "{new_bytes}"
    );
    if (patch.Modify()) {{
        printf("Patch applied successfully!\\n");
    }} else {{
        printf("Patch failed!\\n");
    }}
}}
""".format(library=library, offset=offset, new_bytes=new_bytes)

    @staticmethod
    def generate_kittymemory_patch(library: str, offset: int, new_bytes: str) -> str:
        return """
#include "KittyMemory/KittyMemory.h"

void apply_kittymemory_patch() {{
    uintptr_t addr = KittyMemory::getAbsoluteAddress("{library}", {offset});
    KittyMemory::writeHex(addr, "{new_bytes}");
    printf("Patch applied at %p\\n", (void*)addr);
}}
""".format(library=library, offset=hex(offset), new_bytes=new_bytes)

    @staticmethod
    def find_pattern_in_library(library_path: str, pattern: str) -> List[int]:
        offsets = []
        try:
            data = FileSystem.read_binary(library_path)
            if not data:
                return offsets
            
            pattern_bytes = bytes.fromhex(pattern.replace(' ', ''))
            
            offset = 0
            while True:
                offset = data.find(pattern_bytes, offset)
                if offset == -1:
                    break
                offsets.append(offset)
                offset += len(pattern_bytes)
                
        except Exception as e:
            app_logger.error("Error finding pattern: {0}".format(e))
        
        return offsets

    @staticmethod
    def patch_library(library_path: str, offset: int, new_bytes: bytes) -> bool:
        try:
            data = FileSystem.read_binary(library_path)
            if not data:
                return False
            
            if offset + len(new_bytes) > len(data):
                app_logger.error("Offset {0} out of range".format(offset))
                return False
            
            patched_data = data[:offset] + new_bytes + data[offset + len(new_bytes):]
            
            return FileSystem.write_binary(library_path, patched_data)
            
        except Exception as e:
            app_logger.error("Error patching library: {0}".format(e))
            return False

    @staticmethod
    def create_hex_patch_script(patches: List[Dict]) -> str:
        lines = [
            '#include <cstdint>',
            '#include <cstdio>',
            '#include <unistd.h>',
            '#include "KittyMemory/KittyMemory.h"',
            '#include "Platinmods/PlatinmodsMemoryPatch.h"',
            '',
            'void apply_all_patches() {',
            '    printf("[*] Starting patches...\\n");',
            ''
        ]

        for idx, patch in enumerate(patches):
            library = patch.get("library", "libil2cpp.so")
            offset = patch.get("offset", "0x0")
            new_bytes = patch.get("new_bytes", "")
            description = patch.get("description", "Unknown patch")
            
            var_name = "addr_{0}".format(idx)
            
            lines.append('    // {0}'.format(description))
            lines.append('    uintptr_t {0} = KittyMemory::getAbsoluteAddress("{1}", {2});'.format(var_name, library, offset))
            lines.append('    if ({0}) {{'.format(var_name))
            lines.append('        KittyMemory::writeHex({0}, "{1}");'.format(var_name, new_bytes))
            lines.append('        printf("[+] Applied: {0}\\n");'.format(description))
            lines.append('    } else {')
            lines.append('        printf("[-] Failed: {0}\\n");'.format(description))
            lines.append('    }')
            lines.append('')

        lines.append('    printf("[*] All patches applied!\\n");')
        lines.append('}')

        return '\n'.join(lines)