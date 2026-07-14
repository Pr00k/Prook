// SQLite database layer for persistent storage

use rusqlite::Connection;
use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use serde::{Serialize, Deserialize};
use chrono::Utc;
use crate::errors::{Result, QuantumError};

pub type DbPool = Pool<SqliteConnectionManager>;

/// Database wrapper for connection pooling
pub struct Database {
    pool: DbPool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisLog {
    pub id: String,
    pub apk_path: String,
    pub package_name: String,
    pub engine_type: String,
    pub patches_found: i32,
    pub status: String,
    pub created_at: String,
    pub completed_at: Option<String>,
    pub error_message: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModificationLog {
    pub id: String,
    pub analysis_id: String,
    pub patches: String,
    pub output_path: String,
    pub signed: bool,
    pub status: String,
    pub created_at: String,
}

impl Database {
    /// Create new database connection pool
    pub fn new(db_path: &str) -> Result<Self> {
        let manager = SqliteConnectionManager::file(db_path);
        let pool = Pool::new(manager)
            .map_err(|e| QuantumError::Database(e.into()))?;

        tracing::info!("📦 Database pool created: {}", db_path);
        Ok(Database { pool })
    }

    /// Initialize database schema
    pub fn init_schema(&self) -> Result<()> {
        let conn = self.pool.get()
            .map_err(|e| QuantumError::Database(e.into()))?;

        conn.execute_batch(
            r#"
            CREATE TABLE IF NOT EXISTS analysis_logs (
                id TEXT PRIMARY KEY,
                apk_path TEXT NOT NULL,
                package_name TEXT,
                engine_type TEXT,
                patches_found INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS modification_logs (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                patches TEXT NOT NULL,
                output_path TEXT NOT NULL,
                signed BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_logs(id)
            );

            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_analysis_status ON analysis_logs(status);
            CREATE INDEX IF NOT EXISTS idx_modification_status ON modification_logs(status);
            "#
        ).map_err(|e| QuantumError::Database(e))?;

        tracing::info!("✅ Database schema initialized");
        Ok(())
    }

    /// Insert analysis log
    pub fn insert_analysis_log(&self, log: &AnalysisLog) -> Result<()> {
        let conn = self.pool.get()
            .map_err(|e| QuantumError::Database(e.into()))?;

        conn.execute(
            "INSERT INTO analysis_logs (id, apk_path, package_name, engine_type, patches_found, status, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            rusqlite::params![
                log.id,
                log.apk_path,
                log.package_name,
                log.engine_type,
                log.patches_found,
                log.status,
                log.created_at
            ],
        ).map_err(|e| QuantumError::Database(e))?;

        tracing::info!("📝 Analysis log inserted: {}", log.id);
        Ok(())
    }

    /// Get recent analyses
    pub fn get_recent_analyses(&self, limit: i32) -> Result<Vec<AnalysisLog>> {
        let conn = self.pool.get()
            .map_err(|e| QuantumError::Database(e.into()))?;

        let mut stmt = conn.prepare(
            "SELECT id, apk_path, package_name, engine_type, patches_found, status, created_at, completed_at, error_message
             FROM analysis_logs ORDER BY created_at DESC LIMIT ?1"
        ).map_err(|e| QuantumError::Database(e))?;

        let logs = stmt.query_map(rusqlite::params![limit], |row| {
            Ok(AnalysisLog {
                id: row.get(0)?,
                apk_path: row.get(1)?,
                package_name: row.get(2)?,
                engine_type: row.get(3)?,
                patches_found: row.get(4)?,
                status: row.get(5)?,
                created_at: row.get(6)?,
                completed_at: row.get(7)?,
                error_message: row.get(8)?,
            })
        }).map_err(|e| QuantumError::Database(e))?
            .collect::<std::result::Result<Vec<_>, _>>()
            .map_err(|e| QuantumError::Database(e))?;

        Ok(logs)
    }

    /// Update analysis status
    pub fn update_analysis_status(&self, id: &str, status: &str, error: Option<&str>) -> Result<()> {
        let conn = self.pool.get()
            .map_err(|e| QuantumError::Database(e.into()))?;

        conn.execute(
            "UPDATE analysis_logs SET status = ?1, error_message = ?2, completed_at = ?3 WHERE id = ?4",
            rusqlite::params![status, error, Utc::now().to_rfc3339(), id],
        ).map_err(|e| QuantumError::Database(e))?;

        tracing::info!("✏️ Analysis {} status updated to: {}", id, status);
        Ok(())
    }
}
