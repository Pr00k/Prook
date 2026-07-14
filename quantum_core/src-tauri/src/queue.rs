// Background job queue system for async operations

use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use chrono::Utc;
use crate::errors::Result;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Job {
    pub id: String,
    pub job_type: JobType,
    pub status: JobStatus,
    pub created_at: String,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub error: Option<String>,
    pub progress: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobType {
    AnalyzeApk { path: String },
    InjectMod { apk_path: String, patches: Vec<String> },
    SignApk { path: String },
    BatchAnalyze { paths: Vec<String> },
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum JobStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
}

pub struct JobQueue {
    sender: mpsc::UnboundedSender<Job>,
    jobs: Arc<RwLock<HashMap<String, Job>>>,
}

impl JobQueue {
    pub fn new() -> (Self, mpsc::UnboundedReceiver<Job>) {
        let (sender, receiver) = mpsc::unbounded_channel();
        (
            JobQueue {
                sender,
                jobs: Arc::new(RwLock::new(HashMap::new())),
            },
            receiver,
        )
    }

    pub async fn enqueue(&self, job_type: JobType) -> Result<String> {
        let job = Job {
            id: uuid::Uuid::new_v4().to_string(),
            job_type,
            status: JobStatus::Pending,
            created_at: Utc::now().to_rfc3339(),
            started_at: None,
            completed_at: None,
            error: None,
            progress: 0.0,
        };

        let job_id = job.id.clone();
        self.sender.send(job.clone())
            .map_err(|e| crate::errors::QuantumError::QueueError(e.to_string()))?;
        
        self.jobs.write().await.insert(job_id.clone(), job);

        tracing::info!("📋 Job enqueued: {}", job_id);
        Ok(job_id)
    }

    pub async fn get_job(&self, id: &str) -> Option<Job> {
        self.jobs.read().await.get(id).cloned()
    }

    pub async fn update_job_status(&self, id: &str, status: JobStatus, error: Option<String>) {
        let mut jobs = self.jobs.write().await;
        if let Some(job) = jobs.get_mut(id) {
            job.status = status;
            if error.is_some() {
                job.error = error;
            }
            job.completed_at = Some(Utc::now().to_rfc3339());
            tracing::info!("✏️ Job {} status updated to: {:?}", id, job.status);
        }
    }

    pub async fn update_job_progress(&self, id: &str, progress: f32) {
        let mut jobs = self.jobs.write().await;
        if let Some(job) = jobs.get_mut(id) {
            job.progress = progress.min(100.0);
            if job.status == JobStatus::Pending {
                job.status = JobStatus::Running;
                job.started_at = Some(Utc::now().to_rfc3339());
            }
        }
    }

    pub async fn get_recent_jobs(&self, limit: usize) -> Vec<Job> {
        let jobs = self.jobs.read().await;
        let mut result: Vec<_> = jobs.values().cloned().collect();
        result.sort_by(|a, b| b.created_at.cmp(&a.created_at));
        result.into_iter().take(limit).collect()
    }

    pub async fn get_running_jobs(&self) -> Vec<Job> {
        let jobs = self.jobs.read().await;
        jobs.values()
            .filter(|j| j.status == JobStatus::Running)
            .cloned()
            .collect()
    }

    pub async fn cancel_job(&self, id: &str) -> Result<()> {
        let mut jobs = self.jobs.write().await;
        if let Some(job) = jobs.get_mut(id) {
            job.status = JobStatus::Cancelled;
            job.completed_at = Some(Utc::now().to_rfc3339());
            tracing::info!("❌ Job {} cancelled", id);
        }
        Ok(())
    }

    pub async fn clear_old_jobs(&self, days: i64) {
        let mut jobs = self.jobs.write().await;
        let cutoff = chrono::Utc::now() - chrono::Duration::days(days);
        let before = jobs.len();
        
        jobs.retain(|_, job| {
            if let Ok(created) = chrono::DateTime::parse_from_rfc3339(&job.created_at) {
                created.with_timezone(&chrono::Utc) > cutoff
            } else {
                true
            }
        });

        tracing::info!("🧹 Cleaned up {} old jobs", before - jobs.len());
    }
}

impl Default for JobQueue {
    fn default() -> Self {
        Self::new().0
    }
}
