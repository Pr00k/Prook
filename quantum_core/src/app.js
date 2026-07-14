// ══════════════════════════════════════════════
// QUANTUM CORE v1.0 - Frontend Logic
// ══════════════════════════════════════════════

const { invoke } = window.__TAURI__.core;

// ═══ STATE ═══
let currentApkPath = '';
let analysisResult = null;
let discoveredPatches = [];
let activePatches = new Set();

// ═══ HELP TEXTS ═══
const helpTexts = {
    analyzer: {
        title: '❓ تحليل APK',
        body: `📦 كيف يعمل تحليل APK؟

1️⃣ اختر ملف APK للعبة
2️⃣ يتم فك ضغطه وفحص كل الملفات
3️⃣ يبحث عن:
   • libil2cpp.so (ألعاب Unity)
   • libUE4.so (ألعاب Unreal)
   • global-metadata.dat
   • كل المكتبات الأصلية

4️⃣ يستخرج النصوص ويقارنها بمكتبة الأسماء الشاملة
5️⃣ يكتشف التعديلات الممكنة ويصنفها
6️⃣ يفك التشفير تلقائياً إن وُجد

💡 النتيجة: قائمة بالتعديلات الممكنة مع أسماء واضحة`
    },
    injector: {
        title: '❓ حقن المود منيو',
        body: `💉 كيف يعمل حقن المود منيو؟

1️⃣ يأخذ التعديلات المفعّلة من تبويب "تم كشفها"
2️⃣ يحقنها في APK المعدّل
3️⃣ المود منيو يحتوي على:
   • زر تفعيل/تعطيل لكل تعديل
   • خانة زيادة/نقصان للقيم
   • أيقونة ❓ لوصف كل تعديل

🛡️ الحماية المدمجة (تلقائية):
   • Anti-Detection: تمويه التعديلات
   • Anti-Ban: حماية من الحظر
   • Server Evasion: مراوغة السيرفر
   • ID Spoofing: هوية وهمية
   • Packet Obfuscation: تشفير الحزم

⚡ اعتراض السيرفر (تلقائي):
   • عند تفعيل تعديل → يُعترض الاتصال
   • يُعدّل البيانات قبل إرسالها للسيرفر
   • يُرسل بيانات مزيفة للحماية`
    },
    discovered: {
        title: '❓ التعديلات المكتشفة',
        body: `📋 التعديلات المكتشفة

هنا تظهر كل التعديلات التي اكتشفها المحلل:

• كل تعديل له اسم واضح (مثل: جواهر، صحة، هجوم)
• أيقونة ❓ صغيرة → اضغطها لوصف التعديل
• زر تفعيل/تعطيل → فعّل ما تريد
• خانة +/- → حدد قيمة الزيادة/النقصان

عند الضغط على "حفظ وتفعيل":
1. تُحقن التعديلات في المود منيو
2. يُفعّل اعتراض السيرفر تلقائياً
3. تُفعّل الحماية المتقدمة تلقائياً`
    }
};

// ═══ INIT ═══
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initAnalyzer();
    initInjector();
    initDiscovered();
    initSettings();
    initHelp();
    hideSplash();
});

function hideSplash() {
    setTimeout(() => {
        document.getElementById('splash').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
    }, 2000);
}

// ═══ TABS ═══
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });
}

// ═══ ANALYZER ═══
function initAnalyzer() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('apkFileInput');
    const btnAnalyze = document.getElementById('btnAnalyze');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', e => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    btnAnalyze.addEventListener('click', runAnalysis);
}

