# 📦 Raggadon - RAG-Middleware-System

Ein RAG-Backend mit FastAPI, das Claude in Cursor ein projektbasiertes Gedächtnis verleiht.

## ✨ Features

- **Projektbasierte Speicherung**: Jede Nachricht wird projektsepariert gespeichert
- **OpenAI Embeddings**: Verwendet `text-embedding-3-small` für Vektorisierung
- **Supabase Backend**: Skalierbare Vektor-Datenbank mit Ähnlichkeitssuche
- **Budget-Tracking**: Automatische Token-Verbrauchsüberwachung pro Projekt
- **Type-Safe**: Vollständige Type Hints und Pydantic Models
- **Code Quality**: Black, Ruff und Pre-commit Hooks integriert

## 🏗️ Architektur

```
📦 Raggadon/
├── 🚀 main.py              # FastAPI App & Endpoints
├── 📋 requirements.txt     # Dependencies
├── 🔧 .env.example         # Umgebungsvariablen
├── 🛠️ .pre-commit-config.yaml
└── 📁 app/
    ├── 🧩 __init__.py
    ├── 🗄️ supabase_client.py  # Supabase Integration
    ├── 🧠 embedding.py        # OpenAI Embeddings
    └── 📊 usage.py            # Token Budget Tracking
```

## 🚀 Schnellstart

### 1. Installation

```bash
# Repository klonen
git clone <your-repo-url>
cd Raggadon

# Dependencies installieren
pip install -r requirements.txt

# Pre-commit hooks einrichten
pre-commit install
```

### 2. Umgebungsvariablen

```bash
# .env.example kopieren und ausfüllen
cp .env.example .env

# Erforderliche Variablen:
OPENAI_API_KEY=sk-your-openai-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-supabase-anon-key
```

### 3. Supabase Setup

Erstelle folgende Tabellen in deiner Supabase-Datenbank:

```sql
-- Projekt-Gedächtnis Tabelle
create table project_memory (
  id uuid primary key default gen_random_uuid(),
  project text not null,
  role text not null,
  content text not null,
  embedding vector(1536),
  created_at timestamp default now()
);

-- Usage Tracking Tabelle
create table embedding_usage (
  id uuid primary key default gen_random_uuid(),
  project text not null,
  usage_type text not null,     -- 'save' oder 'search'
  tokens integer not null,
  created_at timestamp default now()
);

-- RPC Function für Ähnlichkeitssuche
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  project_filter text
)
returns table (
  id uuid,
  project text,
  role text,
  content text,
  similarity float
)
language sql stable
as $$
  select
    project_memory.id,
    project_memory.project,
    project_memory.role,
    project_memory.content,
    1 - (project_memory.embedding <=> query_embedding) as similarity
  from project_memory
  where 
    project_memory.project = project_filter
    and 1 - (project_memory.embedding <=> query_embedding) > match_threshold
  order by project_memory.embedding <=> query_embedding
  limit match_count;
$$;
```

### 4. Server starten

```bash
# Development Server
uvicorn main:app --reload

# Oder direkt mit Python
python main.py
```

Server läuft auf: `http://localhost:8000`

API-Dokumentation: `http://localhost:8000/docs`

## 📡 API Endpoints

### POST /save
Speichert Projektinhalt mit Embedding

```bash
curl -X POST "http://localhost:8000/save" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "KibuBot",
    "role": "user",
    "content": "Claude sollte sich an diese wichtige Information erinnern."
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Inhalt für Projekt 'KibuBot' gespeichert",
  "tokens_used": 142,
  "monthly_project_usage": 4280,
  "estimated_cost_usd": 0.0856
}
```

### GET /search
Sucht ähnliche Inhalte im Projektgedächtnis

```bash
curl -X GET "http://localhost:8000/search?project=KibuBot&query=wichtige Information"
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid-here",
      "project": "KibuBot",
      "role": "user", 
      "content": "Claude sollte sich an diese wichtige Information erinnern.",
      "similarity": 0.89
    }
  ],
  "tokens_used": 89,
  "monthly_project_usage": 4369,
  "estimated_cost_usd": 0.0874
}
```

### GET /health
Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 🧾 Budget-Tracking

Jeder API-Aufruf trackt automatisch:
- Token-Verbrauch pro Request
- Monatlicher Verbrauch pro Projekt  
- Geschätzte Kosten (text-embedding-3-small: $0.00002/1K tokens)

Beispiel-Output im Terminal:
```
🧾 Tokenverbrauch: 4.280 Tokens (~$0.09) für Projekt "KibuBot"
```

## 🛠️ Entwicklung

### Code-Qualität

```bash
# Code formatieren
black .

# Linting
ruff check .

# Linting mit Auto-Fix
ruff check . --fix
```

### Pre-commit Hooks

```bash
# Hooks installieren
pre-commit install

# Manuell ausführen
pre-commit run --all-files
```

## 📊 Kosten-Übersicht

- **text-embedding-3-small**: $0.00002 per 1K tokens
- **Durchschnittlicher Satz**: ~150-200 tokens  
- **Kosten pro Speicherung**: ~$0.000003-0.000004
- **1000 Speicherungen**: ~$0.003-0.004

## 🔧 Projektstruktur

- `main.py` - FastAPI App und Endpoints
- `app/supabase_client.py` - Datenbank-Operationen
- `app/embedding.py` - OpenAI Embedding-Service
- `app/usage.py` - Token Budget-Tracking
- `requirements.txt` - Python Dependencies
- `.pre-commit-config.yaml` - Code Quality Hooks

## 🤝 Integration mit Claude/Cursor

1. Kopiere die API-URLs in dein Claude-Setup
2. Verwende `POST /save` um wichtige Projekt-Kontexte zu speichern
3. Verwende `GET /search` um relevante Informationen abzurufen
4. Jede Session kann ihren eigenen `project`-Namen verwenden