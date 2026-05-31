# Doc Ingest

Document ingestion microservice — upload, parsing, and storage of PDF and Markdown files.

## Technologies

| Layer | Library |
|---|---|
| Web framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via aiosqlite |
| Migrations | Alembic |
| Config | pydantic-settings |
| PDF parsing | pypdf |
| Logging | structlog |

## Project Structure

```
src/doc_ingest/
├── main.py                    # FastAPI app — entry point
├── config/
│   └── env.py                 # Settings via .env (DATABASE_URL)
├── db/
│   ├── db.py                  # SQLAlchemy async engine
│   ├── database_session.py    # @database_session decorator
│   └── models/
│       ├── base.py            # BaseModel (DeclarativeBase) + AuditModel
│       └── document.py        # DocumentModel (documents table)
├── entities/
│   └── document.py            # Domain entity (Pydantic)
├── repositories/
│   ├── interfaces/
│   │   └── document.py        # IDocumentRepository (contract)
│   ├── mappers/
│   │   └── document.py        # DocumentMapper: Model ↔ Entity
│   └── document.py            # DocumentRepository (implementation)
├── services/
│   ├── interface/
│   │   └── file_text_parser.py # IFileTextParser (contract)
│   ├── document.py             # DocumentService (business logic)
│   └── file_text_parser.py     # FileTextParser (PDF and Markdown)
├── routes/
│   └── document.py             # REST endpoints
└── dependencies/
    ├── repositories/
    │   └── document.py         # get_document_repository
    └── services/
        └── document.py         # get_document_service + get_file_text_parser
```

## Architecture

The project follows **Clean Architecture** with dependencies pointing inward:

```
Routes ──→ Services ──→ Repository Interface ←── Repository Impl
                │                                    │
                ▼                                    ▼
            Entities ───────────────────────→ Mapper ──→ DB Model
```

Each layer depends only on interfaces (contracts), never on concrete implementations. Dependency injection is handled via `FastAPI Depends`.

## Endpoints

### `GET /documents/`
Lists all documents, ordered by creation date (most recent first).

### `POST /documents/upload`
Uploads a file. Body: `multipart/form-data`, field `file`.

Validations:
- Maximum size: 10 MB
- Accepted Content-Type: `application/pdf`, `text/markdown`

### `GET /documents/{id}`
Returns a specific document by UUID.

## Request Flow

```
POST /documents/upload (multipart file)
  → Route: validates Content-Type and size
  → FileTextParser: extracts text from PDF/Markdown
  → Document.create(): generates entity with UUID and timestamps
  → DocumentRepository.create_document(): persists to database
  ← Document (JSON)
```

## Setup

```bash
# Dependencies
uv sync

# Environment variables
cp .env.example .env   # edit DATABASE_URL if needed

# Migrations
alembic upgrade head

# Run
uv run doc-ingest
```

## Tests

### Structure

```
tests/
├── conftest.py                              # Shared fixtures (in-memory engine, table creation/cleanup)
├── unit/
│   ├── config/
│   │   └── test_env.py                      # Settings (pydantic-settings)
│   ├── entities/
│   │   └── test_document.py                 # Document entity (create, reconstitute, serialization)
│   ├── repositories/
│   │   ├── test_document_mapper.py          # DocumentMapper (to_model, to_entity)
│   │   └── test_document_repository.py      # DocumentRepository with in-memory database
│   └── services/
│       ├── test_document_service.py          # DocumentService (with mocked repo and parser)
│       └── test_file_text_parser.py          # FileTextParser (real Markdown, mocked PDF)
└── integration/
    └── test_document_routes.py               # REST endpoints (httpx ASGITransport + dependency overrides)
```

### Running

```bash
# Sync dependencies (including dev)
uv sync --group dev

# Run all tests
uv run pytest -v

# By layer
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

| Layer | Strategy |
|---|---|
| Entity / Mapper / Config | Pure tests, no external dependencies |
| Service | Mocks via `unittest.mock` (AsyncMock for async methods) |
| Repository | In-memory SQLite database with `StaticPool` (real engine, data isolated per test) |
| Routes | `httpx.ASGITransport` + `app.dependency_overrides` (no real server) |
