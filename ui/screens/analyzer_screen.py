"""
شاشة التحليل المتطورة - مع معالجة الأخطاء
"""

import os
import json
import time
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QProgressBar, QGroupBox,
    QMessageBox, QFileDialog, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPalette

from ui.widgets.buttons import ProokButton, ProokSuccessButton, ProokDangerButton
from ui.widgets.drop_zone import DropZone
from ui.design_system.colors import ColorSystem
from ui.design_system.typography import TypographySystem
from translations.translator import Translator
from core.analysis_engine import AnalysisEngine
from infrastructure.file_system import FileSystem
from infrastructure.logger import app_logger


class AnalysisThread(QThread):
    """خيط التحليل المتقدم مع تقدم حقيقي"""
    progress = pyqtSignal(int, str)
    step = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.engine = AnalysisEngine()

    def run(self):
        try:
            self.progress.emit(10, "📂 قراءة الملف وتحليل البنية...")
            self.step.emit(1, "📂 قراءة الملف وتحليل البنية")
            
            self.progress.emit(30, "🔍 تحليل الملف...")
            self.step.emit(2, "🔍 تحليل الملف")
            
            results = self.engine.analyze_file(self.file_path)
            
            self.progress.emit(60, "📊 معالجة النتائج...")
            self.step.emit(3, "📊 معالجة النتائج")
            
            self.progress.emit(90, "📝 تجميع البيانات...")
            self.step.emit(4, "📝 تجميع البيانات")
            
            self.progress.emit(100, "✅ اكتمل التحليل")
            self.step.emit(5, "✅ اكتمل التحليل")
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))


