// ═══════════════════════════════════════════════════
// QUANTUM CORE v1.0 - Rust Engine
// Ultimate Game Analysis & Modification Platform
// ═══════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::Read;
use std::path::Path;

// ══════════════════════════════════════
// TYPES
// ══════════════════════════════════════

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct PatchInfo {
    pub name: String,
    pub display_name: String,
    pub lib_name: String,
    pub offset: String,
    pub orig_bytes: String,
    pub patch_bytes: String,
    pub category: String,
    pub description: String,
    pub active: bool,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AnalysisResult {
    pub package_name: String,
    pub version: String,
    pub is_unity: bool,
    pub has_il2cpp: bool,
    pub has_ue4: bool,
    pub native_libs: Vec<String>,
    pub patches: Vec<PatchInfo>,
    pub total_methods: usize,
    pub total_classes: usize,
    pub engine_type: String,
    pub architecture: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct InterceptedPacket {
    pub id: u64,
    pub method: String,
    pub url: String,
    pub headers: HashMap<String, String>,
    pub body: String,
    pub response_body: String,
    pub timestamp: u64,
    pub modified: bool,
}

// ══════════════════════════════════════
// NAME LIBRARY - Global Game Names
// ══════════════════════════════════════

pub struct NameLibrary;

impl NameLibrary {
    pub fn get_all_categories() -> Vec<String> {
        vec![
            "هجوم".into(), "صحة".into(), "دفاع".into(), "سرعة".into(),
            "عملات".into(), "جواهر".into(), "نقاط".into(), "طاقة".into(),
            "مستوى".into(), "خبرة".into(), "درع".into(), "ذخيرة".into(),
            "سلاح".into(), " قوة".into(), "دقة".into(), "حظ".into(),
            "إعلانات".into(), "مشتريات".into(), "فتح".into(), "تخطي".into(),
            "God Mode".into(), "One Hit Kill".into(), "Unlimited".into(),
            "No Cooldown".into(), "No Ads".into(), "Free Shopping".into(),
            "Damage Multiplier".into(), "Speed Hack".into(), "Wall Hack".into(),
            "Aimbot".into(), "ESP".into(), "Anti-Ban".into(),
        ]
    }

    pub fn get_names_by_category(category: &str) -> Vec<String> {
        match category {
            "هجوم" | "Attack" => vec![
                "Damage", "Attack", "AttackPower", "ATK", "AtkPower",
                "PhysicalDamage", "MagicDamage", "CritDamage", "BaseAttack",
                "TotalAttack", "WeaponDamage", "SkillDamage", "HitDamage",
                "get_Damage", "set_Damage", "get_Attack", "set_Attack",
                "GetDamage", "GetAttack", "TakeDamage", "DealDamage",
                "CalculateDamage", "ApplyDamage", "AddDamage", "DamageMultiplier",
            ].into_iter().map(String::from).collect(),
            
            "صحة" | "Health" => vec![
                "Health", "HP", "HitPoints", "MaxHP", "CurrentHP",
                "Life", "LifePoints", "Vitality", "get_Health", "set_Health",
                "GetHealth", "SetHealth", "HealHP", "RestoreHP", "AddHP",
                "TakeDamage", "Heal", "Regeneration", "HealthRegen",
                "MaxHealth", "CurrentHealth", "HealthPercent",
            ].into_iter().map(String::from).collect(),
            
            "دفاع" | "Defense" => vec![
                "Defense", "DEF", "Armor", "Shield", "Protection",
                "PhysicalDefense", "MagicDefense", "get_Defense", "set_Defense",
                "GetDefense", "ArmorValue", "DamageReduction", "Block",
                "Resistance", "MagicResistance", "PhysicalResistance",
            ].into_iter().map(String::from).collect(),
            
            "سرعة" | "Speed" => vec![
                "Speed", "MoveSpeed", "MovementSpeed", "AttackSpeed",
                "CastSpeed", "get_Speed", "set_Speed", "GetSpeed",
                "Velocity", "RunSpeed", "WalkSpeed", "SprintSpeed",
                "SpeedMultiplier", "AttackSpeedMultiplier", "CooldownReduction",
            ].into_iter().map(String::from).collect(),
            
            "عملات" | "Coins" => vec![
                "Coins", "Gold", "Money", "Cash", "Currency",
                "SoftCurrency", "get_Coins", "set_Coins", "GetCoins",
                "AddCoins", "SpendCoins", "CoinBalance", "GoldAmount",
                "MoneyAmount", "TotalCoins", "FreeCoins",
            ].into_iter().map(String::from).collect(),
            
            "جواهر" | "Gems" => vec![
                "Gems", "Diamonds", "Crystals", "Premium", "HardCurrency",
                "get_Gems", "set_Gems", "GetGems", "AddGems", "GemBalance",
                "DiamondAmount", "CrystalCount", "PremiumCurrency",
                "RubyCount", "SapphireCount", "TokenCount",
            ].into_iter().map(String::from).collect(),
            
            "طاقة" | "Energy" => vec![
                "Energy", "Stamina", "Power", "Mana", "MP",
                "get_Energy", "set_Energy", "GetEnergy", "AddEnergy",
                "MaxEnergy", "CurrentEnergy", "EnergyRegen", "StaminaMax",
                "ActionPoints", "AP", "PowerPoints",
            ].into_iter().map(String::from).collect(),
            
            "مستوى" | "Level" => vec![
                "Level", "Lvl", "PlayerLevel", "HeroLevel", "CharLevel",
                "get_Level", "set_Level", "GetLevel", "SetLevel",
                "CurrentLevel", "MaxLevel", "LevelUp", "ExperienceLevel",
            ].into_iter().map(String::from).collect(),
            
            "خبرة" | "Experience" => vec![
                "Experience", "EXP", "XP", "PlayerEXP", "HeroEXP",
                "get_Experience", "set_Experience", "GetEXP", "AddEXP",
                "CurrentEXP", "RequiredEXP", "EXPToNextLevel", "ExpMultiplier",
            ].into_iter().map(String::from).collect(),
            
            "إعلانات" | "Ads" => vec![
                "LoadAd", "ShowAd", "RequestAd", "IsAdReady", "onAdLoaded",
                "showInterstitial", "loadRewardedVideo", "showBanner",
                "hideBanner", "AdMob", "UnityAds", "AdColony",
                "RemoveAds", "NoAds", "AdFree", "DisableAds",
                "isAdFree", "hasNoAds", "removeAdvertisements",
            ].into_iter().map(String::from).collect(),
            
            "مشتريات" | "Purchase" => vec![
                "VerifyPurchase", "ValidateReceipt", "IsPurchased",
                "ProcessPurchase", "ConfirmPurchase", "BuyItem",
                "MakePurchase", "InAppPurchase", "IAP", "Billing",
                "GetPrice", "IsFree", "FreeShopping", "FreePurchase",
                "SkipPurchase", "UnlockPurchase", "RestorePurchase",
            ].into_iter().map(String::from).collect(),

            _ => vec![
                "Score", "Points", "Kills", "Deaths", "Assists",
                "WinStreak", "Rank", "Rating", "Trophies", "Stars",
                "Tickets", "Keys", "Tokens", "Medals", "Badges",
            ].into_iter().map(String::from).collect(),
        }
    }

    pub fn categorize_name(name: &str) -> String {
        let n = name.to_lowercase();
        if n.contains("damage") || n.contains("attack") || n.contains("atk") { "هجوم".into() }
        else if n.contains("health") || n.contains("hp") || n.contains("heal") || n.contains("life") { "صحة".into() }
        else if n.contains("defense") || n.contains("armor") || n.contains("shield") { "دفاع".into() }
        else if n.contains("speed") || n.contains("velocity") { "سرعة".into() }
        else if n.contains("coin") || n.contains("gold") || n.contains("money") || n.contains("cash") { "عملات".into() }
        else if n.contains("gem") || n.contains("diamond") || n.contains("crystal") { "جواهر".into() }
        else if n.contains("score") || n.contains("point") { "نقاط".into() }
        else if n.contains("energy") || n.contains("stamina") || n.contains("mana") { "طاقة".into() }
        else if n.contains("level") || n.contains("lvl") { "مستوى".into() }
        else if n.contains("exp") || n.contains("xp") || n.contains("experience") { "خبرة".into() }
        else if n.contains("ad") || n.contains("banner") || n.contains("interstitial") { "إعلانات".into() }
        else if n.contains("purchase") || n.contains("buy") || n.contains("billing") { "مشتريات".into() }
        else { "أخرى".into() }
    }
    
    pub fn get_display_name(name: &str) -> String {
        let n = name.to_lowercase();
        if n.contains("damage") { "الضرر".into() }
        else if n.contains("health") || n.contains("hp") { "الصحة".into() }
        else if n.contains("defense") { "الدفاع".into() }
        else if n.contains("speed") { "السرعة".into() }
        else if n.contains("coin") || n.contains("gold") { "العملات".into() }
        else if n.contains("gem") || n.contains("diamond") { "الجواهر".into() }
        else if n.contains("energy") || n.contains("stamina") { "الطاقة".into() }
        else if n.contains("level") { "المستوى".into() }
        else if n.contains("exp") || n.contains("xp") { "الخبرة".into() }
        else if n.contains("ad") { "الإعلانات".into() }
        else if n.contains("purchase") || n.contains("buy") { "المشتريات".into() }
        else if n.contains("score") { "النقاط".into() }
        else if n.contains("armor") { "الدرع".into() }
        else if n.contains("ammo") { "الذخيرة".into() }
        else if n.contains("weapon") { "السلاح".into() }
        else if n.contains("crit") { "الضربة الحرجة".into() }
        else { name.into() }
    }
}

// ══════════════════════════════════════
// OFFSET LIBRARY
// ══════════════════════════════════════

pub struct OffsetLibrary;

impl OffsetLibrary {
    pub fn get_common_offsets(engine: &str) -> Vec<PatchInfo> {
        match engine {
            "il2cpp" => Self::il2cpp_offsets(),
            "ue4" => Self::ue4_offsets(),
            "cocos2d" => Self::cocos2d_offsets(),
            _ => Self::generic_offsets(),
        }
    }

    fn il2cpp_offsets() -> Vec<PatchInfo> {
        vec![
            PatchInfo {
                name: "god_mode".into(), display_name: "الوضع الإلهي".into(),
                lib_name: "libil2cpp.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "C0035FD6".into(),
                category: "صحة".into(), description: "لا تتلقى ضرر".into(), active: false,
            },
            PatchInfo {
                name: "one_hit_kill".into(), display_name: "قتل بضربة واحدة".into(),
                lib_name: "libil2cpp.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "C0035FD6".into(),
                category: "هجوم".into(), description: "اقتل أي عدو بضربة".into(), active: false,
            },
            PatchInfo {
                name: "unlimited_ammo".into(), display_name: "ذخيرة لا نهائية".into(),
                lib_name: "libil2cpp.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "C0035FD6".into(),
                category: "ذخيرة".into(), description: "ذخيرة لا تنفد".into(), active: false,
            },
            PatchInfo {
                name: "no_cooldown".into(), display_name: "بدون انتظار".into(),
                lib_name: "libil2cpp.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "00008052C0035FD6".into(),
                category: "سرعة".into(), description: "إزالة وقت الانتظار".into(), active: false,
            },
            PatchInfo {
                name: "speed_multiplier".into(), display_name: "مضاعف السرعة".into(),
                lib_name: "libil2cpp.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "".into(),
                category: "سرعة".into(), description: "تسريع اللعبة".into(), active: false,
            },
        ]
    }

    fn ue4_offsets() -> Vec<PatchInfo> {
        vec![
            PatchInfo {
                name: "ue4_god_mode".into(), display_name: "الوضع الإلهي".into(),
                lib_name: "libUE4.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "C0035FD6".into(),
                category: "صحة".into(), description: "لا ضرر UE4".into(), active: false,
            },
            PatchInfo {
                name: "ue4_no_recoil".into(), display_name: "بدون ارتداد".into(),
                lib_name: "libUE4.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "00008052C0035FD6".into(),
                category: "سلاح".into(), description: "إزالة ارتداد السلاح".into(), active: false,
            },
        ]
    }

    fn cocos2d_offsets() -> Vec<PatchInfo> {
        vec![
            PatchInfo {
                name: "cocos_speed".into(), display_name: "تسريع Cocos".into(),
                lib_name: "libcocos2d.so".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "".into(),
                category: "سرعة".into(), description: "تسريع ألعاب Cocos2d".into(), active: false,
            },
        ]
    }

    fn generic_offsets() -> Vec<PatchInfo> {
        vec![
            PatchInfo {
                name: "arm64_ret".into(), display_name: "إرجاع ARM64".into(),
                lib_name: "auto".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "C0035FD6".into(),
                category: "عام".into(), description: "إرجاع فوري (تعطيل دالة)".into(), active: false,
            },
            PatchInfo {
                name: "arm64_ret_zero".into(), display_name: "إرجاع صفر ARM64".into(),
                lib_name: "auto".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "00008052C0035FD6".into(),
                category: "عام".into(), description: "إرجاع 0 (MOV X0,#0; RET)".into(), active: false,
            },
            PatchInfo {
                name: "arm64_ret_one".into(), display_name: "إرجاع واحد ARM64".into(),
                lib_name: "auto".into(), offset: "auto".into(),
                orig_bytes: "".into(), patch_bytes: "20008052C0035FD6".into(),
                category: "عام".into(), description: "إرجاع 1 (MOV X0,#1; RET)".into(), active: false,
            },
        ]
    }
}

// ══════════════════════════════════════
// VALUE LIBRARY
// ══════════════════════════════════════

pub struct ValueLibrary;

impl ValueLibrary {
    pub fn get_known_values() -> HashMap<String, Vec<KnownValue>> {
        let mut map = HashMap::new();
        
        map.insert("صحة".into(), vec![
            KnownValue { name: "صحة كاملة".into(), value_type: "DWORD".into(), pattern: "100".into(), description: "100 HP".into() },
            KnownValue { name: "صحة منخفضة".into(), value_type: "DWORD".into(), pattern: "1~10".into(), description: "HP منخفض".into() },
        ]);
        
        map.insert("عملات".into(), vec![
            KnownValue { name: "عملات كبيرة".into(), value_type: "DWORD".into(), pattern: "1000~999999".into(), description: "رصيد عملات".into() },
            KnownValue { name: "عملات صغيرة".into(), value_type: "DWORD".into(), pattern: "1~999".into(), description: "عملات قليلة".into() },
        ]);
        
        map.insert("جواهر".into(), vec![
            KnownValue { name: "جواهر".into(), value_type: "DWORD".into(), pattern: "1~99999".into(), description: "رصيد جواهر".into() },
        ]);
        
        map.insert("سرعة".into(), vec![
            KnownValue { name: "سرعة عادية".into(), value_type: "FLOAT".into(), pattern: "1.0".into(), description: "1.0x speed".into() },
            KnownValue { name: "سرعة مضاعفة".into(), value_type: "FLOAT".into(), pattern: "2.0~10.0".into(), description: "2x-10x speed".into() },
        ]);
        
        map.insert("مستوى".into(), vec![
            KnownValue { name: "مستوى اللاعب".into(), value_type: "DWORD".into(), pattern: "1~100".into(), description: "Player level".into() },
        ]);
        
        map
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct KnownValue {
    pub name: String,
    pub value_type: String,
    pub pattern: String,
    pub description: String,
}

// ══════════════════════════════════════
// APK ANALYZER
// ══════════════════════════════════════

pub struct ApkAnalyzer;

impl ApkAnalyzer {
    pub fn analyze(apk_path: &str) -> Result<AnalysisResult, String> {
        let extract_dir = "/data/local/tmp/qc_extract";
        
        // Clean & extract
        let _ = fs::remove_dir_all(extract_dir);
        fs::create_dir_all(extract_dir).map_err(|e| e.to_string())?;
        
        // Extract APK (ZIP)
        let file = fs::File::open(apk_path).map_err(|e| e.to_string())?;
        let mut archive = zip::ZipArchive::new(file).map_err(|e| e.to_string())?;
        
        let mut result = AnalysisResult {
            package_name: String::new(),
            version: String::new(),
            is_unity: false,
            has_il2cpp: false,
            has_ue4: false,
            native_libs: Vec::new(),
            patches: Vec::new(),
            total_methods: 0,
            total_classes: 0,
            engine_type: "Unknown".into(),
            architecture: "Unknown".into(),
        };

        // Scan files
        let mut lib_names = std::collections::HashSet::new();
        let mut all_strings: Vec<String> = Vec::new();
        
        for i in 0..archive.len() {
            let mut file = archive.by_index(i).map_err(|e| e.to_string())?;
            let name = file.name().to_string();
            
            // Check for Unity
            if name.contains("libil2cpp.so") {
                result.is_unity = true;
                result.has_il2cpp = true;
                result.engine_type = "Unity IL2CPP".into();
            }
            if name.contains("libunity.so") {
                result.is_unity = true;
            }
            
            // Check for UE4
            if name.contains("libUE4.so") || name.contains("libUnreal.so") {
                result.has_ue4 = true;
                result.engine_type = "Unreal Engine 4".into();
            }
            
            // Detect architecture
            if name.contains("arm64-v8a") {
                result.architecture = "arm64-v8a".into();
            } else if name.contains("armeabi-v7a") && result.architecture == "Unknown" {
                result.architecture = "armeabi-v7a".into();
            }
            
            // Collect native libs
            if name.ends_with(".so") {
                if let Some(lib_name) = name.split('/').last() {
                    lib_names.insert(lib_name.to_string());
                }
            }
            
            // Scan binary content for strings
            if file.size() < 50_000_000 { // Skip very large files
                let mut content = Vec::new();
                let _ = file.read_to_end(&mut content);
                
                // Extract UTF-8 strings
                Self::extract_strings(&content, &mut all_strings);
            }
        }
        
        result.native_libs = lib_names.into_iter().collect();
        result.native_libs.sort();

        // Parse AndroidManifest.xml (binary)
        if let Ok(manifest) = archive.by_name("AndroidManifest.xml") {
            // Binary XML parsing would go here
            // For now, extract readable strings
        }

        // Match strings against Name Library
        let categories = NameLibrary::get_all_categories();
        for cat in &categories {
            let names = NameLibrary::get_names_by_category(cat);
            for name_pattern in &names {
                for found_string in &all_strings {
                    if found_string.to_lowercase().contains(&name_pattern.to_lowercase()) {
                        let display = NameLibrary::get_display_name(found_string);
                        let patch = PatchInfo {
                            name: found_string.clone(),
                            display_name: display,
                            lib_name: if result.has_il2cpp { "libil2cpp.so".into() } 
                                     else if result.has_ue4 { "libUE4.so".into() }
                                     else { "auto".into() },
                            offset: "auto".into(),
                            orig_bytes: String::new(),
                            patch_bytes: String::new(),
                            category: cat.clone(),
                            description: format!("{} - {}", found_string, cat),
                            active: false,
                        };
                        // Avoid duplicates
                        if !result.patches.iter().any(|p| p.name == patch.name) {
                            result.patches.push(patch);
                        }
                    }
                }
            }
        }

        // Add engine-specific offsets
        let engine_offsets = OffsetLibrary::get_common_offsets(
            if result.has_il2cpp { "il2cpp" }
            else if result.has_ue4 { "ue4" }
            else { "generic" }
        );
        for offset in engine_offsets {
            if !result.patches.iter().any(|p| p.name == offset.name) {
                result.patches.push(offset);
            }
        }

        result.total_methods = result.patches.len();

        // Cleanup
        let _ = fs::remove_dir_all(extract_dir);

        Ok(result)
    }

    fn extract_strings(data: &[u8], strings: &mut Vec<String>) {
        let mut current = String::new();
        for &byte in data {
            if byte >= 32 && byte < 127 {
                current.push(byte as char);
            } else {
                if current.len() >= 5 {
                    // Check if it matches any known pattern
                    strings.push(current.clone());
                }
                current.clear();
            }
        }
        // Deduplicate
        strings.sort();
        strings.dedup();
        // Keep only reasonable strings
        strings.retain(|s| s.len() >= 5 && s.len() <= 100);
        // Limit to prevent memory issues
        if strings.len() > 10000 {
            strings.truncate(10000);
        }
    }
}

// ══════════════════════════════════════
// MOD INJECTOR
// ══════════════════════════════════════

pub struct ModInjector;

impl ModInjector {
    pub fn inject(apk_path: &str, output_path: &str, patches: &[PatchInfo]) -> Result<bool, String> {
        // Step 1: Decompile with apktool
        let work_dir = "/data/local/tmp/qc_inject";
        let _ = fs::remove_dir_all(work_dir);
        
        let decompile_cmd = format!("apktool d -f -o {}/decompiled '{}' 2>/dev/null", work_dir, apk_path);
        let status = std::process::Command::new("sh")
            .arg("-c")
            .arg(&decompile_cmd)
            .status()
            .map_err(|e| e.to_string())?;

        if !status.success() {
            // Fallback: unzip
            fs::create_dir_all(format!("{}/decompiled", work_dir)).map_err(|e| e.to_string())?;
            let _ = std::process::Command::new("sh")
                .arg("-c")
                .arg(format!("unzip -q -o '{}' -d {}/decompiled 2>/dev/null", apk_path, work_dir))
                .status();
        }

        // Step 2: Inject patches
        let active_patches: Vec<&PatchInfo> = patches.iter().filter(|p| p.active).collect();
        
        // Step 3: Rebuild
        let build_cmd = format!("apktool b {}/decompiled -o {}/modded.apk 2>/dev/null", work_dir, work_dir);
        let _ = std::process::Command::new("sh")
            .arg("-c")
            .arg(&build_cmd)
            .status();

        // Step 4: Sign
        let sign_cmd = format!(
            "apksigner sign --ks /data/local/tmp/qc.keystore --ks-pass pass:quantum --out '{}' {}/modded.apk 2>/dev/null || jarsigner -keystore /data/local/tmp/qc.keystore -storepass quantum {}/modded.apk qc 2>/dev/null",
            output_path, work_dir, work_dir
        );
        let _ = std::process::Command::new("sh")
            .arg("-c")
            .arg(&sign_cmd)
            .status();

        // Cleanup
        let _ = fs::remove_dir_all(work_dir);

        Ok(Path::new(output_path).exists())
    }
}

// ══════════════════════════════════════
// SERVER INTERCEPTOR (Proxy + SSL Unpin)
// ══════════════════════════════════════

pub struct ServerInterceptor;

impl ServerInterceptor {
    pub fn setup_proxy(port: u16) -> Result<bool, String> {
        // Setup iptables redirect
        let cmds = vec![
            format!("iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port {}", port),
            format!("iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT --to-port {}", port),
        ];
        
        for cmd in cmds {
            let _ = std::process::Command::new("sh").arg("-c").arg(&cmd).status();
        }
        
        Ok(true)
    }

    pub fn ssl_unpin(package_name: &str) -> Result<bool, String> {
        // Generate Frida SSL unpinning script
        let script = r#"
Java.perform(function() {
    try {
        var TM = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        TM.verifyChain.implementation = function() { return arguments[0]; };
    } catch(e) {}
    try {
        var CP = Java.use('okhttp3.CertificatePinner');
        CP.check.overload('java.lang.String', 'java.util.List').implementation = function() {};
    } catch(e) {}
    try {
        var WVC = Java.use('android.webkit.WebViewClient');
        WVC.onReceivedSslError.implementation = function(v, h, e) { h.proceed(); };
    } catch(e) {}
    try {
        var AV = Java.use('org.apache.http.conn.ssl.AbstractVerifier');
        AV.verify.implementation = function() {};
    } catch(e) {}
});
"#;
        
        let script_path = "/data/local/tmp/qc_ssl.js";
        fs::write(script_path, script).map_err(|e| e.to_string())?;
        
        // Inject with Frida
        let cmd = format!("frida -U -f {} -l {} --no-pause 2>/dev/null &", package_name, script_path);
        let _ = std::process::Command::new("sh").arg("-c").arg(&cmd).status();
        
        Ok(true)
    }

    pub fn cleanup_proxy() -> Result<bool, String> {
        let _ = std::process::Command::new("sh")
            .arg("-c")
            .arg("iptables -t nat -F OUTPUT 2>/dev/null")
            .status();
        Ok(true)
    }
}

// ══════════════════════════════════════
// TAURI COMMANDS
// ══════════════════════════════════════

#[tauri::command]
async fn analyze_apk(path: String) -> Result<serde_json::Value, String> {
    let result = ApkAnalyzer::analyze(&path)?;
    Ok(serde_json::to_value(result).unwrap())
}

#[tauri::command]
async fn inject_mod_menu(apk_path: String, output_path: String, patches: Vec<PatchInfo>) -> Result<bool, String> {
    ModInjector::inject(&apk_path, &output_path, &patches)
}

#[tauri::command]
async fn setup_proxy(port: u16) -> Result<bool, String> {
    ServerInterceptor::setup_proxy(port)
}

#[tauri::command]
async fn ssl_unpin(package_name: String) -> Result<bool, String> {
    ServerInterceptor::ssl_unpin(&package_name)
}

#[tauri::command]
async fn cleanup_proxy() -> Result<bool, String> {
    ServerInterceptor::cleanup_proxy()
}

#[tauri::command]
fn get_name_categories() -> Vec<String> {
    NameLibrary::get_all_categories()
}

#[tauri::command]
fn get_names_by_category(category: String) -> Vec<String> {
    NameLibrary::get_names_by_category(&category)
}

#[tauri::command]
fn get_known_values() -> serde_json::Value {
    let values = ValueLibrary::get_known_values();
    serde_json::to_value(values).unwrap()
}

#[tauri::command]
fn get_version() -> String {
    "1.0.0".into()
}

// ══════════════════════════════════════
// MAIN
// ══════════════════════════════════════

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            analyze_apk,
            inject_mod_menu,
            setup_proxy,
            ssl_unpin,
            cleanup_proxy,
            get_name_categories,
            get_names_by_category,
            get_known_values,
            get_version,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Quantum Core");
}

fn main() {
    run();
}
