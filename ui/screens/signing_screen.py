"""
شاشة الإعدادات - ترجمة كاملة إلى العربية
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QCheckBox, QSpinBox,
    QSlider, QFontComboBox, QMessageBox,
    QTabWidget, QFileDialog, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QSettings
from ui.widgets.buttons import ProokSuccessButton, ProokButton
from ui.design_system.colors import ColorSystem
from translations.translator import Translator
from ui.theme.theme_manager import ThemeManager


class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()
        self.settings = QSettings("ProokSuite", "ProokSuite")
        self.theme_manager = ThemeManager()
        
        self.setup_ui()
        self.load_settings()
        self.retranslate_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        self.title_label = QLabel("⚙️ الإعدادات")
        self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color_system.palette.text_primary};")
        layout.addWidget(self.title_label)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {self.color_system.palette.surface};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 16px;
            }}
            QTabBar::tab:selected {{
                background: {self.color_system.palette.primary};
                color: white;
            }}
        """)
        
        # تبويب عام
        general_tab = self.create_general_tab()
        self.tabs.addTab(general_tab, "🌐 عام")
        
        # تبويب المظهر
        appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(appearance_tab, "🎨 المظهر")
        
        # تبويب الخلفية
        background_tab = self.create_background_tab()
        self.tabs.addTab(background_tab, "🖼️ الخلفية")
        
        layout.addWidget(self.tabs)
        
        self.save_btn = ProokSuccessButton("💾 حفظ الإعدادات")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
    
    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        lang_group = QGroupBox("اللغة")
        lang_layout = QHBoxLayout(lang_group)
        lang_label = QLabel("اختر اللغة:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.translator.available_languages)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addWidget(lang_group)
        
        file_group = QGroupBox("إعدادات الملفات")
        file_layout = QVBoxLayout(file_group)
        size_layout = QHBoxLayout()
        size_label = QLabel("الحد الأقصى لحجم الملف (ميجابايت):")
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(10, 1000)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.max_size_spin)
        size_layout.addStretch()
        file_layout.addLayout(size_layout)
        self.auto_backup = QCheckBox("تفعيل النسخ الاحتياطي التلقائي")
        file_layout.addWidget(self.auto_backup)
        layout.addWidget(file_group)
        
        layout.addStretch()
        return widget
    
    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        theme_group = QGroupBox("السمة")
        theme_layout = QHBoxLayout(theme_group)
        theme_label = QLabel("اختر السمة:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["داكن", "فاتح", "تلقائي"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addWidget(theme_group)
        
        font_group = QGroupBox("الخطوط")
        font_layout = QVBoxLayout(font_group)
        family_layout = QHBoxLayout()
        family_label = QLabel("نوع الخط:")
        self.font_combo = QFontComboBox()
        family_layout.addWidget(family_label)
        family_layout.addWidget(self.font_combo)
        family_layout.addStretch()
        font_layout.addLayout(family_layout)
        
        size_layout = QHBoxLayout()
        size_label = QLabel("حجم الخط:")
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(8, 24)
        self.font_size_slider.setValue(12)
        self.font_size_label = QLabel("12")
        self.font_size_slider.valueChanged.connect(lambda v: self.font_size_label.setText(str(v)))
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.font_size_slider)
        size_layout.addWidget(self.font_size_label)
        font_layout.addLayout(size_layout)
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
    
    def create_background_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        bg_group = QGroupBox("إعدادات الخلفية")
        bg_layout = QVBoxLayout(bg_group)
        
        self.bg_enabled = QCheckBox("تفعيل الخلفية المخصصة")
        bg_layout.addWidget(self.bg_enabled)
        
        type_layout = QHBoxLayout()
        type_label = QLabel("نوع الخلفية:")
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["صورة", "GIF", "فيديو"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.bg_type_combo)
        type_layout.addStretch()
        bg_layout.addLayout(type_layout)
        
        file_layout = QHBoxLayout()
        self.bg_file_input = QLineEdit()
        self.bg_file_input.setPlaceholderText("اختر ملف الخلفية...")
        browse_btn = QPushButton("تصفح...")
        browse_btn.clicked.connect(self.browse_background)
        file_layout.addWidget(self.bg_file_input)
        file_layout.addWidget(browse_btn)
        bg_layout.addLayout(file_layout)
        
        self.bg_auto = QCheckBox("ضبط تلقائي حسب حجم النافذة")
        self.bg_auto.setChecked(True)
        bg_layout.addWidget(self.bg_auto)
        
        layout.addWidget(bg_group)
        layout.addStretch()
        return widget
    
    def browse_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر الخلفية",
            "", "Images (*.png *.jpg *.jpeg *.bmp);;GIF (*.gif);;Videos (*.mp4 *.avi *.mov)"
        )
        if file_path:
            self.bg_file_input.setText(file_path)
    
    def load_settings(self):
        self.lang_combo.setCurrentText(self.settings.value("language", "en"))
        self.theme_combo.setCurrentText(self.settings.value("theme", "dark"))
        self.max_size_spin.setValue(int(self.settings.value("max_file_size", 500)))
        self.auto_backup.setChecked(self.settings.value("auto_backup", "true") == "true")
        self.font_size_slider.setValue(int(self.settings.value("font_size", 12)))
        self.font_size_label.setText(str(self.font_size_slider.value()))
        
        self.bg_enabled.setChecked(self.settings.value("bg_enabled", "false") == "true")
        self.bg_type_combo.setCurrentText(self.settings.value("bg_type", "Image"))
        self.bg_file_input.setText(self.settings.value("bg_file", ""))
        self.bg_auto.setChecked(self.settings.value("bg_auto", "true") == "true")
    
    def save_settings(self):
        self.settings.setValue("language", self.lang_combo.currentText())
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("max_file_size", self.max_size_spin.value())
        self.settings.setValue("auto_backup", self.auto_backup.isChecked())
        self.settings.setValue("font_size", self.font_size_slider.value())
        
        self.settings.setValue("bg_enabled", self.bg_enabled.isChecked())
        self.settings.setValue("bg_type", self.bg_type_combo.currentText())
        self.settings.setValue("bg_file", self.bg_file_input.text())
        self.settings.setValue("bg_auto", self.bg_auto.isChecked())
        
        self.translator.set_language(self.lang_combo.currentText())
        self.theme_manager.set_theme(self.theme_combo.currentText())
        
        QMessageBox.information(self, self.translator.translate("نجاح"),
                                self.translator.translate("تم حفظ الإعدادات بنجاح!"))
    
    def retranslate_ui(self):
        self.title_label.setText(self.translator.translate("⚙️ الإعدادات"))
        self.tabs.setTabText(0, self.translator.translate("عام"))
        self.tabs.setTabText(1, self.translator.translate("المظهر"))
        self.tabs.setTabText(2, self.translator.translate("الخلفية"))
        self.save_btn.update_text()
        self.translator.apply_to_widget(self)