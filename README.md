# AI Educational Script Generator

An evidence-based, modular pipeline system for generating educational video scripts with curriculum alignment, misconception checking, fact verification, and accessibility features.

## Features

1. **Pedagogical Template Engine** - FAME framework (Fading, Alternating, Mistakes, Explanation)
2. **Curriculum Alignment** - Integration with CurricuLLM-AU API
3. **Misconception Checker** - Detects and addresses common student misconceptions
4. **Hallucination Safeguard** - Fact-checking against verified sources
5. **Cultural Safety Checker** - Ensures inclusive and culturally sensitive content
6. **Accessibility Generator** - Auto-generates ALT text, captions, and dyslexia-friendly formatting

## Architecture

- **Frontend**: Next.js (App Router)
- **Backend**: FastAPI with modular pipeline architecture
- **Database**: Supabase (PostgreSQL)
- **Vector Store**: FAISS (local) or Pinecone
- **APIs**: CurricuLLM-AU, OpenAI/Anthropic, Brave Search

## Quick Start

### Using Docker (Recommended)

```bash
# Set up environment (creates .env file if it doesn't exist)
make setup

# Edit backend/.env with your API keys
# Then start all services
make docker-up

# Or manually:
# docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# View logs
make docker-logs

# Stop services
make docker-down
```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `backend/.env.example` for required environment variables:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `CURRICULLM_API_KEY`
- `BRAVE_SEARCH_API_KEY` (for fact-checking)
- `DATABASE_URL` (Supabase connection string)
- `REDIS_URL` (optional, for caching) - Supports `redis://` and `rediss://` (SSL/TLS) for services like Upstash. Or use `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, `REDIS_PASSWORD`, `REDIS_SSL` separately

## Project Structure

```
script-foundary/
├── frontend/          # Next.js application
│   ├── app/           # Next.js app directory
│   │   ├── components/ # React components
│   │   └── page.tsx   # Main page
│   └── lib/           # Utilities and API client
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── main.py    # FastAPI app entry
│   │   ├── pipeline/  # Pipeline modules
│   │   ├── services/  # External API clients
│   │   └── models/    # Data models
│   └── scripts/        # Utility scripts
├── data/              # Static data & seeds
│   └── misconceptions/ # Misconception database
├── tests/             # Test files
├── docker-compose.yml  # Docker orchestration
└── Makefile           # Convenience commands
```

## Available Commands

See `Makefile` for all available commands:

- `make setup` - Set up environment files
- `make docker-up` - Start all services
- `make docker-down` - Stop all services
- `make docker-logs` - View logs
- `make test` - Run tests
- `make init-db` - Initialize database tables
- `make seed-misconceptions` - Seed misconceptions database

## Development

The system uses a modular pipeline architecture where each feature is a pluggable module. Modules can be enabled/disabled via configuration.

## License

MIT


