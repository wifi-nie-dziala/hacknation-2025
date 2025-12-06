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
    fact TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS extracted_facts_validated_idx ON extracted_facts (is_validated);
CREATE INDEX IF NOT EXISTS scraped_data_job_id_idx ON scraped_data (job_id);

TRUNCATE TABLE scraped_data, extracted_facts, processing_steps, processing_items, processing_jobs RESTART IDENTITY CASCADE;

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

INSERT INTO processing_steps (job_id, step_number, step_type, status, input_data, output_data, metadata, created_at, updated_at, completed_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'), 1, 'scraping', 'completed', '{"url": "https://example.com/sales-data"}', '{"scraped_length": 2500}', '{"source": "link_item"}', NOW() - INTERVAL '9 minutes', NOW() - INTERVAL '8 minutes', NOW() - INTERVAL '8 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'), 2, 'extraction', 'processing', '{"text_length": 3200}', NULL, '{"language": "en"}', NOW() - INTERVAL '7 minutes', NOW() - INTERVAL '2 minutes', NULL),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 1, 'scraping', 'completed', '{"url": "https://example.com/financial-data"}', '{"scraped_length": 4800}', '{"source": "link_item"}', NOW() - INTERVAL '55 minutes', NOW() - INTERVAL '50 minutes', NOW() - INTERVAL '50 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 2, 'extraction', 'completed', '{"text_length": 8500}', '{"facts_extracted": 12}', '{"language": "en"}', NOW() - INTERVAL '45 minutes', NOW() - INTERVAL '40 minutes', NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 3, 'validation', 'completed', '{"fact_count": 12}', '{"validated_facts": 12}', '{"auto_validate": true}', NOW() - INTERVAL '40 minutes', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'), 4, 'embedding', 'completed', '{"fact_count": 12}', '{"embedded_facts": 12}', '{}', NOW() - INTERVAL '35 minutes', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '44444444-4444-4444-4444-444444444444'), 1, 'scraping', 'failed', '{"url": "https://example.com/broken-endpoint"}', NULL, '{"source": "link_item"}', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 50 minutes', NOW() - INTERVAL '1 hour 50 minutes');

INSERT INTO scraped_data (job_id, step_id, url, content, content_type, status, metadata, created_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222') AND step_number = 1),
     'https://example.com/sales-data',
     'Sales Data Analysis Q4: Total revenue increased by 18%, new customer acquisition up 25%, retention rate improved to 89%.',
     'text/html',
     'completed',
     '{"scrape_time_ms": 450, "content_length": 2500}',
     NOW() - INTERVAL '8 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 1),
     'https://example.com/financial-data',
     'Financial Report Q4: Revenue $5.2M (up 15%), Operating expenses $3.8M (down 5%), Net profit margin 26.9% (up 3%), Customer acquisition cost decreased by 12%, Average revenue per user increased to $245.',
     'text/html',
     'completed',
     '{"scrape_time_ms": 320, "content_length": 4800}',
     NOW() - INTERVAL '50 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '44444444-4444-4444-4444-444444444444'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '44444444-4444-4444-4444-444444444444') AND step_number = 1),
     'https://example.com/broken-endpoint',
     NULL,
     NULL,
     'failed',
     '{"error_code": 404}',
     NOW() - INTERVAL '1 hour 50 minutes');

INSERT INTO extracted_facts (job_id, step_id, fact, source_type, source_content, confidence, is_validated, language, metadata, created_at)
VALUES
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 2),
     'Q4 revenue increased by 15% to $5.2M',
     'llm_extraction',
     'Financial Report Q4: Revenue $5.2M (up 15%), Operating expenses...',
     0.95,
     TRUE,
     'en',
     '{"category": "financial", "period": "Q4"}',
     NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 2),
     'Operating expenses decreased by 5% to $3.8M',
     'llm_extraction',
     'Financial Report Q4: Revenue $5.2M (up 15%), Operating expenses $3.8M (down 5%)...',
     0.92,
     TRUE,
     'en',
     '{"category": "financial", "period": "Q4"}',
     NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 2),
     'Net profit margin improved by 3% to 26.9%',
     'llm_extraction',
     'Financial Report Q4: ...Net profit margin 26.9% (up 3%)...',
     0.90,
     TRUE,
     'en',
     '{"category": "financial", "period": "Q4"}',
     NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 2),
     'Customer acquisition cost decreased by 12%',
     'llm_extraction',
     'Financial Report Q4: ...Customer acquisition cost decreased by 12%...',
     0.88,
     TRUE,
     'en',
     '{"category": "marketing", "period": "Q4"}',
     NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '33333333-3333-3333-3333-333333333333') AND step_number = 2),
     'Average revenue per user increased to $245',
     'llm_extraction',
     'Financial Report Q4: ...Average revenue per user increased to $245.',
     0.91,
     TRUE,
     'en',
     '{"category": "financial", "period": "Q4"}',
     NOW() - INTERVAL '40 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222') AND step_number = 2),
     'Total revenue increased by 18% in Q4',
     'llm_extraction',
     'Sales Data Analysis Q4: Total revenue increased by 18%...',
     0.85,
     FALSE,
     'en',
     '{"category": "sales", "period": "Q4"}',
     NOW() - INTERVAL '5 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222') AND step_number = 2),
     'New customer acquisition up 25%',
     'llm_extraction',
     'Sales Data Analysis Q4: ...new customer acquisition up 25%...',
     0.82,
     FALSE,
     'en',
     '{"category": "marketing", "period": "Q4"}',
     NOW() - INTERVAL '5 minutes'),
    ((SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222'),
     (SELECT id FROM processing_steps WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = '22222222-2222-2222-2222-222222222222') AND step_number = 2),
     'Customer retention rate improved to 89%',
     'llm_extraction',
     'Sales Data Analysis Q4: ...retention rate improved to 89%.',
     0.87,
     FALSE,
     'en',
     '{"category": "sales", "period": "Q4"}',
     NOW() - INTERVAL '5 minutes');

