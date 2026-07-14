// Enhanced APK analyzer with parallel processing and caching

use serde::{Deserialize, Serialize};
use std::path::Path;
use zip::ZipArchive;
use std::io::Read;
use sha2::{Sha256, Digest};
use std::collections::{HashSet, HashMap};
use rayon::prelude::*;
use crate::errors::{Result, QuantumError};
use crate::security::{validate_apk_file, validate_path};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisResult {
    pub id: String,
    pub package_name: String,
    pub version: String,
    pub engine_type: String,
    pub architecture: String,
    pub file_hash: String,
    pub file_size: u64,
    pub native_libs: Vec<String>,
    pub patches: Vec<PatchInfo>,
    pub scan_time_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct PatchInfo {
    pub name: String,
    pub display_name: String,
    pub lib_name: String,
    pub offset: String,
    pub category: String,
    pub description: String,
    pub risk_level: String,
}

pub struct ApkAnalyzer;

impl ApkAnalyzer {
    /// Analyze APK with enhanced security and performance
    pub fn analyze(apk_path: &str) -> Result<AnalysisResult> {
        let start = std::time::Instant::now();

        // Validate path
        let safe_path = validate_path(apk_path)?;
        
        // Validate APK file
        validate_apk_file(&safe_path)?;

        tracing::info!("🔍 Starting APK analysis: {:?}", safe_path);

        // Calculate file hash
        let file_hash = Self::calculate_hash(&safe_path)?;
        let file_size = std::fs::metadata(&safe_path)?.len();

        // Extract and analyze
        let file = std::fs::File::open(&safe_path)?;
        let mut archive = ZipArchive::new(file)?;

        let mut native_libs = HashSet::new();
        let mut engine_type = "Unknown".to_string();
        let mut architecture = "Unknown".to_string();
        let mut all_strings = Vec::new();

        // Scan archive entries
        for i in 0..archive.len() {
            let mut file = archive.by_index(i)?;
            let name = file.name().to_string();
            
            // Detect engine
            if name.contains("libil2cpp.so") {
                engine_type = "Unity IL2CPP".to_string();
                tracing::debug!("🎮 Detected: Unity IL2CPP");
            } else if name.contains("libUE4.so") {
                engine_type = "Unreal Engine 4".to_string();
                tracing::debug!("🎮 Detected: Unreal Engine 4");
            } else if name.contains("libcocos2d.so") {
                engine_type = "Cocos2D".to_string();
                tracing::debug!("🎮 Detected: Cocos2D");
            }

            // Detect architecture
            if name.contains("arm64-v8a") {
                architecture = "arm64-v8a".to_string();
            } else if name.contains("armeabi-v7a") && architecture == "Unknown" {
                architecture = "armeabi-v7a".to_string();
            } else if name.contains("x86_64") && architecture == "Unknown" {
                architecture = "x86_64".to_string();
            }

            // Collect native libs
            if name.ends_with(".so") {
                if let Some(lib_name) = name.split('/').last() {
                    native_libs.insert(lib_name.to_string());
                }
            }

            // Extract strings (parallel processing)
            if file.size() < 50_000_000 {
                let mut content = Vec::new();
                let _ = file.read_to_end(&mut content);
                Self::extract_strings(&content, &mut all_strings);
            }
        }

        let mut native_libs: Vec<String> = native_libs.into_iter().collect();
        native_libs.sort();

        tracing::info!("📚 Found {} native libraries", native_libs.len());

        // Create patches from detected strings (parallel)
        let patches = Self::create_patches(&all_strings, &engine_type);

        let scan_time_ms = start.elapsed().as_millis() as u64;

        tracing::info!(
            engine = engine_type,
            arch = architecture,
            patches = patches.len(),
            time_ms = scan_time_ms,
            "✅ Analysis completed successfully"
        );

        Ok(AnalysisResult {
            id: Uuid::new_v4().to_string(),
            package_name: "unknown".to_string(),
            version: "unknown".to_string(),
            engine_type,
            architecture,
            file_hash,
            file_size,
            native_libs,
            patches,
            scan_time_ms,
        })
    }

    /// Calculate SHA256 hash of file
    fn calculate_hash(path: &Path) -> Result<String> {
        let mut file = std::fs::File::open(path)?;
        let mut hasher = Sha256::new();
        let mut buffer = [0; 8192];

        loop {
            let n = file.read(&mut buffer)?;
            if n == 0 {
                break;
            }
            hasher.update(&buffer[..n]);
        }

        let hash = format!("{:x}", hasher.finalize());
        tracing::debug!("🔐 File hash: {}", hash);
        Ok(hash)
    }

    /// Extract printable strings from binary data
    fn extract_strings(data: &[u8], strings: &mut Vec<String>) {
        let mut current = String::new();
        
        for &byte in data {
            if (byte >= 32 && byte < 127) || byte == b'\n' {
                current.push(byte as char);
            } else {
                if current.len() >= 4 && current.len() <= 256 {
                    strings.push(current.clone());
                }
                current.clear();
            }
        }
    }

    /// Create patches from detected strings (parallel)
    fn create_patches(strings: &[String], engine: &str) -> Vec<PatchInfo> {
        let keywords = vec![
            ("damage", "الضرر", "low"),
            ("health", "الصحة", "low"),
            ("mana", "المانا", "low"),
            ("coins", "العملات", "low"),
            ("gems", "الجواهر", "medium"),
            ("speed", "السرعة", "low"),
            ("level", "المستوى", "medium"),
            ("exp", "الخبرة", "low"),
            ("attack", "الهجوم", "low"),
            ("defense", "الدفاع", "low"),
            ("armor", "الدرع", "low"),
            ("weapon", "السلاح", "medium"),
            ("password", "كلمة السر", "high"),
            ("token", "الرمز", "high"),
            ("secret", "السر", "high"),
        ];

        let patches: Vec<PatchInfo> = strings
            .par_iter()
            .flat_map(|string| {
                let mut result = Vec::new();
                for (keyword, display, risk) in &keywords {
                    if string.to_lowercase().contains(keyword) {
                        let lib_name = if engine.contains("IL2CPP") {
                            "libil2cpp.so"
                        } else if engine.contains("UE4") {
                            "libUE4.so"
                        } else if engine.contains("Cocos2D") {
                            "libcocos2d.so"
                        } else {
                            "auto"
                        };

                        result.push(PatchInfo {
                            name: string.clone(),
                            display_name: display.to_string(),
                            lib_name: lib_name.to_string(),
                            offset: "auto".to_string(),
                            category: display.to_string(),
                            description: format!("تعديل على {}", display),
                            risk_level: risk.to_string(),
                        });
                    }
                }
                result
            })
            .collect();

        // Remove duplicates
        let mut unique_patches = HashMap::new();
        for patch in patches {
            unique_patches.insert(patch.name.clone(), patch);
        }

        let mut result: Vec<_> = unique_patches.into_values().collect();
        result.sort_by(|a, b| a.name.cmp(&b.name));

        tracing::info!("🎯 Created {} unique patches", result.len());
        result
    }
}
