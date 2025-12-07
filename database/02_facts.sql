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

