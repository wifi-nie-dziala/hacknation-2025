CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS facts (
    id SERIAL PRIMARY KEY,
    fact TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS facts_embedding_idx ON facts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS facts_language_idx ON facts (language);
CREATE INDEX IF NOT EXISTS facts_created_at_idx ON facts (created_at DESC);

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

CREATE INDEX IF NOT EXISTS processing_jobs_uuid_idx ON processing_jobs (job_uuid);
CREATE INDEX IF NOT EXISTS processing_jobs_status_idx ON processing_jobs (status);
CREATE INDEX IF NOT EXISTS processing_items_job_id_idx ON processing_items (job_id);
CREATE INDEX IF NOT EXISTS processing_items_status_idx ON processing_items (status);

INSERT INTO processing_jobs (job_uuid, status, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'pending', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes');

INSERT INTO processing_items (job_id, item_type, content, wage, status, created_at, updated_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '11111111-1111-1111-1111-111111111111'), 'text', 'Analyze customer feedback about product quality and pricing', 50.00, 'pending', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '11111111-1111-1111-1111-111111111111'), 'link', 'https://example.com/market-research', 75.00, 'pending', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes');

INSERT INTO processing_jobs (job_uuid, status, created_at, updated_at)
VALUES
    ('22222222-2222-2222-2222-222222222222', 'processing', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '2 minutes');

INSERT INTO processing_items (job_id, item_type, content, wage, status, processed_content, created_at, updated_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'), 'text', 'Review competitor analysis document', 100.00, 'completed', 'Analysis complete: Competitors are focusing on AI features', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '3 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'), 'file', 'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KPj4KPj4KL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL0NvbnRlbnRzIDQgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSA1IFRmCjEwMCA3MDAgVGQKKFByb2Nlc3NpbmcpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmCjAwMDAwMDAwMDkgMDAwMDAgbgowMDAwMDAwMDU4IDAwMDAwIG4KMDAwMDAwMDExNSAwMDAwMCBuCjAwMDAwMDAzMTcgMDAwMDAgbgp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQwOQolJUVPRgo=', 150.00, 'processing', NULL, NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '2 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'), 'link', 'https://example.com/sales-data', 80.00, 'pending', NULL, NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes');

INSERT INTO processing_jobs (job_uuid, status, created_at, updated_at, completed_at)
VALUES
    ('33333333-3333-3333-3333-333333333333', 'completed', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes');

INSERT INTO processing_items (job_id, item_type, content, wage, status, processed_content, created_at, updated_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 'text', 'Extract key insights from Q4 financial report', 200.00, 'completed', 'Key insights: Revenue up 15%, profit margin improved by 3%, customer acquisition cost decreased', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 'link', 'https://example.com/financial-data', 120.00, 'completed', 'Data processed successfully. All financial metrics extracted and validated.', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 'file', 'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KPj4KPj4KL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL0NvbnRlbnRzIDQgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSA1IFRmCjEwMCA3MDAgVGQKKENvbXBsZXRlZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYKMDAwMDAwMDAwOSAwMDAwMCBuCjAwMDAwMDAwNTggMDAwMDAgbgowMDAwMDAwMTE1IDAwMDAwIG4KMDAwMDAwMDMxNyAwMDAwMCBuCnRyYWlsZXIKPDwKL1NpemUgNQovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNDA5CiUlRU9GCg==', 180.00, 'completed', 'PDF document processed. Contains 15 pages of financial data and charts.', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes');

INSERT INTO processing_jobs (job_uuid, status, created_at, updated_at, completed_at, error_message)
VALUES
    ('44444444-4444-4444-4444-444444444444', 'failed', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 50 minutes', NOW() - INTERVAL '1 hour 50 minutes', 'Processing timeout: External data source unavailable');
INSERT INTO processing_items (job_id, item_type, content, wage, status, error_message, created_at, updated_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '44444444-4444-4444-4444-444444444444'), 'link', 'https://example.com/broken-endpoint', 90.00, 'failed', 'HTTP 404: Resource not found', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 50 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '44444444-4444-4444-4444-444444444444'), 'text', 'Process invalid data format', 60.00, 'failed', 'Invalid data format: Unable to parse content', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 50 minutes');

