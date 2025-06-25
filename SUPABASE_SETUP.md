# Supabase Setup für Raggadon

## Fehlerbehebung: match_documents Funktion

Wenn du den Fehler "Could not find the function public.match_documents" bekommst, musst du die Funktion in Supabase erstellen.

### Schritte:

1. **Gehe zu deinem Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/vfrdoxhdphxiprvehbol

2. **Öffne den SQL Editor**
   - Klicke links auf "SQL Editor"

3. **Führe das SQL Script aus**
   - Kopiere den gesamten Inhalt von `create_match_documents_function.sql`
   - Füge ihn in den SQL Editor ein
   - Klicke auf "Run"

4. **Prüfe die Tabellen-Struktur**
   Falls die `project_memory` Tabelle fehlt, erstelle sie mit:

```sql
CREATE TABLE IF NOT EXISTS project_memory (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project text NOT NULL,
    role text NOT NULL,
    content text NOT NULL,
    embedding vector(1536),
    created_at timestamp DEFAULT now()
);
```

### Alternative: Temporärer Fix

Bis die Funktion erstellt ist, kannst du die Suchfunktion temporär deaktivieren, indem du eine einfachere Version verwendest.

## Überprüfung

Nach der Ausführung sollte `rag search` funktionieren:

```bash
rag search "test"
```