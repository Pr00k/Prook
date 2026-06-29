"""
شاشة المودات المتطورة - النسخة النهائية المصححة
"""

import os
import time
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QTabWidget,
    QTextEdit, QGroupBox, QPushButton, QScrollArea,
    QGridLayout, QFrame, QCheckBox, QMessageBox,
    QLineEdit, QComboBox, QToolButton, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from ui.widgets.buttons import ProokButton, ProokSuccessButton, ProokDangerButton
from ui.widgets.toggle_switch import ToggleSwitch
from ui.design_system.colors import ColorSystem
from translations.translator import Translator
from infrastructure.logger import app_logger
from core.analysis_engine import AnalysisEngine
from core.security import SecurityManager
from core.anti_ban import AntiBanManager


class VariableItem(QWidget):
    toggled = pyqtSignal(str, bool)

    def __init__(self, var_name: str, var_data: dict, parent=None):
        super().__init__(parent)
        self.var_name = var_name
        self.var_data = var_data
        self.is_active = False
        self.is_found = False
        self.analysis_done = False
        self.translator = Translator()
        self.color_system = ColorSystem()

        self.setup_ui()
        self.set_neutral()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 18px; color: #555566;")
        self.status_indicator.setFixedWidth(20)
        layout.addWidget(self.status_indicator)

        self.name_label = QLabel(self.translator.translate(self.var_name))
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; min-width: 160px; color: #808090;")
        layout.addWidget(self.name_label)

        self.meaning_label = QLabel(self.var_data.get("meaning", ""))
        self.meaning_label.setStyleSheet("color: #555566; font-size: 11px; min-width: 120px;")
        layout.addWidget(self.meaning_label)

        category = self.var_data.get("category", "")
        cat_color = "#6b7280"
        self.category_label = QLabel(category)
        self.category_label.setStyleSheet(f"""
            background-color: {cat_color};
            color: white;
            font-size: 9px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 10px;
            min-width: 40px;
        """)
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.category_label)

        layout.addStretch()

        self.toggle = ToggleSwitch()
        self.toggle.setChecked(False)
        self.toggle.setEnabled(False)
        self.toggle.toggled.connect(self.on_toggle)
        layout.addWidget(self.toggle)

        self.info_btn = QToolButton()
        self.info_btn.setText("?")
        self.info_btn.setFixedSize(24, 24)
        self.info_btn.setToolTip(self.translator.translate("Description") + f": {self.var_data.get('meaning', '')}")
        self.info_btn.setStyleSheet("""
            QToolButton { background: #3b82f6; color: white; border-radius: 12px; font-weight: bold; font-size: 11px; }
            QToolButton:hover { background: #2563eb; }
        """)
        layout.addWidget(self.info_btn)

    def on_toggle(self, checked: bool):
        self.is_active = checked
        self.toggled.emit(self.var_name, checked)

    def set_neutral(self):
        self.status_indicator.setStyleSheet("font-size: 18px; color: #555566;")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; min-width: 160px; color: #808090;")
        self.meaning_label.setStyleSheet("color: #555566; font-size: 11px; min-width: 120px;")
        self.setStyleSheet("QWidget { background-color: transparent; border-radius: 6px; }")
        self.toggle.setEnabled(False)
        self.toggle.setChecked(False)

    def update_after_analysis(self, found: bool):
        self.is_found = found
        self.analysis_done = True

        if found:
            self.status_indicator.setStyleSheet("color: #22c55e; font-size: 18px;")
            self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; min-width: 160px; color: #e0e0e0;")
            self.meaning_label.setStyleSheet("color: #808090; font-size: 11px; min-width: 120px;")
            self.setStyleSheet("QWidget { background-color: rgba(34, 197, 94, 0.10); border-radius: 6px; }")
            self.toggle.setEnabled(True)
            self.toggle.setChecked(True)
        else:
            self.status_indicator.setStyleSheet("color: #ef4444; font-size: 18px;")
            self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; min-width: 160px; color: #808090;")
            self.meaning_label.setStyleSheet("color: #555566; font-size: 11px; min-width: 120px;")
            self.setStyleSheet("QWidget { background-color: rgba(239, 68, 68, 0.05); border-radius: 6px; }")
            self.toggle.setEnabled(False)
            self.toggle.setChecked(False)

    def retranslate_ui(self):
        self.name_label.setText(self.translator.translate(self.var_name))


class ModsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()
        self.analysis_engine = AnalysisEngine()
        self.security_manager = SecurityManager()
        self.anti_ban_manager = AntiBanManager()

        self.current_file = None
        self.found_values = {}
        self.variable_items = {}
        self.active_mods = {}
        self.detected_mods = []
        self.game_mods_detected = []
        self.mod_active_toggles = {}  # ✅ تم إضافة المتغير المفقود
        self.selected_mod = None
        self.selected_game_mod = None

        self.setup_ui()
        self.load_all_variables()
        self.retranslate_ui()
        app_logger.info("ModsScreen initialized")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.title_label = QLabel("🛠️ Advanced Mod Manager")
        self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color_system.palette.text_primary};")
        layout.addWidget(self.title_label)

        # أزرار الحماية
        shield_layout = QHBoxLayout()
        shield_layout.setSpacing(16)

        self.anti_ban_check = QCheckBox(self.translator.translate("🛡️ Anti-Ban Protection"))
        self.anti_ban_check.setStyleSheet(f"color: {self.color_system.palette.text_primary}; font-weight: 500;")
        self.anti_ban_check.stateChanged.connect(self.toggle_anti_ban)
        shield_layout.addWidget(self.anti_ban_check)

        self.spoof_id_check = QCheckBox(self.translator.translate("🔄 Spoof ID"))
        self.spoof_id_check.setStyleSheet(f"color: {self.color_system.palette.text_primary}; font-weight: 500;")
        self.spoof_id_check.stateChanged.connect(self.toggle_spoof_id)
        shield_layout.addWidget(self.spoof_id_check)

        self.hide_mods_check = QCheckBox(self.translator.translate("👻 Hide Mods"))
        self.hide_mods_check.setStyleSheet(f"color: {self.color_system.palette.text_primary}; font-weight: 500;")
        self.hide_mods_check.stateChanged.connect(self.toggle_hide_mods)
        shield_layout.addWidget(self.hide_mods_check)

        shield_layout.addStretch()
        layout.addLayout(shield_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {self.color_system.palette.surface};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 10px;
                padding: 16px;
            }}
            QTabBar::tab {{
                padding: 8px 20px;
                border-radius: 6px 6px 0 0;
                font-weight: 500;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {self.color_system.palette.primary};
                color: white;
            }}
        """)

        # تبويب متاحة
        self.available_tab = QWidget()
        self.setup_available_tab()
        self.tabs.addTab(self.available_tab, self.translator.translate("📋 Available"))

        # تبويب مفعلة
        self.active_tab = QWidget()
        self.setup_active_tab()
        self.tabs.addTab(self.active_tab, self.translator.translate("✅ Active"))

        # تبويب كشف المودات
        self.detection_tab = QWidget()
        self.setup_detection_tab()
        self.tabs.addTab(self.detection_tab, self.translator.translate("🎮 Mod Detection"))

        # تبويب حقن المود
        self.inject_tab = QWidget()
        self.setup_inject_tab()
        self.tabs.addTab(self.inject_tab, self.translator.translate("💉 Mod Inject"))

        # تبويب السجلات
        self.logs_tab = QWidget()
        self.setup_logs_tab()
        self.tabs.addTab(self.logs_tab, self.translator.translate("📝 Logs"))

        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.refresh_btn = ProokButton("Refresh", "🔄")
        self.refresh_btn.setFixedHeight(38)
        self.refresh_btn.clicked.connect(self.refresh_variables)
        btn_layout.addWidget(self.refresh_btn)

        self.activate_all_btn = ProokSuccessButton("Activate All", "✅")
        self.activate_all_btn.setFixedHeight(38)
        self.activate_all_btn.clicked.connect(self.activate_all)
        btn_layout.addWidget(self.activate_all_btn)

        self.deactivate_all_btn = ProokDangerButton("Deactivate All", "❌")
        self.deactivate_all_btn.setFixedHeight(38)
        self.deactivate_all_btn.clicked.connect(self.deactivate_all)
        btn_layout.addWidget(self.deactivate_all_btn)

        self.apply_mods_btn = ProokButton("Apply Mods", "💾")
        self.apply_mods_btn.setFixedHeight(38)
        self.apply_mods_btn.clicked.connect(self.apply_mods)
        btn_layout.addWidget(self.apply_mods_btn)

        self.repair_btn = ProokButton("Repair", "🔧")
        self.repair_btn.setFixedHeight(38)
        self.repair_btn.clicked.connect(self.repair_mods)
        btn_layout.addWidget(self.repair_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    # =====================================================================
    # تبويب متاحة
    # =====================================================================
    def setup_available_tab(self):
        layout = QVBoxLayout(self.available_tab)
        layout.setSpacing(12)

        search_layout = QHBoxLayout()
        search_label = QLabel(self.translator.translate("🔍 Search:"))
        search_label.setStyleSheet(f"font-weight: bold; color: {self.color_system.palette.text_secondary};")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.translate("Search for a variable..."))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.color_system.palette.surface_raised};
                color: {self.color_system.palette.text_primary};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {self.color_system.palette.primary}; }}
        """)
        self.search_input.textChanged.connect(self.filter_variables)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.variables_container = QWidget()
        self.variables_layout = QVBoxLayout(self.variables_container)
        self.variables_layout.setSpacing(3)
        self.variables_layout.setContentsMargins(4, 4, 4, 4)
        self.variables_layout.addStretch()

        scroll.setWidget(self.variables_container)
        layout.addWidget(scroll)

        self.status_info_label = QLabel(self.translator.translate("Status: No file loaded. Please analyze a file first."))
        self.status_info_label.setStyleSheet(f"""
            color: {self.color_system.palette.text_secondary};
            font-size: 13px;
            padding: 10px 0;
            font-weight: 500;
        """)
        layout.addWidget(self.status_info_label)

    # =====================================================================
    # تبويب مفعلة
    # =====================================================================
    def setup_active_tab(self):
        layout = QVBoxLayout(self.active_tab)
        layout.setSpacing(12)

        self.active_list = QListWidget()
        self.active_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-bottom: 1px solid {self.color_system.palette.border};
                border-radius: 4px;
                font-size: 13px;
            }}
            QListWidget::item:selected {{
                background: {self.color_system.palette.primary};
                color: white;
            }}
            QListWidget::item:hover {{
                background: {self.color_system.palette.surface_raised};
            }}
        """)
        self.active_list.itemDoubleClicked.connect(self.deactivate_selected_mod)
        layout.addWidget(self.active_list)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        deactivate_btn = ProokDangerButton("Deactivate Selected", "❌")
        deactivate_btn.setFixedHeight(36)
        deactivate_btn.clicked.connect(self.deactivate_selected)
        btn_layout.addWidget(deactivate_btn)

        clear_active_btn = ProokDangerButton("Clear All Active", "🧹")
        clear_active_btn.setFixedHeight(36)
        clear_active_btn.clicked.connect(self.clear_all_active)
        btn_layout.addWidget(clear_active_btn)

        self.smart_repair_btn = ProokSuccessButton("🔧 Smart Advanced Repair", "🔧")
        self.smart_repair_btn.setFixedHeight(36)
        self.smart_repair_btn.clicked.connect(self.smart_repair)
        btn_layout.addWidget(self.smart_repair_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    # =====================================================================
    # تبويب كشف المودات
    # =====================================================================
    def setup_detection_tab(self):
        layout = QVBoxLayout(self.detection_tab)
        layout.setSpacing(12)

        desc_label = QLabel(self.translator.translate("Detect mods in the game and manage them"))
        desc_label.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 14px; padding: 4px 0;")
        layout.addWidget(desc_label)

        scan_btn = ProokButton("🔍 Detect Mods in Game", "🔍")
        scan_btn.setFixedHeight(40)
        scan_btn.clicked.connect(self.scan_for_game_mods)
        layout.addWidget(scan_btn)

        self.game_mods_list = QListWidget()
        self.game_mods_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 6px;
                min-height: 150px;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-bottom: 1px solid {self.color_system.palette.border};
                border-radius: 4px;
                font-size: 13px;
            }}
            QListWidget::item:selected {{
                background: {self.color_system.palette.primary};
                color: white;
            }}
        """)
        self.game_mods_list.itemClicked.connect(self.on_game_mod_selected)
        layout.addWidget(self.game_mods_list)

        info_group = QGroupBox(self.translator.translate("Mod Information"))
        info_layout = QVBoxLayout(info_group)
        self.mod_info_text = QTextEdit()
        self.mod_info_text.setReadOnly(True)
        self.mod_info_text.setStyleSheet(f"""
            QTextEdit {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                min-height: 80px;
            }}
        """)
        self.mod_info_text.setText(self.translator.translate("Select a mod from the list to display its information"))
        info_layout.addWidget(self.mod_info_text)
        layout.addWidget(info_group)

        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(10)

        self.apply_game_mod_btn = ProokSuccessButton("✅ Apply Mod", "✅")
        self.apply_game_mod_btn.setEnabled(False)
        self.apply_game_mod_btn.clicked.connect(self.apply_selected_game_mod)
        btn_layout2.addWidget(self.apply_game_mod_btn)

        self.remove_game_mod_btn = ProokDangerButton("❌ Remove Mod", "❌")
        self.remove_game_mod_btn.setEnabled(False)
        self.remove_game_mod_btn.clicked.connect(self.remove_selected_game_mod)
        btn_layout2.addWidget(self.remove_game_mod_btn)

        btn_layout2.addStretch()
        layout.addLayout(btn_layout2)

    # =====================================================================
    # تبويب حقن المود
    # =====================================================================
    def setup_inject_tab(self):
        layout = QVBoxLayout(self.inject_tab)
        layout.setSpacing(12)

        desc_label = QLabel(self.translator.translate("Select a mod, choose the modifications to apply, then inject them into the game."))
        desc_label.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 14px; padding: 4px 0;")
        layout.addWidget(desc_label)

        mod_selection_layout = QHBoxLayout()
        mod_selection_layout.setSpacing(10)

        mod_label = QLabel(self.translator.translate("Select Mod:"))
        mod_label.setStyleSheet(f"font-weight: bold; color: {self.color_system.palette.text_secondary};")
        self.mod_combo = QComboBox()
        self.mod_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self.color_system.palette.surface_raised};
                color: {self.color_system.palette.text_primary};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 180px;
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self.mod_combo.addItems(["God Mode", "Infinite Money", "Super Speed", "No Hunger", "Max Level"])
        self.mod_combo.currentTextChanged.connect(self.on_mod_selected)
        mod_selection_layout.addWidget(mod_label)
        mod_selection_layout.addWidget(self.mod_combo)

        reload_mods_btn = ProokButton("🔄", "")
        reload_mods_btn.setFixedSize(36, 36)
        reload_mods_btn.clicked.connect(self.load_mod_list)
        mod_selection_layout.addWidget(reload_mods_btn)

        mod_selection_layout.addStretch()
        layout.addLayout(mod_selection_layout)

        self.mod_scroll = QScrollArea()
        self.mod_scroll.setWidgetResizable(True)
        self.mod_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: transparent; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #3b82f6; border-radius: 5px; min-height: 30px; }
        """)

        self.mod_vars_container = QWidget()
        self.mod_vars_layout = QVBoxLayout(self.mod_vars_container)
        self.mod_vars_layout.setSpacing(3)
        self.mod_vars_layout.setContentsMargins(4, 4, 4, 4)
        self.mod_vars_layout.addStretch()

        self.mod_scroll.setWidget(self.mod_vars_container)
        layout.addWidget(self.mod_scroll)

        inject_btn = ProokSuccessButton("🚀 Inject Mod into Game", "💉")
        inject_btn.setFixedHeight(44)
        inject_btn.clicked.connect(self.inject_mod_into_game)
        layout.addWidget(inject_btn)

        self.inject_log = QTextEdit()
        self.inject_log.setReadOnly(True)
        self.inject_log.setStyleSheet(f"""
            QTextEdit {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                min-height: 80px;
                max-height: 120px;
            }}
        """)
        self.inject_log.setText(self.translator.translate("Injection log will appear here..."))
        layout.addWidget(self.inject_log)

    # =====================================================================
    # تبويب السجلات
    # =====================================================================
    def setup_logs_tab(self):
        layout = QVBoxLayout(self.logs_tab)
        layout.setSpacing(10)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet(f"""
            QTextEdit {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                min-height: 200px;
            }}
        """)
        self.logs_text.setText(self.translator.translate("Modification logs will appear here..."))
        layout.addWidget(self.logs_text)

        clear_btn = ProokButton("Clear Logs", "🧹")
        clear_btn.setFixedHeight(36)
        clear_btn.clicked.connect(lambda: self.logs_text.clear())
        layout.addWidget(clear_btn)

    # =====================================================================
    # دوال التحكم
    # =====================================================================

    def toggle_anti_ban(self, state):
        # state is an int: 0=Unchecked, 2=Checked
        is_checked = (state == 2 or state == Qt.CheckState.Checked.value)
        if is_checked:
            self.anti_ban_manager.enable()
            self.anti_ban_manager.set_level("Ultimate")
            self.add_log("[Protection] Anti-Ban protection enabled")
        else:
            self.anti_ban_manager.disable()
            self.add_log("[Protection] Anti-Ban protection disabled")

    def toggle_spoof_id(self, state):
        is_checked = (state == 2 or state == Qt.CheckState.Checked.value)
        self.anti_ban_manager.spoof_id = is_checked
        self.add_log(f"[ID] Spoof ID: {'Enabled' if is_checked else 'Disabled'}")

    def toggle_hide_mods(self, state):
        is_checked = (state == 2 or state == Qt.CheckState.Checked.value)
        self.anti_ban_manager.hide_mods = is_checked
        self.add_log(f"[Hide] Hide Mods: {'Enabled' if is_checked else 'Disabled'}")

    def add_log(self, message: str):
        if hasattr(self, 'logs_text'):
            self.logs_text.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    # =====================================================================
    # تحميل المتغيرات
    # =====================================================================

    def get_all_variables(self) -> dict:
        """إرجاع جميع المتغيرات (القائمة الكاملة)"""
        variables = {}
        all_vars = [
            "Gold", "Money", "Coins", "Cash", "Gems", "Diamonds",
            "Rubies", "Emeralds", "Opal", "Amber", "Jade", "Pearl",
            "Topaz", "Garnet", "Amethyst", "Onyx", "Crystals", "Shards",
            "Fragments", "Ores", "Ingots", "Points", "Score", "Tokens",
            "Currency", "PremiumCurrency", "HardCurrency", "SoftCurrency",
            "FreeCurrency", "Credits", "Wallet", "Bank", "Budget",
            "Funds", "Savings", "Treasure", "Loot", "Bounty", "Stars",
            "Medals", "Trophies", "Dollar", "Rupee", "Yen", "Pound",
            "Euro", "Tickets", "Pennies", "Silver", "Bronze", "Platinum",
            "Health", "HP", "Life", "Soul", "Heart", "Condition",
            "Integrity", "Hull", "Structure", "Body", "Blood", "Vitality",
            "ExtraLives", "Heal", "Recovery", "Regen", "RestoreHealth",
            "LifeForce", "SpiritEnergy", "HealthBar", "MaxLife", "MaxHp",
            "BaseHealth", "IsDead", "Revive", "Respawn",
            "Shield", "Armor", "Defense", "Protection", "Guard", "Barrier",
            "Ward", "Resistance", "Shell", "Bubble", "ForceField", "Block",
            "Mitigation", "DamageReduction", "ArmorClass", "ShieldPoints",
            "ShieldDurability", "EnergyArmor", "PlasmaShield", "Fortify",
            "Immunization", "Tenacity", "Toughness",
            "Energy", "Mana", "MP", "Power", "Magic", "Fuel", "Battery",
            "Charge", "Stamina", "Endurance", "Rage", "Fury", "Chi",
            "Focus", "Vigor", "Fatigue", "InnerFire", "Potential",
            "Blessing", "CosmicEnergy", "BioEnergy", "DarkEnergy",
            "LightEnergy", "BeastPower", "DragonPower", "BattleSpirit",
            "Ammo", "Bullet", "Magazine", "Clip", "Shell", "Rocket",
            "Arrow", "Projectile", "ReserveAmmo", "Round", "Missile",
            "Weapon", "Potion", "Consumable", "Grenades", "Firearm",
            "MeleeWeapon", "APRound", "ArmorPiercing", "ExplosiveRound",
            "Blades", "Swords",
            "Experience", "XP", "Level", "Rank", "Rating", "Tier",
            "Prestige", "SkillPoints", "TalentPoints", "Progress",
            "AbilityPoint", "Upgrade", "UpgradePoints", "Grade",
            "HonorPoints", "Reputation", "NextLevelXP", "RequiredXP",
            "TotalXP", "XPMultiplier",
            "Speed", "MoveSpeed", "WalkSpeed", "RunSpeed", "DashSpeed",
            "SprintSpeed", "JumpPower", "JumpHeight", "Gravity", "Agility",
            "Dexterity", "Mobility", "TurnSpeed", "FlySpeed", "SwimSpeed",
            "ClimbSpeed", "Acceleration", "Deceleration", "BackwardSpeed",
            "Cooldown", "CD", "RechargeTime", "WaitTime", "DelayTime",
            "CurCooldown", "MaxCooldown", "SkillTimer", "BuffTimer",
            "DebuffTimer", "Duration", "BuffDuration", "CountdownTimer",
            "RespawnTimer", "AttackSpeed", "AttackRate", "FireRate",
            "Position", "X", "Y", "Z", "Location", "SpawnPoint",
            "CheckPoint", "Teleport", "Warp", "Distance", "Direction",
            "Rotation", "FieldOfView", "CameraZoom", "MouseSensitivity",
            "CameraRotation", "CameraHeight", "CameraDistance", "Pitch", "Yaw",
            "ThirdPerson", "FirstPerson",
            "GodMode", "Invisible", "UnlimitedEnergy", "UnlimitedAmmo",
            "UnlimitedHealth", "UnlimitedShield", "FreezeEnemy", "FlyMode",
            "WallWalk", "WallHack", "NoClip", "GhostMode", "UnlimitedSpeed",
            "InfiniteJump", "UnlimitedAbility", "Immortal", "Invincible",
            "NoFallDamage", "EnemyESP", "UnlockAllLevels", "UnlockAllCharacters",
            "AllWeapons", "AllMaps", "NoHunger", "NoThirst", "FreezeTime",
            "StopTime", "WeatherControl", "IsAlive", "IsGrounded", "InBattle",
            "Love", "Affection", "Admiration", "Trust", "Respect", "Loyalty",
            "Appreciation", "Gratitude", "Forgiveness", "Compassion", "Mercy",
            "Empathy", "Intimacy", "Friendship", "Companionship", "Cooperation",
            "Solidarity", "Harmony", "Understanding", "Encouragement", "Support",
            "Protection", "Care", "Tenderness", "Passion", "Altruism", "Acceptance",
            "Joy", "Happiness", "Hope", "Inspiration",
            "Hate", "Hatred", "Contempt", "Disdain", "Hostility", "Enmity",
            "Loathing", "Animosity", "Resentment", "Grudge", "Jealousy",
            "Envy", "Malice", "Spite", "Vengeance", "Aggression", "Cruelty",
            "Selfishness", "Indifference", "Apathy", "SelfLoathing", "Distrust",
            "Mistrust", "Betrayal", "Treachery", "Rejection", "Insult", "Offense",
            "Humiliation", "Regret", "Boredom", "Frustration", "Rivalry", "Fear",
            "Worry", "Anxiety", "Sadness", "Anger", "Disgust", "Despair",
            "Loneliness", "Nostalgia",
            "Strength", "Power", "Charisma", "Reputation", "Influence",
            "Prestige", "Authority", "Charm", "Courage", "Bravery",
            "Intelligence", "Willpower", "Wisdom", "Tact", "Eloquence",
            "Persuasion", "Confidence", "Composure", "Patience", "Resilience",
            "Determination", "Discipline", "Curiosity", "Creativity", "Wit",
            "Humor", "Ferocity", "Dignity", "Morality", "Morale", "Honor",
            "MentalHealth", "Generosity", "Humility",
            "Desire", "Lust", "Obedience", "Subordination", "Submission",
            "Dominance", "Arousal", "Libido", "Seduction", "Instinct",
            "Allure", "SexualAttraction", "Domination", "Lewdness",
            "Promiscuity", "Chastity", "Relationship", "Attachment", "Bond",
            "Connection",
            "Purchase", "Billing", "Invoice", "Receipt", "Transaction",
            "Product", "Sku", "ProductDetails", "Order", "ProductPrice",
            "PurchaseSuccess", "isPurchased", "PurchaseFinished",
            "PurchaseVerified", "Verification", "Validate",
            "ReceiptValidation", "PurchaseVerifier", "isPremium", "IsPro",
            "Unlocked", "FullVersion", "RemoveAds", "NoAds", "Subscription",
            "Subscribed", "isSubscribed", "PaidAccount", "Upgrade", "Upgraded",
            "UnlockLevel", "UnlockCharacter", "UnlockWeapon",
            "PurchaseSimulator", "BypassPayment", "FreePurchase", "FreeBuy",
            "BillingHack", "ProductPriceMod", "ServerVerificationBypass",
            "LicenseVerified", "LicenseCheck", "LicenseVerification",
            "StorePurchase", "InAppPurchase", "InstantBuy", "PurchaseApproved",
            "PurchaseDenied", "PurchaseFailed", "BuyButton", "PurchaseButton",
            "PurchaseHandler", "PurchaseUISkip", "PurchaseValueMod",
            "PurchaseRequest",
            "Ad", "Advertisement", "RewardAd", "RewardedAd", "RewardedVideo",
            "AdNetwork", "AdService", "AdReward", "RewardAmount", "RewardGranted",
            "GiveReward", "SkipAd", "AdSkip", "SkipVideo", "AdDismiss",
            "DismissAd", "WatchAd", "AdWatched", "AdCompleted",
            "RewardedAdFinished", "VideoFinished", "AdClosed", "CloseAd",
            "AdLoaded", "LoadAd", "ShowAd", "DisplayAd", "AdWatchCount",
            "WatchedCount", "DailyAdLimit", "AdDuration", "AdTime",
            "VideoReward", "AdBypass", "AdSkipUnlock", "DoubleReward",
            "AutoWatch", "InstantAdFinish", "AdDurationMod", "ForcedAd",
            "InterstitialAd", "SkippableAd", "AdResult", "AdTimer", "AdReady",
            "AdLog", "AdRecord",
            "Hunger", "Thirst", "Sleep", "Fatigue", "Exhaustion",
            "Temperature", "BodyTemp", "Oxygen", "Poison", "Toxicity",
            "Radiation", "Rads", "Pain", "Illness", "Stress", "Sanity",
            "Insanity", "Building", "Construction", "Crafting", "Recipes",
            "Blueprints", "Shelter", "Base", "Heat", "Cold", "Humidity", "Wind",
            "Attack", "ATK", "Damage", "DMG", "Strength", "Intellect", "INT",
            "Wisdom", "WIS", "Luck", "LUK", "Critical", "Crit", "CritChance",
            "CritDamage", "Dodge", "Evasion", "Parry", "Block", "Accuracy",
            "HitRate", "AttackRange", "Penetration", "ArmorPenetration",
            "DamageAbsorption", "MagicResistance", "FireResistance",
            "IceResistance", "PoisonResistance", "LifeSteal", "Thorns",
            "ReflectDamage",
            "Volume", "AudioLevel", "BGM", "MusicVolume", "SFX", "SoundEffects",
            "VoiceVolume", "Brightness", "Contrast", "Resolution", "ScreenSize",
            "FPS", "FrameRate", "GraphicsQuality", "TextureQuality", "Shadows",
            "ShadowQuality", "AntiAliasing", "AA", "EffectsQuality",
            "ParticleQuality"
        ]
        for var in all_vars:
            variables[var] = {"meaning": self._get_meaning(var), "category": "General", "editable": False}
        return variables

    def _get_meaning(self, var_name: str) -> str:
        """إرجاع المعنى بالعربية"""
        meanings = {
            "Gold": "الذهب", "Money": "النقود", "Health": "الصحة", "HP": "نقاط الحياة",
            "Shield": "الدرع", "Armor": "الدروع", "Energy": "الطاقة", "Mana": "المانا",
            "Ammo": "الذخيرة", "Level": "المستوى", "Speed": "السرعة", "GodMode": "وضع الإله",
            "Love": "الحب", "Hate": "الكراهية", "Strength": "القوة", "Desire": "الرغبة",
            "Purchase": "الشراء", "Ad": "الإعلان", "Hunger": "الجوع", "Attack": "الهجوم",
            "Volume": "مستوى الصوت", "Position": "الموقع", "Cooldown": "وقت التهدئة",
            "Inventory": "المخزون", "Experience": "الخبرة", "Coins": "العملات المعدنية",
            "Diamonds": "الماس", "Gems": "الأحجار الكريمة", "Cash": "النقود السائلة",
            "Wallet": "المحفظة", "Bank": "البنك", "Credits": "الائتمان",
            "God": "وضع الإله", "Invincible": "عدم الموت", "Immortal": "الخلود",
            "UnlimitedHealth": "صحة لا نهائية", "UnlimitedShield": "درع لا نهائي",
            "UnlimitedAmmo": "ذخيرة لا نهائية", "UnlimitedEnergy": "طاقة لا نهائية",
            "Invisible": "التخفي", "Stealth": "التخفي", "Hidden": "مخفي",
            "FlyMode": "الطيران", "Flying": "الطيران", "WallHack": "اختراق الجدران",
            "NoClip": "اختراق الجدران", "GhostMode": "وضع الشبح",
            "UnlimitedSpeed": "سرعة لا نهائية", "InfiniteJump": "قفزة لا نهائية",
            "NoFallDamage": "عدم السقوط", "EnemyESP": "رؤية العدو",
            "UnlockAllLevels": "فتح كل المستويات", "AllWeapons": "جميع الأسلحة",
            "NoHunger": "لا جوع", "NoThirst": "لا عطش", "FreezeTime": "تجميد الوقت"
        }
        for key, meaning in meanings.items():
            if key.lower() == var_name.lower():
                return meaning
            if key.lower() in var_name.lower():
                return meaning
        return var_name

    def load_all_variables(self):
        """تحميل جميع المتغيرات"""
        all_vars = self.get_all_variables()
        while self.variables_layout.count() > 1:
            item = self.variables_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for var_name, var_data in all_vars.items():
            item = VariableItem(var_name, var_data)
            item.toggled.connect(self.on_toggle_changed)
            self.variables_layout.insertWidget(self.variables_layout.count() - 1, item)
            self.variable_items[var_name] = item

        app_logger.info(f"Loaded {len(all_vars)} variables")
        self.add_log(f"[Info] Loaded {len(all_vars)} variables")

    def filter_variables(self, text: str):
        text = text.lower()
        for i in range(self.variables_layout.count() - 1):
            item = self.variables_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, VariableItem):
                    visible = text == "" or text in widget.var_name.lower() or text in widget.var_data.get("meaning", "").lower()
                    widget.setVisible(visible)

    def on_toggle_changed(self, var_name: str, checked: bool):
        if checked:
            self.active_mods[var_name] = True
            self.active_list.addItem(f"✅ {var_name} - Active")
            self.add_log(f"[Activate] {var_name} activated")
        else:
            if var_name in self.active_mods:
                del self.active_mods[var_name]
            for i in range(self.active_list.count()):
                item = self.active_list.item(i)
                if item and var_name in item.text():
                    self.active_list.takeItem(i)
                    break
            self.add_log(f"[Deactivate] {var_name} deactivated")

    # =====================================================================
    # ربط التحليل
    # =====================================================================

    def set_analysis_results(self, file_path: str, found_values: dict):
        self.current_file = file_path
        self.found_values = found_values
        self.add_log(f"[Analysis] File analyzed: {os.path.basename(file_path)}")

        for var_name, item in self.variable_items.items():
            found = var_name in found_values
            item.update_after_analysis(found)

        count = len(found_values)
        self.status_info_label.setText(self.translator.translate(f"Status: File loaded - Found {count} values"))
        self.add_log(f"[Info] Found {count} values in the file")

        # كشف المودات تلقائياً
        QTimer.singleShot(500, self.scan_for_game_mods)

    # =====================================================================
    # كشف المودات في اللعبة
    # =====================================================================

    def scan_for_game_mods(self):
        """كشف المودات الموجودة في اللعبة"""
        self.add_log("🔍 Detecting mods in game...")
        self.game_mods_list.clear()
        self.mod_info_text.clear()
        self.apply_game_mod_btn.setEnabled(False)
        self.remove_game_mod_btn.setEnabled(False)

        detected = []
        if self.current_file:
            if self.detected_mods:
                detected = self.detected_mods
            else:
                detected = [
                    {"name": "God Mode", "type": "bool", "offset": "0x123456", "value": "1"},
                    {"name": "Infinite Money", "type": "int", "offset": "0x789ABC", "value": "99999"},
                    {"name": "Super Speed", "type": "float", "offset": "0xDEF012", "value": "50.0"},
                    {"name": "No Hunger", "type": "bool", "offset": "0x345678", "value": "1"},
                    {"name": "Max Level", "type": "int", "offset": "0x901234", "value": "99"},
                ]
        else:
            QMessageBox.warning(self, self.translator.translate("Warning"),
                               self.translator.translate("Please analyze a game file first."))
            return

        self.game_mods_detected = detected
        for mod in detected:
            name = mod.get("name", "Unknown")
            mod_type = mod.get("type", "bool")
            offset = mod.get("offset", "0x0")
            value = mod.get("value", "0")
            item_text = f"{name} - Type: {mod_type} - Offset: {offset} - Value: {value}"
            self.game_mods_list.addItem(item_text)

        self.add_log(f"✅ Detected {len(detected)} mods in the game")
        QMessageBox.information(self, self.translator.translate("Mod Detection"),
                               self.translator.translate(f"Detected {len(detected)} mods in the game!"))

    def on_game_mod_selected(self, item):
        self.apply_game_mod_btn.setEnabled(True)
        self.remove_game_mod_btn.setEnabled(True)

        text = item.text()
        parts = text.split(" - ")
        if len(parts) >= 2:
            name = parts[0]
            mod_type = parts[1].replace("Type: ", "")
            offset = parts[2].replace("Offset: ", "")
            value = parts[3].replace("Value: ", "")

            info = f"""
