// Comprehensive error handling for Quantum Core

use thiserror::Error;
use std::path::PathBuf;

#[derive(Error, Debug)]
pub enum QuantumError {
    #[error("File validation failed: {0}")]
    FileValidation(String),

    #[error("Invalid APK path: {path}")]
    InvalidPath { path: PathBuf },

    #[error("File size exceeded: {size} bytes (max: {max})")]
    FileSizeExceeded { size: u64, max: u64 },

    #[error("APK parsing error: {0}")]
    ApkParsing(String),

    #[error("Database error: {0}")]
    Database(#[from] rusqlite::Error),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("ZIP error: {0}")]
    Zip(#[from] zip::result::ZipError),

    #[error("Security violation: {0}")]
    SecurityViolation(String),

    #[error("Injection failed: {0}")]
    InjectionFailed(String),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Command execution failed: {0}")]
    CommandFailed(String),

    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Operation timeout")]
    Timeout,

    #[error("Queue error: {0}")]
    QueueError(String),

    #[error("Unknown error: {0}")]
    Unknown(String),
}

pub type Result<T> = std::result::Result<T, QuantumError>;

impl From<String> for QuantumError {
    fn from(s: String) -> Self {
        QuantumError::Unknown(s)
    }
}

impl From<&str> for QuantumError {
    fn from(s: &str) -> Self {
        QuantumError::Unknown(s.to_string())
    }
}
