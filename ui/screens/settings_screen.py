"""
شاشة الإعدادات - النسخة المحسنة
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QCheckBox, QSpinBox,
    QSlider, QFontComboBox, QMessageBox,
    QTabWidget, QFileDialog, QLineEdit, QPushButton,
    QApplication
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
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
        
        self.title_label = QLabel("⚙️ Settings")
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
        self.tabs.addTab(general_tab, "🌐 General")
        
        # تبويب المظهر
        appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(appearance_tab, "🎨 Appearance")
        
        # تبويب الخلفية
        background_tab = self.create_background_tab()
        self.tabs.addTab(background_tab, "🖼️ Background")
        
        # تبويب الخطوط
        fonts_tab = self.create_fonts_tab()
        self.tabs.addTab(fonts_tab, "🔤 Fonts")
        
        layout.addWidget(self.tabs)
        
        self.save_btn = ProokSuccessButton("💾 Save Settings")
        self.save_btn.setFixedHeight(40)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
    
    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        lang_group = QGroupBox("Language")
        lang_layout = QHBoxLayout(lang_group)
        lang_label = QLabel("Select Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.translator.available_languages or ["en", "ar"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addWidget(lang_group)
        
        file_group = QGroupBox("File Settings")
        file_layout = QVBoxLayout(file_group)
        size_layout = QHBoxLayout()
        size_label = QLabel("Maximum File Size (MB):")
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(10, 1000)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.max_size_spin)
        size_layout.addStretch()
        file_layout.addLayout(size_layout)
        self.auto_backup = QCheckBox("Enable Automatic Backup")
        file_layout.addWidget(self.auto_backup)
        layout.addWidget(file_group)
        
        layout.addStretch()
        return widget
    
    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout(theme_group)
        theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return widget
    
    def create_background_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        bg_group = QGroupBox("Background Settings")
        bg_layout = QVBoxLayout(bg_group)
        
        self.bg_enabled = QCheckBox("Enable Custom Background")
        bg_layout.addWidget(self.bg_enabled)
        
        type_layout = QHBoxLayout()
        type_label = QLabel("Background Type:")
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Image", "GIF", "Video"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.bg_type_combo)
        type_layout.addStretch()
        bg_layout.addLayout(type_layout)
        
        file_layout = QHBoxLayout()
        self.bg_file_input = QLineEdit()
        self.bg_file_input.setPlaceholderText("Choose background file...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_background)
        file_layout.addWidget(self.bg_file_input)
        file_layout.addWidget(browse_btn)
        bg_layout.addLayout(file_layout)
        
        self.bg_auto = QCheckBox("Auto-adjust to window size")
        self.bg_auto.setChecked(True)
        bg_layout.addWidget(self.bg_auto)
        
        layout.addWidget(bg_group)
        layout.addStretch()
        return widget
    
    def create_fonts_tab(self):
        """تبويب التحكم بحجم الخط عالمياً"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        font_group = QGroupBox("Global Font Size")
        font_layout = QVBoxLayout(font_group)
        
        # شرح
        desc_label = QLabel("Change the font size for all UI elements")
        desc_label.setStyleSheet(f"color: {self.color_system.palette.text_secondary}; font-size: 13px;")
        font_layout.addWidget(desc_label)
        
        # شريط التحكم بالحجم
        size_layout = QHBoxLayout()
        size_label = QLabel("Font Size:")
        self.global_font_slider = QSlider(Qt.Orientation.Horizontal)
        self.global_font_slider.setRange(8, 24)
        self.global_font_slider.setValue(12)
        self.global_font_slider.setTickInterval(2)
        self.global_font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.global_font_label = QLabel("12")
        self.global_font_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {self.color_system.palette.primary};")
        
        self.global_font_slider.valueChanged.connect(self.on_font_size_changed)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.global_font_slider)
        size_layout.addWidget(self.global_font_label)
        font_layout.addLayout(size_layout)
        
        # أزرار سريعة
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        small_btn = ProokButton("Small", "")
        small_btn.setFixedHeight(30)
        small_btn.clicked.connect(lambda: self.global_font_slider.setValue(10))
        btn_layout.addWidget(small_btn)
        
        medium_btn = ProokButton("Medium", "")
        medium_btn.setFixedHeight(30)
        medium_btn.clicked.connect(lambda: self.global_font_slider.setValue(12))
        btn_layout.addWidget(medium_btn)
        
        large_btn = ProokButton("Large", "")
        large_btn.setFixedHeight(30)
        large_btn.clicked.connect(lambda: self.global_font_slider.setValue(16))
        btn_layout.addWidget(large_btn)
        
        xlarge_btn = ProokButton("Extra Large", "")
        xlarge_btn.setFixedHeight(30)
        xlarge_btn.clicked.connect(lambda: self.global_font_slider.setValue(20))
        btn_layout.addWidget(xlarge_btn)
        
        btn_layout.addStretch()
        font_layout.addLayout(btn_layout)
        
        # معاينة
        preview_label = QLabel("Preview Text: This is an example of the new font size")
        preview_label.setStyleSheet(f"color: {self.color_system.palette.text_primary}; padding: 10px; background: {self.color_system.palette.surface_raised}; border-radius: 6px;")
        font_layout.addWidget(preview_label)
        
        self.preview_label = preview_label
        
        layout.addWidget(font_group)
        
        # نوع الخط
        font_family_group = QGroupBox("Font Family")
        font_family_layout = QHBoxLayout(font_family_group)
        family_label = QLabel("Select Font Family:")
        self.font_family_combo = QFontComboBox()
        font_family_layout.addWidget(family_label)
        font_family_layout.addWidget(self.font_family_combo)
        font_family_layout.addStretch()
        layout.addWidget(font_family_group)
        
        layout.addStretch()
        return widget
    
    def on_font_size_changed(self, value: int):
        """تطبيق حجم الخط الجديد فوراً"""
        self.global_font_label.setText(str(value))
        # تحديث المعاينة
        font = self.font_family_combo.currentFont()
        font.setPointSize(value)
        self.preview_label.setFont(font)
        # تطبيق على التطبيق بأكمله
        app = QApplication.instance()
        if app:
            default_font = app.font()
            default_font.setPointSize(value)
            app.setFont(default_font)
    
    def browse_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Background",
            "", "Images (*.png *.jpg *.jpeg *.bmp);;GIF (*.gif);;Videos (*.mp4 *.avi *.mov)"
        )
        if file_path:
            self.bg_file_input.setText(file_path)
    
    def load_settings(self):
        try:
            self.lang_combo.setCurrentText(str(self.settings.value("language", "en")))
            self.theme_combo.setCurrentText(str(self.settings.value("theme", "Dark")))
            self.max_size_spin.setValue(int(self.settings.value("max_file_size", 500)))
            self.auto_backup.setChecked(str(self.settings.value("auto_backup", "true")) == "true")
            
            self.bg_enabled.setChecked(str(self.settings.value("bg_enabled", "false")) == "true")
            self.bg_type_combo.setCurrentText(str(self.settings.value("bg_type", "Image")))
            self.bg_file_input.setText(str(self.settings.value("bg_file", "")))
            self.bg_auto.setChecked(str(self.settings.value("bg_auto", "true")) == "true")
            
            # تحميل إعدادات الخط
            font_size = int(self.settings.value("global_font_size", 12))
            self.global_font_slider.setValue(font_size)
            self.global_font_label.setText(str(font_size))
            
            font_family = str(self.settings.value("global_font_family", "Segoe UI"))
            index = self.font_family_combo.findText(font_family)
            if index >= 0:
                self.font_family_combo.setCurrentIndex(index)
            
            # تطبيق الخط المحفوظ
            self.apply_font_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def apply_font_settings(self):
        """تطبيق إعدادات الخط على التطبيق"""
        app = QApplication.instance()
        if app:
            size = self.global_font_slider.value()
            family = self.font_family_combo.currentFont().family()
            font = QFont(family, size)
            app.setFont(font)
            self.preview_label.setFont(font)
    
    def save_settings(self):
        try:
            self.settings.setValue("language", self.lang_combo.currentText())
            self.settings.setValue("theme", self.theme_combo.currentText())
            self.settings.setValue("max_file_size", self.max_size_spin.value())
            self.settings.setValue("auto_backup", self.auto_backup.isChecked())
            
            self.settings.setValue("bg_enabled", self.bg_enabled.isChecked())
            self.settings.setValue("bg_type", self.bg_type_combo.currentText())
            self.settings.setValue("bg_file", self.bg_file_input.text())
            self.settings.setValue("bg_auto", self.bg_auto.isChecked())
            
            # حفظ إعدادات الخط
            self.settings.setValue("global_font_size", self.global_font_slider.value())
            self.settings.setValue("global_font_family", self.font_family_combo.currentFont().family())
            
            # تطبيق الخط
            self.apply_font_settings()
            
            # تطبيق التغييرات الأخرى
            self.translator.set_language(self.lang_combo.currentText())
            self.theme_manager.set_theme(self.theme_combo.currentText())
            
            QMessageBox.information(self, self.translator.translate("Success"),
                                    self.translator.translate("Settings saved successfully!"))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
    
    def retranslate_ui(self):
        self.title_label.setText(self.translator.translate("⚙️ Settings"))
        self.tabs.setTabText(0, self.translator.translate("🌐 General"))
        self.tabs.setTabText(1, self.translator.translate("🎨 Appearance"))
        self.tabs.setTabText(2, self.translator.translate("🖼️ Background"))
        self.tabs.setTabText(3, self.translator.translate("🔤 Fonts"))
        self.save_btn.update_text()
        self.translator.apply_to_widget(self)