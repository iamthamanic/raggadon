-- SQL to create missing embedding_usage table in Supabase
-- Copy this code and run it in the Supabase SQL Editor

CREATE TABLE IF NOT EXISTS embedding_usage (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project text NOT NULL,
    usage_type text NOT NULL,     -- 'save' oder 'search'
    tokens integer NOT NULL,
    created_at timestamp DEFAULT now()
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_embedding_usage_project ON embedding_usage(project);
CREATE INDEX IF NOT EXISTS idx_embedding_usage_created_at ON embedding_usage(created_at);