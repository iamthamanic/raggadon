# 📦 Raggadon - RAG-Middleware-System

Ein RAG-Backend mit FastAPI, das Claude in Cursor ein projektbasiertes Gedächtnis verleiht.

## ✨ Features

- **Projektbasierte Speicherung**: Jede Nachricht wird projektsepariert gespeichert
- **OpenAI Embeddings**: Verwendet `text-embedding-3-small` für Vektorisierung
- **Supabase Backend**: Skalierbare Vektor-Datenbank mit Ähnlichkeitssuche
- **Budget-Tracking**: Automatische Token-Verbrauchsüberwachung pro Projekt mit Kostenberechnung
- **Aktivitäts-Tracking**: Erste und letzte Nutzung pro Projekt mit exakten Zeitstempeln
- **CLI-Integration**: Globaler `rag` Befehl für einfache Nutzung in jedem Projekt
- **Auto-Start Service**: Automatischer Server-Start beim System-Login
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

### One-Line Installation

**Option 1: Mit eigenen API Keys**
```bash
curl -sSL https://raw.githubusercontent.com/iamthamanic/raggadon/main/install-blank.sh | bash
```

**Option 2: Mit vorkonfigurierten Keys (nur für @iamthamanic)**
```bash
curl -sSL https://raw.githubusercontent.com/iamthamanic/raggadon/main/install-preconfigured.sh | bash
```

### Manuelle Installation

```bash
# Repository klonen
git clone https://github.com/iamthamanic/raggadon.git
cd raggadon

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
- `app/supabase_client.py` - Datenbank-Operationen mit Aktivitäts-Tracking
- `app/embedding.py` - OpenAI Embedding-Service
- `app/usage.py` - Token Budget-Tracking und Statistiken
- `rag` - CLI-Tool für einfache Nutzung
- `install-*.sh` - Verschiedene Installer-Varianten
- `start_server.sh` - Server-Starter Script
- `install_service.sh` - Auto-Start Service Installer
- `requirements.txt` - Python Dependencies
- `.pre-commit-config.yaml` - Code Quality Hooks

## 🆕 Neue Features (v2.0)

### Erweiterte Statistiken
- **Kosten-Tracking**: Automatische Berechnung der OpenAI-Kosten
- **Aktivitäts-Timeline**: Erste und letzte Nutzung pro Projekt
- **Token-Verbrauch**: Monatliche Übersicht pro Projekt
- **Letzte Aktivitäten**: Historie der letzten save/search Operationen

### CLI-Verbesserungen
- **Zeitstempel-Format**: Exakte Datumsangaben (24.Juni.2025 - 13:41:30 Uhr)
- **Detaillierte Status-Ausgabe**: Umfassende Projekt-Informationen
- **Automatische Installation**: One-Liner Setup für neue Rechner

### Service-Integration
- **Auto-Start**: Server startet automatisch beim Login
- **Background-Betrieb**: Läuft dauerhaft im Hintergrund
- **Service-Management**: einfache Start/Stop Befehle

## 🤝 Integration mit Claude/Cursor

### Einfache CLI-Befehle

Nach der Installation des `rag` CLI-Tools kannst du Raggadon in jedem Projekt verwenden:

```bash
# In deinem Projekt (z.B. ~/MeinProjekt)
cd ~/MeinProjekt

# Wichtige Informationen speichern
rag save "Die Hauptdatenbank heißt production_db und läuft auf PostgreSQL"
rag save "Der API-Key ist in der .env Datei unter EXTERNAL_API_KEY"
rag save "Alle React-Komponenten liegen im src/components Ordner"

# Nach Informationen suchen
rag search "datenbank"
rag search "api key"
rag search "komponenten"

# Server-Status prüfen
rag status

# Server starten (falls nicht läuft)
rag start
```

**Wichtig:** Der Projektname wird automatisch aus dem aktuellen Ordnernamen ermittelt!

### CLI-Installation

```bash
# Einmalig installieren
cd ~/Desktop/ars\ vivai/Raggadon
./install_rag_cli.sh
source ~/.zshrc
```

### Service für automatischen Start

```bash
# Raggadon als Service installieren (startet automatisch bei Login)
./install_service.sh

# Service manuell steuern
launchctl start com.raggadon.server
launchctl stop com.raggadon.server
```

### Integration in Claude Code

Wenn du mit Claude Code arbeitest, kannst du Raggadon direkt in der Konversation nutzen:

**Verfügbare Befehle in Claude Code:**
- `rag status` - Zeigt erweiterte Server-Statistiken mit Kosten und Zeitangaben
- `rag save` - Claude speichert automatisch wichtige Infos aus dem Kontext
- `rag search <begriff>` - Sucht nach gespeicherten Informationen
- `rag summary` - Zeigt Zusammenfassung des Projekts
- `rag mode <modus>` - Steuert wie Claude über RAG-Operationen informiert

**RAG-Modi konfigurieren:**
```bash
rag mode active    # ✅ Claude zeigt alle RAG-Speicherungen an
rag mode silent    # 🔇 Arbeite im Hintergrund (Status mit 'rag status')
rag mode ask       # ❓ Frage vor jeder Operation
rag mode show      # 🔧 Zeige aktuellen Modus
```

**Erweiterte `rag status` Ausgabe:**
```
✅ Raggadon läuft auf http://127.0.0.1:8000
📁 Aktuelles Projekt: MeinProjekt

📊 Projekt-Statistiken:
   💾 Gespeicherte Einträge: 15
   🔤 Tokens diesen Monat: 2,847
   💰 Geschätzte Kosten: $0.0569
   🤖 Embedding Model: text-embedding-3-small
   💵 Preis: $0.02 pro 1K Tokens
   🕐 Erste Aktivität: 15.Juni.2025 - 09:23:45 Uhr
   🕐 Letzte Aktivität: 24.Juni.2025 - 13:41:30 Uhr

📋 Letzte Aktivitäten:
   • save: 142 Tokens
   • search: 89 Tokens
   • save: 156 Tokens
```

**Automatische Features:**
- Claude speichert proaktiv wichtige Code-Snippets und Entscheidungen
- Bei Fragen sucht Claude automatisch nach relevanten Infos in Raggadon
- Du wirst informiert, wenn relevante Informationen gefunden wurden

**Modi-Verhalten:**
- **✅ Active Mode:** Claude meldet jede RAG-Speicherung sofort
- **🔇 Silent Mode:** Claude arbeitet unsichtbar (Status mit `rag status` prüfen)
- **❓ Ask Mode:** Claude fragt vor jeder Speicherung um Erlaubnis

### Direkte API-Nutzung

Alternativ kannst du die API direkt verwenden:

1. Kopiere die API-URLs in dein Claude-Setup
2. Verwende `POST /save` um wichtige Projekt-Kontexte zu speichern
3. Verwende `GET /search` um relevante Informationen abzurufen
4. Jede Session kann ihren eigenen `project`-Namen verwenden
