# ⚡ Quantum Core v1.0

## منصة تحليل وتعديل الألعاب المتقدمة

### البنية
```
quantum_core/
├── src-tauri/              ← Rust Backend
│   ├── src/
│   │   ├── main.rs         ← المحركات + Tauri Commands
│   │   └── libraries.rs    ← مكتبة الأسماء الشاملة
│   ├── Cargo.toml
│   └── tauri.conf.json
├── src/                    ← Frontend (HTML/CSS/JS)
│   ├── index.html          ← الواجهة الرئيسية
│   ├── styles.css          ← التصميم الداكن
│   └── app.js              ← المنطق
├── package.json
├── build.sh                ← سكريبت البناء (Termux)
└── README.md
```

### المكتبات المدمجة
| المكتبة | المحتوى |
|---------|---------|
| 📛 أسماء | 200+ اسم (مفاتيح، صناديق، عملات، تذاكر، مواد، إحصائيات، هاكات) |
| 📍 أوفستات | IL2CPP, UE4, Cocos2d, Generic |
| 💰 قيم | معروفة + مشفرة + أنماط |

### الحماية المتقدمة (تلقائية)
- Anti-Detection
- Anti-Ban
- Server Evasion
- ID Spoofing
- Packet Obfuscation

### البناء

#### Termux (Android)
```bash
cd quantum_core
chmod +x build.sh
./build.sh
```

#### PC
```bash
npm install
npx tauri build
```
