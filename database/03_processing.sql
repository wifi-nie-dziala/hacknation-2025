CREATE TABLE IF NOT EXISTS processing_jobs (
    id SERIAL PRIMARY KEY,
    job_uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS processing_items (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL CHECK (item_type IN ('text', 'file', 'link')),
    content TEXT NOT NULL,
    wage DECIMAL(10, 2),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    processed_content TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processing_steps (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_type VARCHAR(50) NOT NULL CHECK (step_type IN ('scraping', 'extraction', 'reasoning', 'validation', 'embedding')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped')),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(job_id, step_number)
);

CREATE TABLE IF NOT EXISTS extracted_facts (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES processing_steps(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES processing_items(id) ON DELETE CASCADE,
    fact TEXT NOT NULL,
    wage DECIMAL(10, 2),
    source_type VARCHAR(20),
    source_content TEXT,
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    is_validated BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraped_data (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES processing_steps(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    content TEXT,
    content_type VARCHAR(50),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS processing_jobs_uuid_idx ON processing_jobs (job_uuid);
CREATE INDEX IF NOT EXISTS processing_jobs_status_idx ON processing_jobs (status);
CREATE INDEX IF NOT EXISTS processing_items_job_id_idx ON processing_items (job_id);
CREATE INDEX IF NOT EXISTS processing_items_status_idx ON processing_items (status);
CREATE INDEX IF NOT EXISTS processing_steps_job_id_idx ON processing_steps (job_id);
CREATE INDEX IF NOT EXISTS processing_steps_status_idx ON processing_steps (status);
CREATE INDEX IF NOT EXISTS extracted_facts_job_id_idx ON extracted_facts (job_id);
CREATE INDEX IF NOT EXISTS extracted_facts_item_id_idx ON extracted_facts (item_id);
CREATE INDEX IF NOT EXISTS extracted_facts_validated_idx ON extracted_facts (is_validated);
CREATE INDEX IF NOT EXISTS scraped_data_job_id_idx ON scraped_data (job_id);