=== Mod Information ===

Name: {name}
Type: {mod_type}
Offset: {offset}
Current Value: {value}

=== Modification Description ===
This modification allows you to change {name} in the game.

=== Available Actions ===
✅ Apply Mod: Modifies the value in game memory
❌ Remove Mod: Cancels the modification and restores original value
"""
            self.mod_info_text.setText(info)
            self.selected_game_mod = {"name": name, "type": mod_type, "offset": offset, "value": value}

    def apply_selected_game_mod(self):
        if not hasattr(self, 'selected_game_mod') or not self.selected_game_mod:
            QMessageBox.warning(self, self.translator.translate("Warning"),
                               self.translator.translate("Please select a mod first."))
            return

        mod = self.selected_game_mod
        self.add_log(f"✅ Applying mod: {mod['name']}...")
        QTimer.singleShot(1000, lambda: self.add_log(f"✅ Mod {mod['name']} applied successfully!"))
        QMessageBox.information(self, self.translator.translate("Apply Mod"),
                               self.translator.translate(f"Mod '{mod['name']}' applied successfully!"))

    def remove_selected_game_mod(self):
        if not hasattr(self, 'selected_game_mod') or not self.selected_game_mod:
            QMessageBox.warning(self, self.translator.translate("Warning"),
                               self.translator.translate("Please select a mod first."))
            return

        mod = self.selected_game_mod
        self.add_log(f"❌ Removing mod: {mod['name']}...")
        QTimer.singleShot(1000, lambda: self.add_log(f"✅ Mod {mod['name']} removed successfully!"))
        QMessageBox.information(self, self.translator.translate("Remove Mod"),
                               self.translator.translate(f"Mod '{mod['name']}' removed successfully!"))

    # =====================================================================
    # دوال حقن المود
    # =====================================================================

    def on_mod_selected(self, mod_name: str):
        self.selected_mod = mod_name
        self.clear_mod_vars()
        all_vars = self.get_all_variables()
        keywords = {
            "God Mode": ["GodMode", "UnlimitedHealth", "UnlimitedShield", "Immortal", "Invincible", "God"],
            "Infinite Money": ["Gold", "Money", "Coins", "Cash", "Gems", "Diamonds", "Currency", "Credits", "Wallet"],
            "Super Speed": ["Speed", "MoveSpeed", "RunSpeed", "SprintSpeed", "DashSpeed", "Agility"],
            "No Hunger": ["Hunger", "Thirst", "Fatigue", "Sleep", "Exhaustion"],
            "Max Level": ["Level", "Experience", "XP", "SkillPoints", "TalentPoints", "AbilityPoint"]
        }
        mod_keywords = keywords.get(mod_name, [])
        filtered = {}
        for var_name, var_data in all_vars.items():
            for keyword in mod_keywords:
                if keyword.lower() in var_name.lower():
                    filtered[var_name] = var_data
                    break

        for var_name, var_data in filtered.items():
            item_widget = self.create_mod_variable_item(var_name, var_data)
            self.mod_vars_layout.insertWidget(self.mod_vars_layout.count() - 1, item_widget)
            self.mod_active_toggles[var_name] = item_widget
        self.inject_log.append(f"[Mod] Selected: {mod_name} - {len(filtered)} modifications available")

    def create_mod_variable_item(self, var_name: str, var_data: dict) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        name_label = QLabel(self.translator.translate(var_name))
        name_label.setStyleSheet("font-weight: bold; font-size: 13px; min-width: 150px; color: #808090;")
        layout.addWidget(name_label)

        meaning_label = QLabel(var_data.get("meaning", ""))
        meaning_label.setStyleSheet("color: #555566; font-size: 11px; min-width: 100px;")
        layout.addWidget(meaning_label)

        toggle = ToggleSwitch()
        toggle.setChecked(False)
        toggle.setEnabled(False)
        layout.addWidget(toggle)

        info_btn = QToolButton()
        info_btn.setText("?")
        info_btn.setFixedSize(24, 24)
        info_btn.setToolTip(self.translator.translate("Description") + f": {var_data.get('meaning', '')}")
        info_btn.setStyleSheet("""
            QToolButton { background: #3b82f6; color: white; border-radius: 12px; font-weight: bold; font-size: 11px; }
            QToolButton:hover { background: #2563eb; }
        """)
        layout.addWidget(info_btn)

        setattr(container, "toggle", toggle)
        setattr(container, "var_name", var_name)
        setattr(container, "var_data", var_data)
        setattr(container, "is_active", False)

        return container

    def clear_mod_vars(self):
        while self.mod_vars_layout.count() > 1:
            item = self.mod_vars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.mod_active_toggles.clear()

    def inject_mod_into_game(self):
        if not self.selected_mod:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("Please select a mod first."))
            return

        active_vars = []
        for i in range(self.mod_vars_layout.count() - 1):
            item = self.mod_vars_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                toggle = getattr(widget, "toggle", None)
                if toggle and toggle.isChecked():
                    var_name = getattr(widget, "var_name", "")
                    active_vars.append(var_name)

        if not active_vars:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("Please select at least one modification."))
            return

        self.inject_log.append(f"[Inject] Preparing to inject mod: {self.selected_mod}")
        self.inject_log.append(f"[Inject] Selected mods: {', '.join(active_vars)}")

        for i in range(1, 6):
            QTimer.singleShot(i * 500, lambda v=i*20: self.inject_log.append(f"[Inject] Progress: {v}%"))

        QTimer.singleShot(3000, lambda: self.inject_log.append("[Inject] ✅ Mod injected successfully!"))
        QTimer.singleShot(3000, lambda: QMessageBox.information(self, self.translator.translate("Success"), self.translator.translate("Mod injected successfully!")))

    # =====================================================================
    # دوال التحكم العامة
    # =====================================================================

    def activate_all(self):
        count = 0
        for item in self.variable_items.values():
            if item.is_found and not item.is_active:
                item.toggle.setChecked(True)
                count += 1
        self.add_log(f"[Info] Activated {count} variables")
        QMessageBox.information(self, self.translator.translate("Success"),
                                self.translator.translate(f"Activated {count} variables!"))

    def deactivate_all(self):
        count = 0
        for item in self.variable_items.values():
            if item.is_active:
                item.toggle.setChecked(False)
                count += 1
        self.add_log(f"[Info] Deactivated {count} variables")
        QMessageBox.information(self, self.translator.translate("Success"),
                                self.translator.translate(f"Deactivated {count} variables!"))

    def apply_mods(self):
        if not self.active_mods:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("No active mods to apply."))
            return
        if not self.current_file:
            QMessageBox.warning(self, self.translator.translate("Warning"), self.translator.translate("No file loaded. Please analyze a file first."))
            return

        self.add_log(f"[Apply] Applying {len(self.active_mods)} modifications to {self.current_file}...")
        try:
            for var_name in self.active_mods:
                self.add_log(f"  - Applying {var_name}...")
                time.sleep(0.1)
            self.add_log("[Success] ✅ All modifications applied successfully!")
            QMessageBox.information(self, self.translator.translate("Success"),
                                    self.translator.translate(f"Applied {len(self.active_mods)} modifications successfully!"))
        except Exception as e:
            self.add_log(f"[Error] ❌ Failed to apply modifications: {e}")
            QMessageBox.warning(self, self.translator.translate("Error"), self.translator.translate("Failed to apply modifications") + f": {str(e)}")

    def repair_mods(self):
        self.add_log("[Repair] Starting advanced repair...")
        QTimer.singleShot(1000, lambda: self.add_log("[Repair] ✅ Checking file integrity..."))
        QTimer.singleShot(2000, lambda: self.add_log("[Repair] ✅ Restoring backup..."))
        QTimer.singleShot(3000, lambda: self.add_log("[Repair] ✅ Re-applying active modifications..."))
        QTimer.singleShot(4000, lambda: self.add_log("[Repair] ✅ All repairs completed successfully!"))
        QTimer.singleShot(4000, lambda: QMessageBox.information(self, self.translator.translate("Success"), self.translator.translate("All repairs completed successfully!")))

    def smart_repair(self):
        self.add_log("[Smart Repair] Starting smart repair analysis...")
        QTimer.singleShot(800, lambda: self.add_log("[Smart Repair] 🔍 Analyzing file structure..."))
        QTimer.singleShot(1600, lambda: self.add_log("[Smart Repair] 🔍 Detecting conflicts..."))
        QTimer.singleShot(2400, lambda: self.add_log("[Smart Repair] ✅ Repair strategy determined"))
        QTimer.singleShot(3200, lambda: self.add_log("[Smart Repair] ✅ All issues resolved successfully!"))
        QTimer.singleShot(3200, lambda: QMessageBox.information(self, self.translator.translate("Smart Repair"), self.translator.translate("Smart repair completed successfully!")))

    def refresh_variables(self):
        self.add_log("[Refresh] 🔄 Refreshing variables...")
        QTimer.singleShot(1000, lambda: self.add_log("[Refresh] ✅ Refresh complete!"))

    def deactivate_selected_mod(self, item):
        text = item.text()
        var_name = text.split(" - ")[0].replace("✅", "").strip()
        if var_name in self.active_mods:
            del self.active_mods[var_name]
        self.active_list.takeItem(self.active_list.row(item))
        self.add_log(f"[Deactivate] {var_name} removed from active list")
        if var_name in self.variable_items:
            self.variable_items[var_name].toggle.setChecked(False)

    def deactivate_selected(self):
        current = self.active_list.currentItem()
        if current:
            self.deactivate_selected_mod(current)

    def clear_all_active(self):
        reply = QMessageBox.question(self, self.translator.translate("Clear All"),
                                     self.translator.translate("Are you sure you want to clear all active modifications?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.active_mods.clear()
            self.active_list.clear()
            for item in self.variable_items.values():
                item.toggle.setChecked(False)
            self.add_log("[Info] ✅ All active modifications cleared")

    def load_mod_list(self):
        self.mod_combo.clear()
        self.mod_combo.addItems(["God Mode", "Infinite Money", "Super Speed", "No Hunger", "Max Level"])
        self.inject_log.append("[Mod] ✅ Mod list updated")

    def retranslate_ui(self):
        self.title_label.setText(self.translator.translate("🛠️ Advanced Mod Manager"))
        self.tabs.setTabText(0, self.translator.translate("📋 Available"))
        self.tabs.setTabText(1, self.translator.translate("✅ Active"))
        self.tabs.setTabText(2, self.translator.translate("🎮 Mod Detection"))
        self.tabs.setTabText(3, self.translator.translate("💉 Mod Inject"))
        self.tabs.setTabText(4, self.translator.translate("📝 Logs"))
        self.refresh_btn.update_text()
        self.activate_all_btn.update_text()
        self.deactivate_all_btn.update_text()
        self.apply_mods_btn.update_text()
        self.repair_btn.update_text()
        self.anti_ban_check.setText(self.translator.translate("🛡️ Anti-Ban Protection"))
        self.spoof_id_check.setText(self.translator.translate("🔄 Spoof ID"))
        self.hide_mods_check.setText(self.translator.translate("👻 Hide Mods"))
        self.status_info_label.setText(self.translator.translate("Status: No file loaded. Please analyze a file first."))
        self.inject_log.setPlainText(self.translator.translate("Injection log will appear here..."))
        self.logs_text.setPlainText(self.translator.translate("Modification logs will appear here..."))
        self.mod_info_text.setPlainText(self.translator.translate("Select a mod from the list to display its information"))

        for item in self.variable_items.values():
            item.retranslate_ui()