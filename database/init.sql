-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create facts table
CREATE TABLE IF NOT EXISTS facts (
    id SERIAL PRIMARY KEY,
    fact TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS facts_embedding_idx ON facts USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for language
CREATE INDEX IF NOT EXISTS facts_language_idx ON facts (language);

-- Create index for created_at
CREATE INDEX IF NOT EXISTS facts_created_at_idx ON facts (created_at DESC);