async function handleFile(file) {
    document.getElementById('fileInfo').classList.remove('hidden');
    document.getElementById('fileName').textContent = '📦 ' + file.name;
    document.getElementById('fileSize').textContent = formatSize(file.size);
    currentApkPath = file.path || file.name;
    document.getElementById('btnAnalyze').disabled = false;
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

async function runAnalysis() {
    const progress = document.getElementById('analysisProgress');
    const result = document.getElementById('analysisResult');
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');

    progress.classList.remove('hidden');
    result.classList.add('hidden');

    // Simulate progress
    let pct = 0;
    const interval = setInterval(() => {
        pct += Math.random() * 15;
        if (pct > 90) pct = 90;
        fill.style.width = pct + '%';
        text.textContent = pct < 30 ? 'فك ضغط APK...' :
                          pct < 60 ? 'فحص المكتبات...' :
                          pct < 80 ? 'تحليل النصوص...' : 'مطابقة الأسماء...';
    }, 300);

    try {
        analysisResult = await invoke('analyze_apk', { path: currentApkPath });
        
        clearInterval(interval);
        fill.style.width = '100%';
        text.textContent = '✅ اكتمل التحليل!';

        setTimeout(() => {
            progress.classList.add('hidden');
            showAnalysisResult(analysisResult);
        }, 500);
    } catch (e) {
        clearInterval(interval);
        progress.classList.add('hidden');
        showToast('❌ خطأ: ' + e, 'error');
    }
}

function showAnalysisResult(data) {
    const result = document.getElementById('analysisResult');
    result.classList.remove('hidden');

    document.getElementById('resPackage').textContent = data.package_name || 'غير معروف';
    document.getElementById('resEngine').textContent = data.engine_type || 'غير معروف';
    document.getElementById('resArch').textContent = data.architecture || 'غير معروف';
    document.getElementById('resPatches').textContent = (data.patches || []).length;

    // Show native libs
    const libList = document.getElementById('libList');
    libList.innerHTML = '';
    if (data.native_libs && data.native_libs.length > 0) {
        const title = document.createElement('div');
        title.className = 'lib-title';
        title.textContent = '📚 المكتبات الأصلية (' + data.native_libs.length + ')';
        libList.appendChild(title);
        
        data.native_libs.forEach(lib => {
            const item = document.createElement('div');
            item.className = 'lib-item';
            item.textContent = lib;
            libList.appendChild(item);
        });
    }

    // Store patches for discovered tab
    discoveredPatches = data.patches || [];
    updateDiscoveredTab();
    
    document.getElementById('discoveredBadge').textContent = discoveredPatches.length;
    document.getElementById('btnInject').disabled = discoveredPatches.length === 0;
    
    showToast('✅ تم اكتشاف ' + discoveredPatches.length + ' تعديل', 'success');
}

// ═══ INJECTOR ═══
function initInjector() {
    document.getElementById('btnInject').addEventListener('click', injectModMenu);
    document.getElementById('btnInstall').addEventListener('click', installModdedApk);
}

async function injectModMenu() {
    const activeList = discoveredPatches.filter(p => activePatches.has(p.name));
    if (activeList.length === 0) {
        showToast('⚠️ فعّل تعديلاً واحداً على الأقل', 'warning');
        return;
    }

    const progress = document.getElementById('injectProgress');
    const resultDiv = document.getElementById('injectResult');
    const fill = document.getElementById('injectProgressFill');
    const text = document.getElementById('injectProgressText');

    progress.classList.remove('hidden');
    resultDiv.classList.add('hidden');

    let pct = 0;
    const interval = setInterval(() => {
        pct += Math.random() * 12;
        if (pct > 95) pct = 95;
        fill.style.width = pct + '%';
        text.textContent = pct < 25 ? 'تحضير التعديلات...' :
                          pct < 50 ? 'حقن المود منيو...' :
                          pct < 75 ? 'تطبيق الحماية المتقدمة...' :
                          pct < 90 ? 'إعداد اعتراض السيرفر...' : 'توقيع APK...';
    }, 400);

    try {
        const outputPath = currentApkPath.replace('.apk', '_modded.apk');
        const success = await invoke('inject_mod_menu', {
            apkPath: currentApkPath,
            outputPath: outputPath,
            patches: activeList
        });

        clearInterval(interval);
        fill.style.width = '100%';
        text.textContent = '✅ تم الحقن!';

        setTimeout(() => {
            progress.classList.add('hidden');
            if (success) {
                resultDiv.classList.remove('hidden');
                showToast('✅ تم حقن المود منيو بنجاح!', 'success');
            } else {
                showToast('❌ فشل الحقن', 'error');
            }
        }, 500);
    } catch (e) {
        clearInterval(interval);
        progress.classList.add('hidden');
        showToast('❌ خطأ: ' + e, 'error');
    }
}

async function installModdedApk() {
    const outputPath = currentApkPath.replace('.apk', '_modded.apk');
    try {
        await invoke('install_apk', { path: outputPath });
        showToast('📲 جاري التثبيت...', 'success');
    } catch (e) {
        showToast('ثبّت APK يدوياً: ' + outputPath, 'info');
    }
}

// ═══ DISCOVERED ═══
function initDiscovered() {
    document.getElementById('categoryFilter').addEventListener('change', filterDiscovered);
    document.getElementById('searchFilter').addEventListener('input', filterDiscovered);
    document.getElementById('btnSelectAll').addEventListener('click', selectAll);
    document.getElementById('btnSavePatches').addEventListener('click', savePatches);
}

function updateDiscoveredTab() {
    const list = document.getElementById('discoveredList');
    const filter = document.getElementById('categoryFilter');
    
    // Update category filter
    const categories = new Set(discoveredPatches.map(p => p.category));
    filter.innerHTML = '<option value="all">الكل</option>';
    categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat;
        filter.appendChild(opt);
    });

    renderDiscoveredList(discoveredPatches);
}

