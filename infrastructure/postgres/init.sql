CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(id),
    file_name VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    content TEXT NOT NULL,
    embedding vector(768)
);

CREATE TABLE IF NOT EXISTS clinical_events (
    id UUID PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(id),
    document_id UUID REFERENCES documents(id),
    event_type VARCHAR(100) NOT NULL,
    details JSONB,
    confidence FLOAT,
    event_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS care_gaps (
    id UUID PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(id),
    gap_type VARCHAR(100) NOT NULL,
    description TEXT,
    confidence FLOAT,
    status VARCHAR(50) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(id),
    gap_id UUID REFERENCES care_gaps(id),
    description TEXT,
    priority VARCHAR(50) DEFAULT 'Medium',
    assigned_to VARCHAR(100),
    status VARCHAR(50) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);