# Setup Guide

## Prerequisites

- Docker and Docker Compose
- Node.js (via nvm) - for local development
- Python 3.11+ - for local development
- API Keys:
  - OpenAI API key OR Anthropic API key
  - CurricuLLM-AU API key (optional, will use mock data if not provided)

## Quick Start with Docker

1. **Clone and navigate to the project:**
   ```bash
   cd script-foundary
   ```

2. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **View logs:**
   ```bash
   docker-compose logs -f
   ```

6. **Stop services:**
   ```bash
   docker-compose down
   ```

## Local Development Setup

### Backend

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Use nvm for Node.js:**
   ```bash
   source ~/.nvm/nvm.sh
   nvm use --lts
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

5. **Access frontend:**
   - http://localhost:3000

## Running Tests

```bash
# From project root
cd backend
pytest ../tests/
```

## Project Structure

```
script-foundary/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app entry
│   │   ├── config.py    # Configuration
│   │   ├── pipeline/    # Pipeline modules
│   │   ├── services/    # External API clients
│   │   └── models/      # Data models
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── components/ # React components
│   │   └── page.tsx    # Main page
│   └── package.json
├── data/                # Static data
│   └── misconceptions/  # Misconception database
├── tests/               # Test files
└── docker-compose.yml   # Docker orchestration
```

## Environment Variables

Required environment variables (in `backend/.env`):

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM API key
- `CURRICULLM_API_KEY` - CurricuLLM-AU API key (optional)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (optional)

See `backend/.env.example` for all available options.

## Features

The system includes 6 modular features that can be enabled/disabled:

1. **Curriculum Aligner** - Aligns content with Australian curriculum
2. **Misconception Checker** - Detects and addresses common misconceptions
3. **Script Generator** - Core LLM-based script generation
4. **Fact Checker** - Verifies factual claims
5. **Cultural Safety Checker** - Ensures inclusive content
6. **Accessibility Generator** - Creates accessibility features

All features can be toggled via the frontend form or backend configuration.

## Troubleshooting

### Docker Issues

- **Port already in use:** Change ports in `docker-compose.yml`
- **Permission errors:** Ensure Docker has proper permissions
- **Build failures:** Check Docker logs with `docker-compose logs`

### Backend Issues

- **Import errors:** Ensure virtual environment is activated
- **API key errors:** Check `.env` file is properly configured
- **Database errors:** Ensure PostgreSQL is running (if not using Docker)

### Frontend Issues

- **npm install fails:** Use nvm to ensure correct Node.js version
- **API connection errors:** Check `NEXT_PUBLIC_API_URL` matches backend URL
- **Build errors:** Clear `.next` directory and rebuild

## Next Steps

1. Add your API keys to `backend/.env`
2. Start the services with Docker or locally
3. Test script generation with a sample topic
4. Review generated scripts and adjust prompts as needed
5. Add more misconceptions to `data/misconceptions/`