function renderDiscoveredList(patches) {
    const list = document.getElementById('discoveredList');
    list.innerHTML = '';

    if (patches.length === 0) {
        list.innerHTML = `<div class="empty-state">
            <span class="empty-icon">📭</span>
            <p>لا توجد تعديلات</p>
        </div>`;
        return;
    }

    // Group by category
    const grouped = {};
    patches.forEach(p => {
        if (!grouped[p.category]) grouped[p.category] = [];
        grouped[p.category].push(p);
    });

    Object.entries(grouped).forEach(([category, items]) => {
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `<span class="cat-icon">${getCategoryIcon(category)}</span>
                           <span class="cat-name">${category}</span>
                           <span class="cat-count">${items.length}</span>`;
        list.appendChild(header);

        items.forEach(patch => {
            const item = document.createElement('div');
            item.className = 'patch-item' + (activePatches.has(patch.name) ? ' active' : '');
            item.dataset.name = patch.name;

            item.innerHTML = `
                <div class="patch-main">
                    <label class="toggle-switch">
                        <input type="checkbox" ${activePatches.has(patch.name) ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <div class="patch-info">
                        <span class="patch-name">${patch.display_name || patch.name}</span>
                        <span class="patch-detail">${patch.lib_name || ''} | ${patch.offset || ''}</span>
                    </div>
                    <button class="btn-help-small" data-patch="${patch.name}" title="وصف التعديل">❓</button>
                </div>
                <div class="patch-controls ${activePatches.has(patch.name) ? '' : 'hidden'}">
                    <button class="btn-adjust" data-action="decrease" data-patch="${patch.name}">➖</button>
                    <input type="number" class="adjust-input" value="${patch.value || 999999}" data-patch="${patch.name}">
                    <button class="btn-adjust" data-action="increase" data-patch="${patch.name}">➕</button>
                </div>
            `;

            // Toggle
            const toggle = item.querySelector('input[type="checkbox"]');
            toggle.addEventListener('change', () => {
                if (toggle.checked) {
                    activePatches.add(patch.name);
                    item.classList.add('active');
                    item.querySelector('.patch-controls').classList.remove('hidden');
                    // Auto server intercept
                    autoIntercept(patch);
                } else {
                    activePatches.delete(patch.name);
                    item.classList.remove('active');
                    item.querySelector('.patch-controls').classList.add('hidden');
                }
                updateSaveButton();
            });

            // Help button
            const helpBtn = item.querySelector('.btn-help-small');
            helpBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showPatchHelp(patch);
            });

            // Adjust buttons
            item.querySelectorAll('.btn-adjust').forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = item.querySelector('.adjust-input');
                    let val = parseInt(input.value) || 0;
                    if (btn.dataset.action === 'increase') val += 1000;
                    else val = Math.max(0, val - 1000);
                    input.value = val;
                });
            });

            list.appendChild(item);
        });
    });
}

function getCategoryIcon(cat) {
    const icons = {
        'هجوم': '⚔️', 'صحة': '❤️', 'دفاع': '🛡️', 'سرعة': '⚡',
        'عملات': '💰', 'جواهر': '💎', 'نقاط': '⭐', 'طاقة': '🔋',
        'مستوى': '📈', 'خبرة': '📚', 'ذخيرة': '🔫', 'سلاح': '🗡️',
        'إعلانات': '📺', 'مشتريات': '🛒', 'مفاتيح': '🔑', 'صناديق': '📦',
        'تذاكر': '🎫', 'مواد': '🧱', 'مستهلكات': '🧪', 'إحصائيات': '📊',
        'هاكات': '🔓', 'عام': '⚙️'
    };
    return icons[cat] || '📌';
}

function showPatchHelp(patch) {
    const modal = document.getElementById('helpModal');
    document.getElementById('helpTitle').textContent = '❓ ' + (patch.display_name || patch.name);
    document.getElementById('helpBody').innerHTML = `
        <div class="help-patch-info">
            <p><strong>الاسم:</strong> ${patch.name}</p>
            <p><strong>الاسم العربي:</strong> ${patch.display_name || patch.name}</p>
            <p><strong>التصنيف:</strong> ${patch.category}</p>
            <p><strong>المكتبة:</strong> ${patch.lib_name || 'غير محدد'}</p>
            <p><strong>الأوفست:</strong> ${patch.offset || 'تلقائي'}</p>
            <p><strong>الوصف:</strong> ${patch.description || 'تعديل على ' + (patch.display_name || patch.name)}</p>
            <hr>
            <p>💡 <strong>كيف يعمل:</strong></p>
            <p>عند تفعيل هذا التعديل:</p>
            <ul>
                <li>يتم حقن الكود في المود منيو</li>
                <li>يُفعّل اعتراض السيرفر تلقائياً</li>
                <li>تُفعّل الحماية المتقدمة تلقائياً</li>
                <li>يمكنك تعديل القيمة من داخل اللعبة</li>
            </ul>
            <p>🛡️ <strong>الحماية:</strong></p>
            <ul>
                <li>Anti-Detection: تمويه التعديل</li>
                <li>Server Evasion: مراوغة السيرفر</li>
                <li>ID Spoofing: هوية وهمية</li>
            </ul>
        </div>
    `;
    modal.classList.remove('hidden');
}

