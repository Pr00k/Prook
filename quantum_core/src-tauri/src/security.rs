// Security utilities for input validation and sanitization

use std::path::{Path, PathBuf};
use regex::Regex;
use crate::errors::{Result, QuantumError};

const MAX_FILE_SIZE: u64 = 500 * 1024 * 1024; // 500 MB
const MAX_PATH_LENGTH: usize = 4096;

/// Validate file path safety
pub fn validate_path(path: &str) -> Result<PathBuf> {
    // Check length
    if path.len() > MAX_PATH_LENGTH {
        return Err(QuantumError::InvalidPath {
            path: PathBuf::from(path),
        });
    }

    // Check for path traversal attacks
    if path.contains("..") || path.contains("~") {
        return Err(QuantumError::SecurityViolation(
            "Path traversal detected".to_string(),
        ));
    }

    Ok(PathBuf::from(path))
}

/// Validate APK file
pub fn validate_apk_file(path: &Path) -> Result<()> {
    // Check if file exists
    if !path.exists() {
        return Err(QuantumError::FileValidation(
            format!("File does not exist: {:?}", path),
        ));
    }

    // Check if it's a file (not directory)
    if !path.is_file() {
        return Err(QuantumError::FileValidation(
            "Path is not a file".to_string(),
        ));
    }

    // Check file extension
    let extension = path.extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("");

    if !matches!(extension, "apk" | "xapk" | "apks") {
        return Err(QuantumError::FileValidation(
            format!("Invalid file extension: {}", extension),
        ));
    }

    // Check file size
    let metadata = std::fs::metadata(path)
        .map_err(|e| QuantumError::FileValidation(e.to_string()))?;
    
    if metadata.len() > MAX_FILE_SIZE {
        return Err(QuantumError::FileSizeExceeded {
            size: metadata.len(),
            max: MAX_FILE_SIZE,
        });
    }

    // Check if it's a valid ZIP file
    let file = std::fs::File::open(path)
        .map_err(|e| QuantumError::FileValidation(e.to_string()))?;
    zip::ZipArchive::new(file)
        .map_err(|e| QuantumError::FileValidation(format!("Invalid ZIP: {}", e)))?;

    tracing::info!("✅ File validation passed: {:?}", path);
    Ok(())
}

/// Sanitize command output
pub fn sanitize_output(output: &str) -> String {
    output
        .trim()
        .lines()
        .filter(|line| !line.starts_with("WARNING") && !line.is_empty())
        .collect::<Vec<_>>()
        .join("\n")
}

/// Escape shell special characters
pub fn escape_shell(s: &str) -> String {
    format!("'{}'", s.replace("'", "'\\\"'\\\"'"))
}

/// Validate package name format
pub fn validate_package_name(pkg: &str) -> Result<()> {
    let re = Regex::new(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$")
        .map_err(|e| QuantumError::SecurityViolation(e.to_string()))?;

    if re.is_match(pkg) {
        Ok(())
    } else {
        Err(QuantumError::SecurityViolation(
            "Invalid package name format".to_string(),
        ))
    }
}