class AnalyzerScreen(QWidget):
    """شاشة التحليل المتطورة"""

    analysis_completed = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.color_system = ColorSystem()
        self.analysis_engine = AnalysisEngine()
        self.current_file = None
        self.analysis_results = None
        self.is_analyzing = False

        self.setup_ui()
        self.retranslate_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        # العنوان
        title_layout = QHBoxLayout()
        self.title_label = QLabel("🔍 محلل الملفات المتقدم")
        self.title_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {self.color_system.palette.text_primary};")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # منطقة اختيار الملف
        file_group = QGroupBox("اختيار الملف")
        file_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {self.color_system.palette.border};
                border-radius: 10px;
                padding-top: 18px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px;
                color: {self.color_system.palette.text_secondary};
                font-weight: bold;
            }}
        """)
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(12)
        self.drop_zone = DropZone(self)
        self.drop_zone.file_dropped.connect(self.on_file_dropped)
        file_layout.addWidget(self.drop_zone)

        browse_layout = QHBoxLayout()
        browse_btn = ProokButton("تصفح الملف", "📂")
        browse_btn.setFixedHeight(40)
        browse_btn.clicked.connect(self.browse_file)
        browse_layout.addStretch()
        browse_layout.addWidget(browse_btn)
        file_layout.addLayout(browse_layout)
        layout.addWidget(file_group)

        # شريط التقدم
        progress_container = QWidget()
        progress_container.setStyleSheet(f"""
            QWidget {{
                background: {self.color_system.palette.surface_raised};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 8px;
                background: {self.color_system.palette.surface};
                height: 28px;
                font-weight: bold;
                font-size: 13px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.5 #8b5cf6, stop:1 #ec4899);
                border-radius: 8px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("جاهز")
        self.progress_label.setStyleSheet(f"""
            color: {self.color_system.palette.text_secondary};
            font-size: 13px;
            font-weight: 500;
            padding: 4px 0;
        """)
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_container)

        # زر التحليل
        self.analyze_btn = ProokButton("🔍 بدء التحليل الكامل", "🔍")
        self.analyze_btn.setFixedHeight(50)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #7c3aed);
            }
            QPushButton:disabled {
                background: #555566;
            }
        """)
        layout.addWidget(self.analyze_btn)

        # نتائج التحليل
        results_group = QGroupBox("نتائج التحليل")
        results_group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {self.color_system.palette.border};
                border-radius: 10px;
                padding-top: 18px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px;
                color: {self.color_system.palette.text_secondary};
                font-weight: bold;
            }}
        """)
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(f"""
            QTextEdit {{
                background: {self.color_system.palette.surface_raised};
                border: 1px solid {self.color_system.palette.border};
                border-radius: 8px;
                padding: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                min-height: 180px;
                line-height: 1.6;
            }}
        """)
        self.results_text.setText(self.translator.translate("اختر ملفاً وانقر على 'بدء التحليل الكامل'"))
        results_layout.addWidget(self.results_text)
        layout.addWidget(results_group)

    def on_file_dropped(self, file_path: str):
        self.current_file = file_path
        self.drop_zone.text_label.setText(f"📄 {os.path.basename(file_path)}")
        self.analyze_btn.setEnabled(True)
        self.results_text.clear()
        self.results_text.append(f"📄 تم اختيار الملف: {file_path}\n")
        self.results_text.append("انقر على 'بدء التحليل الكامل' للبدء...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        app_logger.info(f"File selected: {file_path}")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.translate("اختر ملفاً"),
            "",
            self.translator.translate("جميع الملفات (*.*)")
        )
        if file_path:
            self.on_file_dropped(file_path)

    def start_analysis(self):
        if not self.current_file:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار ملف أولاً.")
            return

        if self.is_analyzing:
            return

        self.is_analyzing = True
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("⏳ جاري التحليل...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("🚀 بدء التحليل...")
        self.results_text.clear()
        self.results_text.append(f"🔍 جاري تحليل: {self.current_file}\n")
        self.results_text.append("يرجى الانتظار...\n")

        # بدء خيط التحليل
        self.thread = AnalysisThread(self.current_file)
        self.thread.progress.connect(self.update_progress)
        self.thread.step.connect(self.update_step)
        self.thread.finished.connect(self.on_analysis_finished)
        self.thread.error.connect(self.on_analysis_error)
        self.thread.start()

    def update_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    def update_step(self, step_num: int, step_name: str):
        self.results_text.append(f"  ✅ {step_name}")

    def on_analysis_finished(self, results: dict):
        """معالج اكتمال التحليل"""
        self.is_analyzing = False
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 بدء التحليل الكامل")
        self.analysis_results = results

        # عرض النتائج
        self._display_results(results)

        # إرسال النتائج إلى التعديلات تلقائياً
        self._send_results_to_mods(results)

        # إرسال إشارة اكتمال التحليل
        self.analysis_completed.emit(self.current_file, results)

        app_logger.info(f"Analysis completed for {results.get('file_path', self.current_file)}")

    def _display_results(self, results: dict):
        """عرض النتائج بشكل منظم - مع معالجة المفاتيح المفقودة"""
        # ✅ استخدام .get() لتجنب KeyError
        text = "=" * 70 + "\n"
        text += "📊  اكتمل التحليل\n"
        text += "=" * 70 + "\n\n"

        text += f"📄  الملف: {results.get('file_path', 'غير معروف')}\n"
        text += f"📦  الحجم: {results.get('size', 0):,} بايت\n"
        text += f"📈  الإنتروبيا: {results.get('entropy', 0.0):.4f}\n"
        text += f"🔐  مشفر: {'✅ نعم' if results.get('is_encrypted', False) else '❌ لا'}\n"
        text += f"📦  مضغوط: {'✅ نعم' if results.get('is_compressed', False) else '❌ لا'}\n"
        text += f"📋  نوع الملف: {results.get('file_type', 'غير معروف')}\n"
        text += f"📋  صيغة الملف: {results.get('file_format', 'غير معروفة')}\n"
        text += f"🔑  MD5: {results.get('hash_md5', 'غير متاح')}\n"
        text += f"🔑  SHA256: {results.get('hash_sha256', 'غير متاح')[:32] if results.get('hash_sha256') else 'غير متاح'}...\n"
        text += f"📝  عدد النصوص: {results.get('all_strings_found', 0)}\n"
        text += f"⭐  درجة التحليل: {results.get('score', 0)}\n"
        text += f"🎮  محرك اللعبة: {results.get('game_engine', 'غير معروف')}\n\n"

        text += "-" * 70 + "\n"
        text += "🔍  المتغيرات المكتشفة\n"
        text += "-" * 70 + "\n"
        variables = results.get('variables', {})
        if variables:
            for var, values in list(variables.items())[:30]:
                text += f"  •  {var}: {', '.join(values[:3])}\n"
            if len(variables) > 30:
                text += f"  ... و {len(variables) - 30} متغيرات أخرى\n"
        else:
            text += "  ❌  لا توجد متغيرات مكتشفة\n"

        hacking_values = results.get('hacking_values', {})
        if hacking_values:
            text += "\n" + "-" * 70 + "\n"
            text += "💀  القيم التهكيرية المكتشفة\n"
            text += "-" * 70 + "\n"
            for name, values in list(hacking_values.items())[:15]:
                text += f"  •  {name}: {', '.join(values[:3])}\n"

        auto_mods = results.get('auto_memory_mods', [])
        if auto_mods:
            text += "\n" + "-" * 70 + "\n"
            text += "🔧  التعديلات المقترحة\n"
            text += "-" * 70 + "\n"
            for mod in auto_mods[:10]:
                text += f"  •  {mod.get('type', 'unknown')}: {mod.get('value', 'N/A')}\n"

        detected_mods = results.get('detected_mods', [])
        if detected_mods:
            text += "\n" + "-" * 70 + "\n"
            text += "🎯  المودات المكتشفة\n"
            text += "-" * 70 + "\n"
            for mod in detected_mods[:10]:
                text += f"  •  {mod}\n"

        # معلومات APK
        apk_info = results.get('apk_info', {})
        if apk_info:
            text += "\n" + "-" * 70 + "\n"
            text += "📱  معلومات APK\n"
            text += "-" * 70 + "\n"
            if apk_info.get('package_name'):
                text += f"  •  الحزمة: {apk_info.get('package_name')}\n"
            if apk_info.get('version_name'):
                text += f"  •  الإصدار: {apk_info.get('version_name')}\n"
            if apk_info.get('permissions'):
                text += f"  •  الأذونات: {', '.join(apk_info.get('permissions', [])[:5])}\n"

        # معلومات IPA
        ipa_info = results.get('ipa_info', {})
        if ipa_info:
            text += "\n" + "-" * 70 + "\n"
            text += "🍎  معلومات IPA\n"
            text += "-" * 70 + "\n"
            if ipa_info.get('bundle_id'):
                text += f"  •  Bundle ID: {ipa_info.get('bundle_id')}\n"
            if ipa_info.get('version'):
                text += f"  •  الإصدار: {ipa_info.get('version')}\n"
            if ipa_info.get('name'):
                text += f"  •  الاسم: {ipa_info.get('name')}\n"

        if results.get('error'):
            text += "\n" + "-" * 70 + "\n"
            text += f"⚠️  خطأ أثناء التحليل: {results.get('error')}\n"
            text += "-" * 70 + "\n"

        text += "\n" + "-" * 70 + "\n"
        text += "✅  تم إرسال النتائج إلى شاشة التعديلات تلقائياً!\n"
        text += "-" * 70 + "\n"

        self.results_text.append(text)

    def _send_results_to_mods(self, results: dict):
        """إرسال النتائج إلى شاشة التعديلات"""
        mods_screen = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'mods_screen'):
                mods_screen = parent.mods_screen
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None

        if mods_screen and hasattr(mods_screen, 'set_analysis_results'):
            found_values = {}
            for var, values in results.get('variables', {}).items():
                if values:
                    found_values[var] = values[0]
                else:
                    found_values[var] = "0"
            for name, values in results.get('hacking_values', {}).items():
                if values:
                    found_values[f"Hack_{name}"] = values[0]
                else:
                    found_values[f"Hack_{name}"] = "0"
            for mod in results.get('auto_memory_mods', []):
                mod_type = mod.get('type', 'unknown')
                mod_value = mod.get('value', '0')
                found_values[f"Mod_{mod_type}"] = mod_value

            mods_screen.set_analysis_results(self.current_file, found_values)
            self.results_text.append("\n✅ تم إرسال النتائج إلى شاشة التعديلات تلقائياً!\n")
        else:
            self.results_text.append("\n⚠️ لم يتم العثور على شاشة التعديلات\n")

    def on_analysis_error(self, error: str):
        self.is_analyzing = False
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 بدء التحليل الكامل")
        self.results_text.setText(f"❌ خطأ أثناء التحليل: {error}")
        app_logger.error(f"Analysis error: {error}")

    def retranslate_ui(self):
        self.title_label.setText(self.translator.translate("🔍 محلل الملفات المتقدم"))
        self.analyze_btn.update_text()
        self.drop_zone.update_text()
        if not self.analysis_results:
            self.results_text.setText(self.translator.translate("اختر ملفاً وانقر على 'بدء التحليل الكامل'"))