async function autoIntercept(patch) {
    // Auto server intercept when activating a patch
    try {
        if (analysisResult && analysisResult.package_name) {
            await invoke('ssl_unpin', { packageName: analysisResult.package_name });
            await invoke('setup_proxy', { port: 8080 });
        }
    } catch (e) {
        // Silent fail - intercept is best effort
    }
}

function filterDiscovered() {
    const cat = document.getElementById('categoryFilter').value;
    const search = document.getElementById('searchFilter').value.toLowerCase();
    
    let filtered = discoveredPatches;
    if (cat !== 'all') filtered = filtered.filter(p => p.category === cat);
    if (search) filtered = filtered.filter(p => 
        (p.name || '').toLowerCase().includes(search) ||
        (p.display_name || '').toLowerCase().includes(search) ||
        (p.category || '').toLowerCase().includes(search)
    );
    
    renderDiscoveredList(filtered);
}

function selectAll() {
    const allActive = discoveredPatches.every(p => activePatches.has(p.name));
    if (allActive) {
        activePatches.clear();
    } else {
        discoveredPatches.forEach(p => activePatches.add(p.name));
    }
    renderDiscoveredList(discoveredPatches);
    updateSaveButton();
}

function updateSaveButton() {
    const btn = document.getElementById('btnSavePatches');
    btn.disabled = activePatches.size === 0;
    btn.textContent = activePatches.size > 0 
        ? `💾 حفظ وتفعيل (${activePatches.size})` 
        : '💾 حفظ وتفعيل';
}

async function savePatches() {
    // Switch to injector tab and trigger injection
    document.querySelector('[data-tab="injector"]').click();
    showToast('✅ تم حفظ ' + activePatches.size + ' تعديل - اضغط حقن المنيو', 'success');
}

// ═══ HELP ═══
function initHelp() {
    document.querySelectorAll('[data-help]').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.dataset.help;
            const help = helpTexts[key];
            if (help) {
                document.getElementById('helpTitle').textContent = help.title;
                document.getElementById('helpBody').textContent = help.body;
                document.getElementById('helpModal').classList.remove('hidden');
            }
        });
    });

    document.getElementById('closeHelp').addEventListener('click', () => {
        document.getElementById('helpModal').classList.add('hidden');
    });

    document.getElementById('btnHelp').addEventListener('click', () => {
        document.getElementById('helpTitle').textContent = '❓ مساعدة عامة';
        document.getElementById('helpBody').innerHTML = `
            <h3>⚡ Quantum Core v1.0</h3>
            <p>منصة تحليل وتعديل الألعاب المتقدمة</p>
            <hr>
            <p><strong>🔍 تحليل APK:</strong> اختر ملف APK → تحليل شامل</p>
            <p><strong>📋 تم كشفها:</strong> التعديلات المكتشفة مع أسماء واضحة</p>
            <p><strong>💉 حقن المنيو:</strong> حقن التعديلات في APK معدّل</p>
            <hr>
            <p>🛡️ الحماية تعمل تلقائياً عند تفعيل أي تعديل</p>
            <p>🌐 اعتراض السيرفر يعمل تلقائياً عند التفعيل</p>
        `;
        document.getElementById('helpModal').classList.remove('hidden');
    });
}

// ═══ SETTINGS ═══
function initSettings() {
    const modal = document.getElementById('settingsModal');
    
    document.getElementById('btnSettings').addEventListener('click', () => modal.classList.remove('hidden'));
    document.getElementById('closeSettings').addEventListener('click', () => modal.classList.add('hidden'));
    
    // Color picker
    document.querySelectorAll('.color-opt').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.color-opt').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.documentElement.style.setProperty('--primary', btn.dataset.color);
        });
    });

    // Font
    document.getElementById('fontSelect').addEventListener('change', e => {
        document.body.style.fontFamily = e.target.value + ', sans-serif';
    });

    // Close modals on backdrop click
    document.querySelectorAll('.modal').forEach(m => {
        m.addEventListener('click', e => {
            if (e.target === m) m.classList.add('hidden');
        });
    });
}

// ═══ TOAST ═══
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}
