# RepoLens AI — Agentic GitHub Codebase Explorer

> An intelligent, agentic developer tool that allows engineers to submit any public GitHub repository URL and query its architectural patterns, symbol hierarchies, dependencies, and execution flows using natural language.

---

## 🏛️ System Architecture

RepoLens AI is architected as a modular monorepo cleanly separating the client application from the backend intelligence engine:

```
repolens-ai/
├── .env.example              # Monorepo environment blueprint
├── .gitignore                # Production ignore rules (secrets, venvs, cache, data)
├── README.md                 # Project architecture and documentation
│
├── backend/                  # FastAPI 3.11+ intelligence backend
│   ├── .env.example          # Backend configuration contract
│   ├── requirements.txt      # Core runtime dependencies
│   ├── requirements-dev.txt  # Testing and development tools
│   ├── pytest.ini            # Pytest configuration
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint, lifespan, CORS & middleware
│   │   ├── core/             # Central configuration, errors, logging & DI
│   │   │   ├── config.py     # Pydantic Settings & environment validation
│   │   │   ├── errors.py     # Centralized exception handlers & error envelopes
│   │   │   ├── logging.py    # Structured logging
│   │   │   └── dependencies.py # FastAPI dependency injection providers
│   │   ├── api/              # API routers and versioning
│   │   │   ├── router.py     # Root /api aggregator
│   │   │   └── routes/
│   │   │       └── health.py # GET /api/health endpoint
│   │   ├── schemas/          # Pydantic v2 data contracts
│   │   │   ├── common.py     # Response envelopes & health status models
│   │   │   ├── repository.py # Repository ingestion models
│   │   │   └── query.py      # Q&A, citation, and trace models
│   │   ├── services/         # Business logic layer
│   │   │   ├── base.py       # Base service abstraction
│   │   │   └── health_service.py # Health diagnostics and uptime tracking
│   │   ├── ingestion/        # (Phase 2) Git CLI cloning & shallow fetch contracts
│   │   │   └── base.py       # BaseRepositoryIngestionService interface
│   │   ├── parsing/          # (Phase 2) Python AST & Tree-sitter parsers
│   │   │   └── base.py       # BaseCodeParser, CodeSymbol & ParsedFile
│   │   ├── retrieval/        # (Phase 3) SentenceTransformers & ChromaDB store
│   │   │   └── base.py       # BaseVectorStore & SearchResult contracts
│   │   ├── agents/           # (Phase 4) LangGraph orchestration contracts
│   │   │   └── base.py       # BaseCodebaseAgent reasoning interface
│   │   ├── mcp/              # (Phase 5) FastMCP tools server registry
│   │   │   └── server.py     # MCPToolRegistry interface
│   │   └── utils/            # Path security & formatters
│   │       └── path_helpers.py # Safe path resolution & directory traversal guards
│   └── tests/
│       ├── conftest.py       # Pytest fixtures and TestClient initialization
│       └── test_health.py    # Health, CORS, error handling & path security tests
│
└── frontend/                 # React 18 + TypeScript + Vite + Tailwind client
    ├── .env.example          # Frontend configuration contract
    ├── package.json          # Dependencies and npm scripts
    ├── tsconfig.json         # Strict TypeScript compiler options
    ├── vite.config.ts        # Vite configuration with Vitest setup
    ├── tailwind.config.js    # Developer-tool dark theme palette
    ├── src/
    │   ├── main.tsx          # React application DOM entrypoint
    │   ├── App.tsx           # Route provider and application layout
    │   ├── index.css         # Tailwind directives and custom scrollbars
    │   ├── types/            # TypeScript interfaces
    │   ├── services/         # Axios API client with interceptors
    │   ├── components/
    │   │   ├── common/       # StatusBadge, MetricCards
    │   │   └── layout/       # AppShell, Header, Sidebar
    │   └── pages/
    │       ├── DashboardPage.tsx # Overview, live diagnostics, repo submission preview
    │       ├── ExplorerPage.tsx  # AST & repository explorer workspace (Phase 2 stub)
    │       └── SettingsPage.tsx  # Runtime configuration viewer
    └── tests/
        ├── setup.ts          # Jest-DOM matchers setup
        ├── App.test.tsx      # Main application smoke and routing tests
        └── StatusBadge.test.tsx # UI component unit tests
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Axios |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Pydantic Settings, Uvicorn |
| **AI Orchestration** | LangGraph *(Phase 4)* |
| **LLM Provider** | Groq API (`llama-3.3-70b-versatile`) *(Phase 4)* |
| **Embeddings & DB** | SentenceTransformers (`all-MiniLM-L6-v2`), ChromaDB *(Phase 3)* |
| **Code Parsing** | Python AST *(Phase 3)*, Tree-sitter *(Phase 3+)* |
| **Repository Management** | Git CLI *(Implemented - Phase 2)* |
| **Agent Protocol** | FastMCP *(Phase 5)* |
| **Testing** | Pytest + pytest-asyncio + HTTPX (backend), Vitest + React Testing Library (frontend) |

---

## 📡 API Endpoints

### System & Diagnostics
- `GET /api/health`: System status, version, uptime, and storage diagnostics.

### Repository Ingestion & Inspection (Phase 2)
- `POST /api/repositories`: Ingest a public GitHub repository.
  ```json
  {
    "github_url": "https://github.com/psf/requests",
    "branch": "main" // Optional
  }
  ```
- `GET /api/repositories`: List all previously ingested repositories.
- `GET /api/repositories/{repository_id}`: Retrieve repository metadata, commit SHA, file count, detected languages, and README status.
- `GET /api/repositories/{repository_id}/files`: Retrieve all discovered source code and documentation files.

---

## 🚀 Quickstart & Local Development

### Prerequisites

- **Python**: `>= 3.11` (Python 3.13 tested)
- **Node.js**: `>= 18.0.0` (Node.js 22 tested)
- **Git**: Installed and available in PATH

---

### 1. Repository Setup

```bash
cd repolens-ai

# Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

# Frontend setup
cd ../frontend
npm install
cp .env.example .env
```

---

### 2. Running the Backend

From `repolens-ai/backend`:

```bash
# Activate virtual environment if not already activated
source .venv/bin/activate

# Run FastAPI development server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Health check**: `http://localhost:8000/api/health`
- **Interactive OpenAPI documentation**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

---

### 3. Running the Frontend

From `repolens-ai/frontend`:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

---

### 4. Running Tests

#### Backend Pytest Suite

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Tests verify:
- Health check endpoint `GET /api/health` payload structure and response code
- Explicit CORS allowlist origin validation and unlisted origin rejection
- Centralized JSON error handling envelopes for 404 and unhandled errors
- Path traversal protection and repository ID sanitization
- Pydantic Settings parsing of comma-separated and JSON string formats

#### Frontend Vitest Suite

```bash
cd frontend
npm test
```

Tests verify:
- Application shell navigation and branding rendering
- Dashboard hero and URL validation input
- Status badge health indicators and styling
- Mocked backend health integration

#### Production Frontend Build

```bash
cd frontend
npm run build
```

---

## 🔒 Security & Engineering Best Practices

1. **Explicit CORS Allowlist**: Only origins declared in `CORS_ORIGINS` (defaults to `http://localhost:5173`) are permitted.
2. **Centralized Error Handling**: All HTTP exceptions, schema validation errors, and uncaught exceptions are normalized into a standardized `{ success: false, error: { code, message, details } }` envelope.
3. **Strict Validation & No Hardcoded Secrets**: Configuration is managed via Pydantic Settings reading exclusively from `.env` files.
4. **Path Traversal Guards**: The filesystem helper `resolve_safe_path` enforces that all operations on repositories stay strictly within the assigned data directory.
5. **Clean Modularity**: The codebase adheres to strict separation of concerns, providing well-defined abstract interfaces for ingestion, parsing, retrieval, agents, and MCP without premature overengineering.
