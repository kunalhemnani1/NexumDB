use thiserror::Error;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("Failed to open database: {0}")]
    OpenError(String),

    #[error("Failed to write to database: {0}")]
    WriteError(String),

    #[error("Failed to read from database: {0}")]
    ReadError(String),

    #[error("Key not found: {0}")]
    KeyNotFound(String),

    #[error("Serialization error: {0}")]
    SerializationError(String),
}

impl From<sled::Error> for StorageError {
    fn from(err: sled::Error) -> Self {
        match err {
            sled::Error::Io(io_err) => StorageError::WriteError(io_err.to_string()),
            _ => StorageError::WriteError(err.to_string()),
        }
    }
}

impl From<serde_json::Error> for StorageError {
    fn from(err: serde_json::Error) -> Self {
        StorageError::SerializationError(err.to_string())
    }
}
