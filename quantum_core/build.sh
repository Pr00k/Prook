#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "⚡ Quantum Core v1.0 - Builder"
echo "═══════════════════════════════════"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

# Step 1: Install Rust
echo -e "${YELLOW}[1/5] فحص Rust...${NC}"
if ! command -v rustc &> /dev/null; then
    echo "تثبيت Rust..."
    pkg install -y rust
fi

# Step 2: Install Node.js
echo -e "${YELLOW}[2/5] فحص Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "تثبيت Node.js..."
    pkg install -y nodejs
fi

# Step 3: Install Tauri CLI
echo -e "${YELLOW}[3/5] تثبيت Tauri CLI...${NC}"
npm install -g @tauri-apps/cli 2>/dev/null || npm install @tauri-apps/cli

# Step 4: Install Android targets (if building for Android)
echo -e "${YELLOW}[4/5] إعداد Android targets...${NC}"
rustup target add aarch64-linux-android 2>/dev/null || true
rustup target add armv7-linux-androideabi 2>/dev/null || true

# Step 5: Build
echo -e "${YELLOW}[5/5] بناء المشروع...${NC}"
npx tauri build 2>&1 | tail -20

echo ""
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo -e "${GREEN}✅ تم البناء!${NC}"
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo ""
echo "APK في: src-tauri/target/release/bundle/apk/"
echo "لتشغيل وضع التطوير: npx tauri dev"
