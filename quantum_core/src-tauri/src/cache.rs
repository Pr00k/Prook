// Result caching system with TTL support

use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use chrono::{DateTime, Utc, Duration};
use serde_json::Value;

pub struct CacheEntry {
    value: Value,
    expires_at: DateTime<Utc>,
}

/// Thread-safe cache with automatic expiration
pub struct Cache {
    store: Arc<RwLock<HashMap<String, CacheEntry>>>,
}

impl Cache {
    /// Create new cache instance
    pub fn new() -> Self {
        Cache {
            store: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Set cache value with TTL (minutes)
    pub async fn set(&self, key: String, value: Value, ttl_minutes: i64) {
        let mut store = self.store.write().await;
        let expires_at = Utc::now() + Duration::minutes(ttl_minutes);
        store.insert(key, CacheEntry { value, expires_at });
        tracing::debug!("💾 Cache set: {} (TTL: {}min)", key, ttl_minutes);
    }

    /// Get cache value (returns None if expired)
    pub async fn get(&self, key: &str) -> Option<Value> {
        let mut store = self.store.write().await;
        if let Some(entry) = store.get(key) {
            if entry.expires_at > Utc::now() {
                tracing::debug!("⚡ Cache hit: {}", key);
                return Some(entry.value.clone());
            } else {
                tracing::debug!("🗑️ Cache expired: {}", key);
                store.remove(key);
            }
        }
        None
    }

    /// Clear all cache
    pub async fn clear(&self) {
        let mut store = self.store.write().await;
        store.clear();
        tracing::info!("🗑️ Cache cleared");
    }

    /// Remove expired entries
    pub async fn cleanup(&self) {
        let mut store = self.store.write().await;
        let now = Utc::now();
        let before = store.len();
        store.retain(|_, entry| entry.expires_at > now);
        tracing::info!("🧹 Cache cleanup: removed {} expired entries", before - store.len());
    }

    /// Get cache size
    pub async fn size(&self) -> usize {
        self.store.read().await.len()
    }
}

impl Default for Cache {
    fn default() -> Self {
        Self::new()
    }
}
