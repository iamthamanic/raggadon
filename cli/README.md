# Raggadon CLI

**NPM package for Raggadon RAG system** - Provides project-based memory for AI assistants like Claude Code.

## Installation

### Global Installation
```bash
npm install -g raggadon
raggadon status
```

### NPX (No Installation)
```bash
npx raggadon status
npx raggadon save "important information"
```

## Quick Start

1. **Initialize in your project:**
   ```bash
   cd your-project
   npx raggadon init
   ```

2. **Save important information:**
   ```bash
   npx raggadon save "User authentication uses JWT tokens"
   npx raggadon save "API endpoint: POST /api/auth/login"
   ```

3. **Search your project memory:**
   ```bash
   npx raggadon search "authentication"
   npx raggadon search "API endpoints"
   ```

4. **Check status:**
   ```bash
   npx raggadon status
   ```

## Commands

### `npx raggadon save <content>`
Stores important information for the current project with semantic search capabilities.

**Example:**
```bash
npx raggadon save "The user model has fields: email, name, role, created_at"
```

### `npx raggadon search <query>`
Searches for similar content in the current project using vector similarity.

**Example:**
```bash
npx raggadon search "user model"
# Returns relevant information about user-related code
```

### `npx raggadon status`
Shows server status, project statistics, token usage, and costs.

**Output includes:**
- Server health status
- Current project name
- Operating mode (active/silent/ask)
- Memory entries count
- Monthly token usage and costs
- Recent activity

### `npx raggadon init`
Initializes Raggadon for the current project by copying `CLAUDE.md` configuration.

### `npx raggadon mode <mode>`
Changes the auto-save behavior mode.

**Modes:**
- `active` - Claude shows all RAG operations (default)
- `silent` - Works in background, check with `status`
- `ask` - Ask before each operation
- `show` - Display current mode

### `npx raggadon start`
Starts the Raggadon server (if installed locally).

## Requirements

- **Raggadon Server:** Must be running on `http://127.0.0.1:8001`
- **Node.js:** Version 16 or higher
- **Backend:** Supabase with pgvector + OpenAI API

## How It Works

1. **Project Detection:** Uses current directory name as project identifier
2. **Content Storage:** Converts text to embeddings using OpenAI's `text-embedding-3-small`
3. **Vector Search:** Uses PostgreSQL + pgvector for similarity search
4. **Cost Tracking:** Monitors token usage and estimates costs

## Cost Structure

- **Model:** `text-embedding-3-small` (1536 dimensions)
- **Rate:** $0.02 per 1,000 tokens
- **Typical save:** ~150-200 tokens (~$0.000003-0.000004)
- **Monthly budget:** Usually under $0.01 for normal usage

## Claude Code Integration

When you run `npx raggadon init`, it adds a `CLAUDE.md` file that instructs Claude Code to:
- Automatically save important code definitions
- Search project memory before answering questions
- Store architecture decisions and configurations
- Track TODOs and bug fixes

## Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────┐
│  NPX Package    │ ──────────────→ │  Raggadon Server │
│  (CLI Client)   │                 │  FastAPI + Poetry│
│                 │ ←────────────── │  + Supabase      │
│                 │                 │  + OpenAI        │
└─────────────────┘                 └──────────────────┘
                                    
Server Dependencies:
• Poetry (dev) / pip (production)
• Python 3.9+
• FastAPI + uvicorn
• Supabase + pgvector
```

## Examples

**Development Workflow:**
```bash
# Start new project
cd my-awesome-app
npx raggadon init

# Save key information as you code
npx raggadon save "Uses React 18 with TypeScript and Vite"
npx raggadon save "API endpoints defined in src/api/routes.ts"
npx raggadon save "Authentication middleware in src/middleware/auth.ts"

# Search when you need context
npx raggadon search "authentication"
npx raggadon search "API structure"

# Check your usage
npx raggadon status
```

**Team Collaboration:**
```bash
# Each team member can access shared project memory
npx raggadon search "deployment process"
npx raggadon search "database schema"
```

## Troubleshooting

**Server not running:**
```bash
npx raggadon status
# Shows: ❌ Raggadon läuft nicht!
```

**Solution:** Start the Raggadon server or check your installation.

**No results found:**
- Check if you're in the correct project directory
- Verify you've saved information with `npx raggadon save`
- Try broader search terms

## License

MIT

## Repository

[https://github.com/iamthamanic/raggadon](https://github.com/iamthamanic/raggadon)