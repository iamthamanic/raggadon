# PGVector Setup für Raggadon

## Schritt-für-Schritt Anleitung

### 1. Öffne Supabase Dashboard
Gehe zu: https://supabase.com/dashboard/project/vfrdoxhdphxiprvehbol/sql/new

### 2. Führe folgende SQL-Befehle aus:

```sql
-- 1. Aktiviere pgvector Extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Erstelle die match_documents Funktion
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

-- 3. Setze Berechtigungen
GRANT EXECUTE ON FUNCTION match_documents(vector, float, int, text) TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents(vector, float, int, text) TO anon;

-- 4. Erstelle Index für bessere Performance
CREATE INDEX IF NOT EXISTS idx_project_memory_embedding ON project_memory 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 3. Klicke auf "Run"

### 4. Teste die Funktion
Nach der Installation kannst du testen:

```bash
rag search "AI Integration"
```

## Warum pgvector?

- **Echte Vektor-Ähnlichkeitssuche**: Findet semantisch ähnliche Inhalte, nicht nur Textübereinstimmungen
- **Bessere Ergebnisse**: Versteht Kontext und Bedeutung
- **Skalierbar**: Funktioniert auch mit Millionen von Einträgen
- **OpenAI Integration**: Nutzt die gleichen Embeddings wie ChatGPT

## Troubleshooting

Falls du den Fehler "permission denied for schema pgvector" bekommst:
1. Kontaktiere Supabase Support
2. Oder nutze temporär die Textsuche (bereits als Fallback implementiert)