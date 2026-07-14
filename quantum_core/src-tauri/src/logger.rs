// Comprehensive logging system using tracing

use tracing_subscriber::{
    fmt::{self, format::FmtSpan},
    layer::SubscriberExt,
    util::SubscriberInitExt,
    EnvFilter,
};
use tracing_appender::non_blocking::WorkerGuard;
use crate::errors::Result;

/// Initialize tracing for the application
pub fn init_tracing() -> Result<WorkerGuard> {
    let file_appender = tracing_appender::rolling::daily("/tmp/quantum_core", "quantum.log");
    let (non_blocking, guard) = tracing_appender::non_blocking(file_appender);

    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("quantum_core=debug,info"));

    tracing_subscriber::registry()
        .with(env_filter)
        .with(
            fmt::layer()
                .json()
                .with_span_events(FmtSpan::CLOSE)
                .with_writer(non_blocking),
        )
        .with(
            fmt::layer()
                .pretty()
                .with_writer(std::io::stdout),
        )
        .init();

    tracing::info!("🚀 Quantum Core Logging Initialized");
    Ok(guard)
}

#[macro_export]
macro_rules! log_operation {
    ($op:expr, $status:expr) => {
        if $status {
            tracing::info!(operation = $op, "✅ Operation completed");
        } else {
            tracing::error!(operation = $op, "❌ Operation failed");
        }
    };
}
