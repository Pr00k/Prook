"""
محرك تحليل الملفات المتقدم - يدعم:
- تحليل PE, ELF, APK
- فك التجميع (Disassembly)
- البحث عن القيم والمتغيرات
- فك التشفير المتقدم
- الهندسة العكسية
"""

import os
import re
import math
import struct
import hashlib
import binascii
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

# مكتبات متقدمة للتحليل
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
    HAS_ELFFILE = True
except ImportError:
    HAS_ELFFILE = False

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from infrastructure.file_system import FileSystem
from infrastructure.logger import app_logger
from infrastructure.crypto import CryptoEngine


class AnalysisEngine:
    """محرك التحليل المتقدم"""

    # ================ القائمة الشاملة لجميع المتغيرات ================
    ALL_VARIABLES = {
        # === الذهب والنقود ===
        "gold": {"name": "الذهب", "category": "money"},
        "golden": {"name": "الذهب", "category": "money"},
        "golds": {"name": "الذهب", "category": "money"},
        "money": {"name": "النقود", "category": "money"},
        "monies": {"name": "النقود", "category": "money"},
        "coins": {"name": "العملات المعدنية", "category": "money"},
        "coin": {"name": "العملة", "category": "money"},
        "cash": {"name": "النقود السائلة", "category": "money"},
        "cashing": {"name": "النقود السائلة", "category": "money"},
        "gems": {"name": "الأحجار الكريمة", "category": "money"},
        "gem": {"name": "الحجر الكريم", "category": "money"},
        "diamonds": {"name": "الماس", "category": "money"},
        "diamond": {"name": "الماسة", "category": "money"},
        "rubies": {"name": "الياقوت", "category": "money"},
        "ruby": {"name": "الياقوتة", "category": "money"},
        "emeralds": {"name": "الزمرد", "category": "money"},
        "emerald": {"name": "الزمردة", "category": "money"},
        "crystals": {"name": "البلورات", "category": "money"},
        "crystal": {"name": "البلورة", "category": "money"},
        "points": {"name": "النقاط", "category": "money"},
        "point": {"name": "النقطة", "category": "money"},
        "score": {"name": "النتيجة", "category": "money"},
        "scoring": {"name": "التسجيل", "category": "money"},
        "tokens": {"name": "الرموز", "category": "money"},
        "token": {"name": "الرمز", "category": "money"},
        "currency": {"name": "العملة", "category": "money"},
        "currencies": {"name": "العملات", "category": "money"},
        "credits": {"name": "الائتمان", "category": "money"},
        "credit": {"name": "الائتمان", "category": "money"},
        "wallet": {"name": "المحفظة", "category": "money"},
        "wallets": {"name": "المحافظ", "category": "money"},
        "bank": {"name": "البنك", "category": "money"},
        "banking": {"name": "البنك", "category": "money"},
        "budget": {"name": "الميزانية", "category": "money"},
        "funds": {"name": "الأموال", "category": "money"},
        "fund": {"name": "الصندوق", "category": "money"},
        "savings": {"name": "المدخرات", "category": "money"},
        "treasure": {"name": "الكنز", "category": "money"},
        "loot": {"name": "الغنيمة", "category": "money"},
        "bounty": {"name": "المكافأة", "category": "money"},
        "stars": {"name": "النجوم", "category": "money"},
        "star": {"name": "النجمة", "category": "money"},
        "medals": {"name": "الميداليات", "category": "money"},
        "trophies": {"name": "الكؤوس", "category": "money"},
        "dollar": {"name": "الدولار", "category": "money"},
        "rupee": {"name": "الروبية", "category": "money"},
        "yen": {"name": "الين", "category": "money"},
        "souls": {"name": "الأرواح", "category": "money"},
        "fragment": {"name": "الشظية", "category": "money"},
        "shard": {"name": "الشظية", "category": "money"},
        "piece": {"name": "القطعة", "category": "money"},
        "premiumcurrency": {"name": "العملة المميزة", "category": "money"},
        "hardcurrency": {"name": "العملة الصعبة", "category": "money"},
        "softcurrency": {"name": "العملة الناعمة", "category": "money"},
        "ingots": {"name": "السبائك", "category": "money"},
        "ores": {"name": "الخامات", "category": "money"},

        # === الصحة والحياة ===
        "health": {"name": "الصحة", "category": "health"},
        "hitpoints": {"name": "نقاط الحياة", "category": "health"},
        "hp": {"name": "نقاط الحياة", "category": "health"},
        "life": {"name": "الحياة", "category": "health"},
        "lives": {"name": "الحياة", "category": "health"},
        "vitality": {"name": "الحيوية", "category": "health"},
        "condition": {"name": "الحالة الجسدية", "category": "health"},
        "integrity": {"name": "السلامة الهيكلية", "category": "health"},
        "hull": {"name": "بدن", "category": "health"},
        "healthregen": {"name": "استعادة الصحة", "category": "health"},
        "recovery": {"name": "الشفاء", "category": "health"},
        "heal": {"name": "الشفاء", "category": "health"},
        "spirit": {"name": "الروح", "category": "health"},
        "soul": {"name": "الروح", "category": "health"},
        "heart": {"name": "القلب", "category": "health"},
        "blood": {"name": "الدم", "category": "health"},
        "maxhealth": {"name": "الحياة القصوى", "category": "health"},
        "maxhp": {"name": "الحياة القصوى", "category": "health"},
        "basehealth": {"name": "الحياة الأساسية", "category": "health"},
        "healthbar": {"name": "شريط الحياة", "category": "health"},
        "hpbar": {"name": "شريط الحياة", "category": "health"},

        # === الدرع والحماية ===
        "shield": {"name": "الدرع", "category": "shield"},
        "armor": {"name": "الدروع", "category": "shield"},
        "armour": {"name": "الدروع", "category": "shield"},
        "defense": {"name": "الدفاع", "category": "shield"},
        "defence": {"name": "الدفاع", "category": "shield"},
        "protection": {"name": "الحماية", "category": "shield"},
        "guard": {"name": "الحارس", "category": "shield"},
        "barrier": {"name": "الحاجز", "category": "shield"},
        "ward": {"name": "الحصن", "category": "shield"},
        "resistance": {"name": "المقاومة", "category": "shield"},
        "shell": {"name": "الغلاف", "category": "shield"},
        "bubble": {"name": "الفقاعة", "category": "shield"},
        "forcefield": {"name": "حقل القوة", "category": "shield"},
        "block": {"name": "الحجب", "category": "shield"},
        "mitigation": {"name": "تقليل الضرر", "category": "shield"},
        "damagereduction": {"name": "تقليل الضرر", "category": "shield"},
        "armorclass": {"name": "فئة الدرع", "category": "shield"},
        "shielddurability": {"name": "صلابة الدرع", "category": "shield"},
        "energyarmor": {"name": "درع الطاقة", "category": "shield"},

        # === الطاقة والمانا ===
        "energy": {"name": "الطاقة", "category": "energy"},
        "mana": {"name": "المانا", "category": "energy"},
        "magicpoints": {"name": "نقاط السحر", "category": "energy"},
        "mp": {"name": "نقاط السحر", "category": "energy"},
        "power": {"name": "القوة", "category": "energy"},
        "magic": {"name": "السحر", "category": "energy"},
        "fuel": {"name": "الوقود", "category": "energy"},
        "battery": {"name": "البطارية", "category": "energy"},
        "charge": {"name": "الشحن", "category": "energy"},
        "stamina": {"name": "التحمل", "category": "energy"},
        "endurance": {"name": "الجلد الجسدي", "category": "energy"},
        "rage": {"name": "الغضب", "category": "energy"},
        "fury": {"name": "الحماس", "category": "energy"},
        "chi": {"name": "تشي", "category": "energy"},
        "ki": {"name": "تشي", "category": "energy"},
        "qi": {"name": "تشي", "category": "energy"},
        "focus": {"name": "التركيز", "category": "energy"},
        "vigor": {"name": "النشاط", "category": "energy"},
        "fatigue": {"name": "الإرهاق", "category": "energy"},
        "darkenergy": {"name": "الطاقة المظلمة", "category": "energy"},
        "lightenergy": {"name": "طاقة النور", "category": "energy"},
        "battlespirit": {"name": "الروح القتالية", "category": "energy"},

        # === الذخيرة والأسلحة ===
        "ammo": {"name": "الذخيرة", "category": "ammo"},
        "bullet": {"name": "الرصاصة", "category": "ammo"},
        "magazine": {"name": "المخزن", "category": "ammo"},
        "mag": {"name": "المخزن", "category": "ammo"},
        "clip": {"name": "المشبك", "category": "ammo"},
        "shell": {"name": "القذيفة", "category": "ammo"},
        "rocket": {"name": "الصاروخ", "category": "ammo"},
        "arrow": {"name": "السهم", "category": "ammo"},
        "projectile": {"name": "المقذوف", "category": "ammo"},
        "reserveammo": {"name": "الذخيرة الاحتياطية", "category": "ammo"},
        "round": {"name": "الطلقة", "category": "ammo"},
        "missile": {"name": "الصاروخ الصغير", "category": "ammo"},
        "weapon": {"name": "السلاح", "category": "ammo"},
        "potion": {"name": "الجرعة", "category": "ammo"},
        "consumable": {"name": "المواد الاستهلاكية", "category": "ammo"},
        "grenades": {"name": "القنابل اليدوية", "category": "ammo"},
        "firearm": {"name": "العتاد الناري", "category": "ammo"},
        "meleeweapon": {"name": "العتاد البارد", "category": "ammo"},
        "apround": {"name": "الطلقات الخارقة", "category": "ammo"},
        "armorpiercing": {"name": "اختراق الدرع", "category": "ammo"},

        # === الخبرة والمستوى ===
        "experience": {"name": "الخبرة", "category": "exp"},
        "exp": {"name": "الخبرة", "category": "exp"},
        "xp": {"name": "الخبرة", "category": "exp"},
        "level": {"name": "المستوى", "category": "exp"},
        "lv": {"name": "المستوى", "category": "exp"},
        "lvl": {"name": "المستوى", "category": "exp"},
        "rank": {"name": "الرتبة", "category": "exp"},
        "rating": {"name": "التقييم", "category": "exp"},
        "tier": {"name": "الطبقة", "category": "exp"},
        "prestige": {"name": "الهيبة", "category": "exp"},
        "skillpoints": {"name": "نقاط المهارة", "category": "exp"},
        "sp": {"name": "نقاط المهارة", "category": "exp"},
        "talentpoints": {"name": "نقاط الموهبة", "category": "exp"},
        "tp": {"name": "نقاط الموهبة", "category": "exp"},
        "progress": {"name": "التقدم", "category": "exp"},
        "abilitypoint": {"name": "نقاط القدرات", "category": "exp"},
        "ap": {"name": "نقاط القدرات", "category": "exp"},
        "upgrade": {"name": "التطوير", "category": "exp"},
        "upgradepoints": {"name": "نقاط التطوير", "category": "exp"},
        "grade": {"name": "الدرجة", "category": "exp"},
        "honorpoints": {"name": "نقاط الشرف", "category": "exp"},
        "reputation": {"name": "السمعة", "category": "exp"},
        "nextlevelxp": {"name": "الخبرة المطلوبة", "category": "exp"},
        "requiredxp": {"name": "الخبرة المطلوبة", "category": "exp"},
        "xpmultiplier": {"name": "مضاعف الخبرة", "category": "exp"},

        # === المخزون ===
        "inventory": {"name": "المخزون", "category": "inventory"},
        "bag": {"name": "الحقيبة", "category": "inventory"},
        "backpack": {"name": "حقيبة الظهر", "category": "inventory"},
        "pouch": {"name": "الجراب", "category": "inventory"},
        "slot": {"name": "الفتحة", "category": "inventory"},
        "equipment": {"name": "المعدات", "category": "inventory"},
        "weight": {"name": "الوزن", "category": "inventory"},
        "capacity": {"name": "السعة", "category": "inventory"},
        "carryweight": {"name": "وزن الحمولة", "category": "inventory"},
        "stack": {"name": "الكومة", "category": "inventory"},
        "quantity": {"name": "الكمية", "category": "inventory"},
        "item": {"name": "العنصر", "category": "inventory"},
        "components": {"name": "المكونات", "category": "inventory"},
        "lootbox": {"name": "صندوق الكنز", "category": "inventory"},
        "treasurechest": {"name": "صندوق الكنز", "category": "inventory"},
        "extraslots": {"name": "الفتحات الإضافية", "category": "inventory"},

        # === السرعة والحركة ===
        "speed": {"name": "السرعة", "category": "speed"},
        "movespeed": {"name": "سرعة الحركة", "category": "speed"},
        "walkspeed": {"name": "سرعة المشي", "category": "speed"},
        "runspeed": {"name": "سرعة الركض", "category": "speed"},
        "dashspeed": {"name": "سرعة الاندفاع", "category": "speed"},
        "sprintspeed": {"name": "سرعة العدو", "category": "speed"},
        "jumppower": {"name": "قوة القفز", "category": "speed"},
        "jumpforce": {"name": "قوة القفز", "category": "speed"},
        "jumpheight": {"name": "ارتفاع القفز", "category": "speed"},
        "gravity": {"name": "الجاذبية", "category": "speed"},
        "agility": {"name": "الرشاقة", "category": "speed"},
        "dexterity": {"name": "الخفة", "category": "speed"},
        "mobility": {"name": "الحركية", "category": "speed"},
        "turnspeed": {"name": "سرعة الدوران", "category": "speed"},
        "flyspeed": {"name": "سرعة الطيران", "category": "speed"},
        "swimspeed": {"name": "سرعة السباحة", "category": "speed"},
        "acceleration": {"name": "تسارع", "category": "speed"},
        "deceleration": {"name": "تباطؤ", "category": "speed"},
        "drag": {"name": "تباطؤ", "category": "speed"},

        # === التهدئة ===
        "cooldown": {"name": "وقت التهدئة", "category": "cooldown"},
        "cd": {"name": "وقت التهدئة", "category": "cooldown"},
        "rechargetime": {"name": "وقت إعادة الشحن", "category": "cooldown"},
        "waittime": {"name": "وقت الانتظار", "category": "cooldown"},
        "delaytime": {"name": "وقت التأخير", "category": "cooldown"},
        "curcooldown": {"name": "التهدئة الحالية", "category": "cooldown"},
        "maxcooldown": {"name": "التهدئة القصوى", "category": "cooldown"},
        "skilltimer": {"name": "مؤقت المهارة", "category": "cooldown"},
        "bufftimer": {"name": "مؤقت التعزيز", "category": "cooldown"},
        "duration": {"name": "مدة التأثير", "category": "cooldown"},
        "countdowntimer": {"name": "العداد التنازلي", "category": "cooldown"},
        "respawntimer": {"name": "وقت الإنعاش", "category": "cooldown"},
        "attackspeed": {"name": "معدل الهجوم", "category": "cooldown"},
        "attackrate": {"name": "معدل الهجوم", "category": "cooldown"},
        "firerate": {"name": "معدل إطلاق النار", "category": "cooldown"},

        # === الإحداثيات ===
        "position": {"name": "الموقع", "category": "coordinates"},
        "pos": {"name": "الموقع", "category": "coordinates"},
        "x": {"name": "الإحداثي السيني", "category": "coordinates"},
        "xaxis": {"name": "الإحداثي السيني", "category": "coordinates"},
        "y": {"name": "الإحداثي الصادي", "category": "coordinates"},
        "yaxis": {"name": "الإحداثي الصادي", "category": "coordinates"},
        "z": {"name": "الإحداثي العيني", "category": "coordinates"},
        "zaxis": {"name": "الإحداثي العيني", "category": "coordinates"},
        "location": {"name": "مكان التواجد", "category": "coordinates"},
        "loc": {"name": "مكان التواجد", "category": "coordinates"},
        "spawnpoint": {"name": "نقطة التمركز", "category": "coordinates"},
        "checkpoint": {"name": "نقطة الالتقاط", "category": "coordinates"},
        "teleport": {"name": "الانتقال السريع", "category": "coordinates"},
        "tp": {"name": "الانتقال السريع", "category": "coordinates"},
        "warp": {"name": "الانتقال السريع", "category": "coordinates"},
        "distance": {"name": "المسافة", "category": "coordinates"},
        "direction": {"name": "الاتجاه", "category": "coordinates"},
        "fieldofview": {"name": "زاوية الرؤية", "category": "coordinates"},
        "fov": {"name": "زاوية الرؤية", "category": "coordinates"},
        "camerazoom": {"name": "تكبير الكاميرا", "category": "coordinates"},
        "mousesensitivity": {"name": "حساسية الفأرة", "category": "coordinates"},
        "camerarotation": {"name": "دوران الكاميرا", "category": "coordinates"},
        "pitch": {"name": "زاوية الميل", "category": "coordinates"},
        "yaw": {"name": "زاوية الانحراف", "category": "coordinates"},

        # === الحالات المنطقية (Boolean) ===
        "godmode": {"name": "وضع الإله", "category": "boolean"},
        "god": {"name": "وضع الإله", "category": "boolean"},
        "invisible": {"name": "التخفي", "category": "boolean"},
        "stealth": {"name": "التخفي", "category": "boolean"},
        "hidden": {"name": "التخفي", "category": "boolean"},
        "unlimitedenergy": {"name": "طاقة لا نهائية", "category": "boolean"},
        "infiniteenergy": {"name": "طاقة لا نهائية", "category": "boolean"},
        "unlimitedammo": {"name": "ذخيرة لا نهائية", "category": "boolean"},
        "infiniteammo": {"name": "ذخيرة لا نهائية", "category": "boolean"},
        "unlimitedhealth": {"name": "صحة لا نهائية", "category": "boolean"},
        "infinitehealth": {"name": "صحة لا نهائية", "category": "boolean"},
        "unlimitedshield": {"name": "درع لا نهائي", "category": "boolean"},
        "infiniteshield": {"name": "درع لا نهائي", "category": "boolean"},
        "freezeenemy": {"name": "تجميد العدو", "category": "boolean"},
        "freezeai": {"name": "تجميد العدو", "category": "boolean"},
        "flymode": {"name": "الطيران", "category": "boolean"},
        "flying": {"name": "الطيران", "category": "boolean"},
        "wallwalk": {"name": "المشي على الجدران", "category": "boolean"},
        "wallhack": {"name": "اختراق الجدران", "category": "boolean"},
        "noclip": {"name": "اختراق الجدران", "category": "boolean"},
        "ghostmode": {"name": "وضع الشبح", "category": "boolean"},
        "unlimitedspeed": {"name": "سرعة لا نهائية", "category": "boolean"},
        "infinitejump": {"name": "قفزة لا نهائية", "category": "boolean"},
        "immortal": {"name": "عدم الموت", "category": "boolean"},
        "invincible": {"name": "عدم الموت", "category": "boolean"},
        "nofalldamage": {"name": "عدم السقوط", "category": "boolean"},
        "unlockalllevels": {"name": "فتح كل المستويات", "category": "boolean"},
        "allweapons": {"name": "جميع الأسلحة", "category": "boolean"},
        "unlockallweapons": {"name": "جميع الأسلحة", "category": "boolean"},
        "nohunger": {"name": "لا جوع", "category": "boolean"},
        "nothirst": {"name": "لا عطش", "category": "boolean"},
        "freezetime": {"name": "تجميد الوقت", "category": "boolean"},

        # === المشاعر الإيجابية ===
        "love": {"name": "الحب", "category": "emotions"},
        "affection": {"name": "العاطفة", "category": "emotions"},
        "admiration": {"name": "الإعجاب", "category": "emotions"},
        "like": {"name": "الإعجاب", "category": "emotions"},
        "trust": {"name": "الثقة", "category": "emotions"},
        "respect": {"name": "الاحترام", "category": "emotions"},
        "loyalty": {"name": "الإخلاص", "category": "emotions"},
        "appreciation": {"name": "التقدير", "category": "emotions"},
        "gratitude": {"name": "التقدير", "category": "emotions"},
        "forgiveness": {"name": "التسامح", "category": "emotions"},
        "compassion": {"name": "الرحمة", "category": "emotions"},
        "mercy": {"name": "الرحمة", "category": "emotions"},
        "empathy": {"name": "التعاطف", "category": "emotions"},
        "intimacy": {"name": "الحميمية", "category": "emotions"},
        "friendship": {"name": "الصداقة", "category": "emotions"},
        "companionship": {"name": "الرفقة", "category": "emotions"},
        "cooperation": {"name": "التعاون", "category": "emotions"},
        "solidarity": {"name": "التضامن", "category": "emotions"},
        "harmony": {"name": "الانسجام", "category": "emotions"},
        "understanding": {"name": "التفاهم", "category": "emotions"},
        "support": {"name": "الدعم", "category": "emotions"},
        "care": {"name": "الرعاية", "category": "emotions"},
        "tenderness": {"name": "الحنان", "category": "emotions"},
        "passion": {"name": "الشغف", "category": "emotions"},
        "altruism": {"name": "الإيثار", "category": "emotions"},
        "acceptance": {"name": "القبول", "category": "emotions"},
        "encouragement": {"name": "التشجيع", "category": "emotions"},
        "joy": {"name": "الفرح", "category": "emotions"},
        "happiness": {"name": "الفرح", "category": "emotions"},
        "hope": {"name": "الأمل", "category": "emotions"},
        "inspiration": {"name": "الإلهام", "category": "emotions"},

        # === المشاعر السلبية ===
        "hate": {"name": "الكراهية", "category": "emotions"},
        "hatred": {"name": "الكراهية", "category": "emotions"},
        "contempt": {"name": "الازدراء", "category": "emotions"},
        "disdain": {"name": "الازدراء", "category": "emotions"},
        "hostility": {"name": "العداوة", "category": "emotions"},
        "enmity": {"name": "العداوة", "category": "emotions"},
        "loathing": {"name": "الكراهية الشديدة", "category": "emotions"},
        "animosity": {"name": "العداء", "category": "emotions"},
        "resentment": {"name": "الضغينة", "category": "emotions"},
        "grudge": {"name": "الضغينة", "category": "emotions"},
        "jealousy": {"name": "الغيرة", "category": "emotions"},
        "envy": {"name": "الغيرة", "category": "emotions"},
        "malice": {"name": "الحقد", "category": "emotions"},
        "spite": {"name": "الحقد", "category": "emotions"},
        "vengeance": {"name": "الانتقام", "category": "emotions"},
        "aggression": {"name": "العدوانية", "category": "emotions"},
        "cruelty": {"name": "القسوة", "category": "emotions"},
        "selfishness": {"name": "الأنانية", "category": "emotions"},
        "indifference": {"name": "اللامبالاة", "category": "emotions"},
        "apathy": {"name": "اللامبالاة", "category": "emotions"},
        "selfloathing": {"name": "كراهية الذات", "category": "emotions"},
        "distrust": {"name": "عدم الثقة", "category": "emotions"},
        "mistrust": {"name": "عدم الثقة", "category": "emotions"},
        "betrayal": {"name": "الخيانة", "category": "emotions"},
        "treachery": {"name": "الغدر", "category": "emotions"},
        "rejection": {"name": "الرفض", "category": "emotions"},
        "insult": {"name": "الإهانة", "category": "emotions"},
        "offense": {"name": "الإهانة", "category": "emotions"},
        "humiliation": {"name": "التحقير", "category": "emotions"},
        "regret": {"name": "الندم", "category": "emotions"},
        "boredom": {"name": "الملل", "category": "emotions"},
        "frustration": {"name": "الإحباط", "category": "emotions"},
        "rivalry": {"name": "التنافس", "category": "emotions"},
        "fear": {"name": "الخوف", "category": "emotions"},
        "worry": {"name": "القلق", "category": "emotions"},
        "anxiety": {"name": "القلق", "category": "emotions"},
        "sadness": {"name": "الحزن", "category": "emotions"},
        "anger": {"name": "الغضب", "category": "emotions"},
        "disgust": {"name": "الاشمئزاز", "category": "emotions"},
        "despair": {"name": "اليأس", "category": "emotions"},
        "loneliness": {"name": "الوحدة", "category": "emotions"},
        "nostalgia": {"name": "الحنين", "category": "emotions"},

        # === القوى والصفات ===
        "strength": {"name": "القوة", "category": "stats"},
        "power": {"name": "القوة", "category": "stats"},
        "charisma": {"name": "الكاريزما", "category": "stats"},
        "influence": {"name": "النفوذ", "category": "stats"},
        "authority": {"name": "السلطة", "category": "stats"},
        "charm": {"name": "الوسامة", "category": "stats"},
        "courage": {"name": "الشجاعة", "category": "stats"},
        "bravery": {"name": "الشجاعة", "category": "stats"},
        "intelligence": {"name": "الذكاء", "category": "stats"},
        "intellect": {"name": "الذكاء", "category": "stats"},
        "willpower": {"name": "الإرادة", "category": "stats"},
        "wisdom": {"name": "الحكمة", "category": "stats"},
        "tact": {"name": "اللباقة", "category": "stats"},
        "eloquence": {"name": "البلاغة", "category": "stats"},
        "persuasion": {"name": "الإقناع", "category": "stats"},
        "confidence": {"name": "الثقة بالنفس", "category": "stats"},
        "composure": {"name": "الهدوء", "category": "stats"},
        "patience": {"name": "الصبر", "category": "stats"},
        "resilience": {"name": "المرونة", "category": "stats"},
        "determination": {"name": "التصميم", "category": "stats"},
        "discipline": {"name": "الانضباط", "category": "stats"},
        "curiosity": {"name": "الفضول", "category": "stats"},
        "creativity": {"name": "الإبداع", "category": "stats"},
        "wit": {"name": "الظرف", "category": "stats"},
        "humor": {"name": "الظرف", "category": "stats"},
        "ferocity": {"name": "القسوة", "category": "stats"},
        "dignity": {"name": "الكرامة", "category": "stats"},
        "morality": {"name": "الأخلاق", "category": "stats"},
        "morale": {"name": "الروح المعنوية", "category": "stats"},
        "honor": {"name": "الشرف", "category": "stats"},
        "mentalhealth": {"name": "الصحة النفسية", "category": "stats"},

        # === الرغبة والطاعة ===
        "desire": {"name": "الرغبة", "category": "desire"},
        "lust": {"name": "الشهوة", "category": "desire"},
        "obedience": {"name": "الطاعة", "category": "desire"},
        "subordination": {"name": "التبعية", "category": "desire"},
        "submission": {"name": "الخضوع", "category": "desire"},
        "dominance": {"name": "السيطرة", "category": "desire"},
        "arousal": {"name": "الإثارة", "category": "desire"},
        "libido": {"name": "الرغبة الجنسية", "category": "desire"},
        "seduction": {"name": "الإغراء", "category": "desire"},
        "instinct": {"name": "الغريزة", "category": "desire"},
        "allure": {"name": "السحر الجنسي", "category": "desire"},
        "sexualattraction": {"name": "الانجذاب الجنسي", "category": "desire"},
        "domination": {"name": "التسلط", "category": "desire"},
        "lewdness": {"name": "الفجور", "category": "desire"},
        "promiscuity": {"name": "التحرر الجنسي", "category": "desire"},
        "chastity": {"name": "العفة", "category": "desire"},
        "attachment": {"name": "الارتباط", "category": "desire"},

        # === البقاء ===
        "hunger": {"name": "الجوع", "category": "survival"},
        "thirst": {"name": "العطش", "category": "survival"},
        "sleep": {"name": "النوم", "category": "survival"},
        "exhaustion": {"name": "التعب", "category": "survival"},
        "temperature": {"name": "درجة الحرارة", "category": "survival"},
        "bodytemp": {"name": "درجة الحرارة", "category": "survival"},
        "oxygen": {"name": "الأكسجين", "category": "survival"},
        "o2": {"name": "الأكسجين", "category": "survival"},
        "poison": {"name": "السمية", "category": "survival"},
        "toxicity": {"name": "السمية", "category": "survival"},
        "radiation": {"name": "الإشعاع", "category": "survival"},
        "rads": {"name": "الإشعاع", "category": "survival"},
        "pain": {"name": "الألم", "category": "survival"},
        "illness": {"name": "المرض", "category": "survival"},
        "stress": {"name": "التوتر", "category": "survival"},
        "sanity": {"name": "الجنون", "category": "survival"},
        "insanity": {"name": "الجنون", "category": "survival"},
        "building": {"name": "البناء", "category": "survival"},
        "crafting": {"name": "التصنيع", "category": "survival"},
        "recipes": {"name": "الوصفات", "category": "survival"},
        "blueprints": {"name": "الوصفات", "category": "survival"},

        # === القتال ===
        "attack": {"name": "الهجوم", "category": "combat"},
        "atk": {"name": "الهجوم", "category": "combat"},
        "damage": {"name": "الضرر", "category": "combat"},
        "dmg": {"name": "الضرر", "category": "combat"},
        "intellect": {"name": "الذكاء", "category": "combat"},
        "int": {"name": "الذكاء", "category": "combat"},
        "wis": {"name": "الحكمة", "category": "combat"},
        "luck": {"name": "الحظ", "category": "combat"},
        "luk": {"name": "الحظ", "category": "combat"},
        "critical": {"name": "الضربة الحاسمة", "category": "combat"},
        "crit": {"name": "الضربة الحاسمة", "category": "combat"},
        "critchance": {"name": "فرصة الضربة الحاسمة", "category": "combat"},
        "critdamage": {"name": "ضرر الضربة الحاسمة", "category": "combat"},
        "dodge": {"name": "المراوغة", "category": "combat"},
        "evasion": {"name": "المراوغة", "category": "combat"},
        "parry": {"name": "التصدي", "category": "combat"},
        "accuracy": {"name": "الدقة", "category": "combat"},
        "hitrate": {"name": "الدقة", "category": "combat"},
        "attackrange": {"name": "مدى الهجوم", "category": "combat"},
        "penetration": {"name": "اختراق الدرع", "category": "combat"},
        "armorpenetration": {"name": "اختراق الدرع", "category": "combat"},
        "damageabsorption": {"name": "امتصاص الضرر", "category": "combat"},

        # === الصوت والصورة ===
        "volume": {"name": "مستوى الصوت", "category": "settings"},
        "bgm": {"name": "موسيقى الخلفية", "category": "settings"},
        "musicvolume": {"name": "موسيقى الخلفية", "category": "settings"},
        "sfx": {"name": "المؤثرات الصوتية", "category": "settings"},
        "soundeffects": {"name": "المؤثرات الصوتية", "category": "settings"},
        "brightness": {"name": "السطوع", "category": "settings"},
        "contrast": {"name": "التباين", "category": "settings"},
        "resolution": {"name": "دقة الشاشة", "category": "settings"},
        "fps": {"name": "معدل الإطارات", "category": "settings"},
        "framerate": {"name": "معدل الإطارات", "category": "settings"},
        "graphicsquality": {"name": "جودة الرسوميات", "category": "settings"},
        "shadows": {"name": "الظلال", "category": "settings"},
        "antialiasing": {"name": "مكافحة التعرج", "category": "settings"},
        "aa": {"name": "مكافحة التعرج", "category": "settings"},
    }

    # البادئات واللواحق
    PREFIXES = ["m_", "f_", "i_", "b_", "cur_", "max_", "min_", "base_",
                "total_", "current_", "default_", "temp_", "_"]
    SUFFIXES = ["_value", "_amount", "_count"]

    @classmethod
    def get_all_variable_names(cls) -> List[str]:
        """الحصول على جميع أسماء المتغيرات مع البادئات واللواحق"""
        result = set()
        for var in cls.ALL_VARIABLES.keys():
            result.add(var)
            for p in cls.PREFIXES:
                result.add(p + var)
            for s in cls.SUFFIXES:
                result.add(var + s)
                for p in cls.PREFIXES:
                    result.add(p + var + s)
        return list(result)

    @classmethod
    def get_variable_info(cls, var_name: str) -> Dict:
        """الحصول على معلومات المتغير (الاسم العربي، التصنيف)"""
        # إزالة البادئات واللواحق
        clean_name = var_name
        for p in cls.PREFIXES:
            if clean_name.startswith(p):
                clean_name = clean_name[len(p):]
                break
        for s in cls.SUFFIXES:
            if clean_name.endswith(s):
                clean_name = clean_name[:-len(s)]
                break
        return cls.ALL_VARIABLES.get(clean_name.lower(), {"name": clean_name, "category": "unknown"})

    # ================ أدوات التحليل المتقدمة ================

    @staticmethod
    def detect_file_type(file_path: str) -> Dict:
        """كشف نوع الملف باستخدام python-magic"""
        if not HAS_MAGIC:
            return {"type": "unknown", "mime": "unknown"}
        try:
            import magic
            mime = magic.from_file(file_path, mime=True)
            desc = magic.from_file(file_path)
            return {"type": desc, "mime": mime}
        except Exception as e:
            app_logger.error(f"File type detection failed: {e}")
            return {"type": "unknown", "mime": "unknown"}

    @staticmethod
    def analyze_pe(file_path: str) -> Dict:
        """تحليل ملف PE (Windows Executable)"""
        if not HAS_PEFILE:
            return {"error": "pefile not installed"}
        try:
            pe = pefile.PE(file_path)
            result = {
                "is_pe": True,
                "entry_point": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                "image_base": hex(pe.OPTIONAL_HEADER.ImageBase),
                "sections": [],
                "imports": [],
                "exports": [],
                "resources": []
            }

            # الأقسام
            for section in pe.sections:
                result["sections"].append({
                    "name": section.Name.decode().strip('\x00'),
                    "virtual_size": section.Misc_VirtualSize,
                    "virtual_address": hex(section.VirtualAddress),
                    "raw_size": section.SizeOfRawData,
                    "characteristics": hex(section.Characteristics)
                })

            # الاستيرادات
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode()
                    for imp in entry.imports:
                        result["imports"].append({
                            "dll": dll_name,
                            "name": imp.name.decode() if imp.name else f"ordinal_{imp.ordinal}",
                            "address": hex(imp.address)
                        })

            return result
        except Exception as e:
            app_logger.error(f"PE analysis failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def disassemble(data: bytes, arch: str = "x86", base_addr: int = 0) -> List[Dict]:
        """فك تجميع البيانات إلى تعليمات (Disassembly)"""
        if not HAS_CAPSTONE:
            return [{"error": "capstone not installed"}]

        try:
            if arch == "x86":
                mode = capstone.CS_MODE_32
            elif arch == "x64":
                mode = capstone.CS_MODE_64
            elif arch == "arm":
                mode = capstone.CS_MODE_ARM
            elif arch == "arm64":
                mode = capstone.CS_MODE_ARM64
            else:
                mode = capstone.CS_MODE_32

            md = capstone.Cs(capstone.CS_ARCH_X86, mode)
            instructions = []
            for insn in md.disasm(data, base_addr):
                instructions.append({
                    "address": hex(insn.address),
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "bytes": insn.bytes.hex()
                })
            return instructions
        except Exception as e:
            app_logger.error(f"Disassembly failed: {e}")
            return [{"error": str(e)}]

    @staticmethod
    def extract_strings_advanced(data: bytes, min_length: int = 4) -> Dict:
        """
        استخراج النصوص المتقدم مع كشف الترميزات المختلفة
        """
        results = {
            "ascii": [],
            "unicode": [],
            "hex": [],
            "found_variables": []
        }

        # ASCII
        current = []
        for b in data:
            if 32 <= b <= 126:
                current.append(chr(b))
            else:
                if len(current) >= min_length:
                    results["ascii"].append(''.join(current))
                current = []
        if len(current) >= min_length:
            results["ascii"].append(''.join(current))

        # Unicode (UTF-16 LE)
        current = []
        for i in range(0, len(data) - 1, 2):
            if data[i] != 0 and 32 <= data[i] <= 126:
                current.append(chr(data[i]))
            else:
                if len(current) >= min_length:
                    results["unicode"].append(''.join(current))
                current = []
        if len(current) >= min_length:
            results["unicode"].append(''.join(current))

        # البحث عن المتغيرات
        all_vars = AnalysisEngine.get_all_variable_names()
        for s in results["ascii"] + results["unicode"]:
            for var in all_vars:
                if var.lower() in s.lower():
                    info = AnalysisEngine.get_variable_info(var)
                    results["found_variables"].append({
                        "name": var,
                        "arabic_name": info.get("name", var),
                        "category": info.get("category", "unknown"),
                        "context": s[:50]
                    })
                    break

        return results

    @staticmethod
    def search_memory_pattern(data: bytes, pattern: bytes, mask: str = None) -> List[int]:
        """
        البحث عن نمط في الذاكرة (مشابه لـ Cheat Engine)
        """
        results = []
        if mask:
            # نمط مع قناع (مثل ? ? 00 01 ?)
            pattern_len = len(pattern)
            for i in range(len(data) - pattern_len):
                match = True
                for j in range(pattern_len):
                    if mask[j] != '?' and data[i + j] != pattern[j]:
                        match = False
                        break
                if match:
                    results.append(i)
        else:
            # بحث عادي
            pattern_len = len(pattern)
            for i in range(len(data) - pattern_len):
                if data[i:i + pattern_len] == pattern:
                    results.append(i)
        return results

    @staticmethod
    def analyze_elf(file_path: str) -> Dict:
        """تحليل ملف ELF (Linux Executable)"""
        if not HAS_ELFFILE:
            return {"error": "pyelftools not installed"}
        try:
            with open(file_path, 'rb') as f:
                elf = ELFFile(f)
                result = {
                    "is_elf": True,
                    "elf_class": "ELF64" if elf.elfclass == 64 else "ELF32",
                    "data_encoding": "LSB" if elf.little_endian else "MSB",
                    "entry_point": hex(elf.header.e_entry) if hasattr(elf.header, 'e_entry') else None,
                    "sections": []
                }
                for section in elf.iter_sections():
                    result["sections"].append({
                        "name": section.name,
                        "type": section.header.get('sh_type', 'unknown'),
                        "address": hex(section.header.get('sh_addr', 0)),
                        "size": section.header.get('sh_size', 0)
                    })
                return result
        except Exception as e:
            app_logger.error(f"ELF analysis failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def calculate_entropy(data: bytes) -> float:
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
    def calculate_entropy_from_file(file_path: str) -> float:
        data = FileSystem.read_binary(file_path)
        return AnalysisEngine.calculate_entropy(data) if data else 0.0

    @staticmethod
    def reverse_engineer_full(file_path: str) -> Dict:
        """
        الهندسة العكسية الكاملة للملف
        """
        app_logger.info(f"Starting full reverse engineering: {file_path}")

        results = {
            "file_path": file_path,
            "size": 0,
            "entropy": 0.0,
            "file_type": {},
            "pe_info": {},
            "elf_info": {},
            "strings": {},
            "variables": [],
            "instructions": [],
            "is_encrypted": False,
            "is_compressed": False,
            "suspicious_patterns": []
        }

        try:
            data = FileSystem.read_binary(file_path)
            if not data:
                return results

            results["size"] = len(data)
            results["entropy"] = AnalysisEngine.calculate_entropy(data)

            # كشف التشفير والضغط
            if results["entropy"] > 7.5:
                results["is_encrypted"] = True
            if b"PK" in data[:10] or b"GZIP" in data[:10] or b"\x1F\x8B" in data[:10]:
                results["is_compressed"] = True

            # كشف نوع الملف
            results["file_type"] = AnalysisEngine.detect_file_type(file_path)

            # تحليل PE
            if results["file_type"].get("mime") in ["application/x-dosexec", "application/x-msdownload"]:
                results["pe_info"] = AnalysisEngine.analyze_pe(file_path)

            # تحليل ELF
            if "ELF" in results["file_type"].get("type", ""):
                results["elf_info"] = AnalysisEngine.analyze_elf(file_path)

            # استخراج النصوص
            results["strings"] = AnalysisEngine.extract_strings_advanced(data)
            results["variables"] = results["strings"].get("found_variables", [])

            # فك التجميع (إذا كانت البيانات قابلة للتنفيذ)
            if len(data) < 100000:  # حد معقول
                results["instructions"] = AnalysisEngine.disassemble(data[:4096])

            app_logger.info(f"Reverse engineering completed: {len(results['variables'])} variables found")

        except Exception as e:
            app_logger.error(f"Reverse engineering failed: {e}")
            results["error"] = str(e)

        return results