CREATE TABLE IF NOT EXISTS nodes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    type VARCHAR(30) NOT NULL CHECK (type IN ('fact', 'prediction')),
    value TEXT NOT NULL,
    job_id INTEGER REFERENCES processing_jobs(id) ON DELETE CASCADE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS node_relations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL CHECK (relation_type IN ('derived_from', 'supports', 'contradicts', 'requires', 'suggests')),
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS nodes_type_idx ON nodes (type);
CREATE INDEX IF NOT EXISTS nodes_job_id_idx ON nodes (job_id);
CREATE INDEX IF NOT EXISTS node_relations_source_idx ON node_relations (source_node_id);
CREATE INDEX IF NOT EXISTS node_relations_target_idx ON node_relations (target_node_id);
CREATE INDEX IF NOT EXISTS node_relations_type_idx ON node_relations (relation_type);

