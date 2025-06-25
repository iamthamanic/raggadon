-- SQL to create the match_documents function for vector similarity search
-- Copy this code and run it in the Supabase SQL Editor

-- Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create or replace the match_documents function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    project_filter text
)
RETURNS TABLE (
    id uuid,
    project text,
    role text,
    content text,
    similarity float,
    created_at timestamp
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pm.id,
        pm.project,
        pm.role,
        pm.content,
        1 - (pm.embedding <=> query_embedding) as similarity,
        pm.created_at
    FROM project_memory pm
    WHERE pm.project = project_filter
        AND 1 - (pm.embedding <=> query_embedding) > match_threshold
    ORDER BY pm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION match_documents(vector, float, int, text) TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents(vector, float, int, text) TO anon;

-- Create an index for better performance on vector similarity search
CREATE INDEX IF NOT EXISTS idx_project_memory_embedding ON project_memory 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on project for faster filtering
CREATE INDEX IF NOT EXISTS idx_project_memory_project ON project_memory(project);