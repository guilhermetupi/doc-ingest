# Doc Ingest

Microsserviço de ingestão de documentos — upload, parsing e armazenamento de arquivos PDF e Markdown.

## Tecnologias

| Camada | Biblioteca |
|---|---|
| Web framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via aiosqlite |
| Migrations | Alembic |
| Config | pydantic-settings |
| PDF parsing | PyPDF2 |
| Logging | structlog |

## Estrutura do projeto

```
src/doc_ingest/
├── main.py                    # FastAPI app — ponto de entrada
├── config/
│   └── env.py                 # Settings via .env (DATABASE_URL)
├── db/
│   ├── db.py                  # Engine assíncrono do SQLAlchemy
│   ├── database_session.py    # Decorator @database_session
│   └── models/
│       ├── base.py            # BaseModel (DeclarativeBase) + AuditModel
│       └── document.py        # DocumentModel (tabela documents)
├── entities/
│   └── document.py            # Entidade de domínio (Pydantic)
├── repositories/
│   ├── interfaces/
│   │   └── document.py        # IDocumentRepository (contrato)
│   ├── mappers/
│   │   └── document.py        # DocumentMapper: Model ↔ Entity
│   └── document.py            # DocumentRepository (implementação)
├── services/
│   ├── interface/
│   │   └── file_text_parser.py # IFileTextParser (contrato)
│   ├── document.py             # DocumentService (lógica de negócio)
│   └── file_text_parser.py     # FileTextParser (PDF e Markdown)
├── routes/
│   └── document.py             # Endpoints REST
└── dependencies/
    ├── repositories/
    │   └── document.py         # get_document_repository
    └── services/
        └── document.py         # get_document_service + get_file_text_parser
```

## Arquitetura

O projeto segue **Clean Architecture** com dependências apontando para dentro:

```
Routes ──→ Services ──→ Repository Interface ←── Repository Impl
                │                                    │
                ▼                                    ▼
            Entities ───────────────────────→ Mapper ──→ DB Model
```

Cada camada depende apenas de interfaces (contratos), nunca de implementações concretas. A injeção de dependências é feita via `FastAPI Depends`.

## Endpoints

### `GET /documents/`
Lista todos os documentos, ordenados por data de criação (mais recentes primeiro).

### `POST /documents/upload`
Faz upload de um arquivo. Corpo: `multipart/form-data`, campo `file`.

Validações:
- Tamanho máximo: 10 MB
- Content-Type aceito: `application/pdf`, `text/markdown`

### `GET /documents/{id}`
Retorna um documento específico por UUID.

## Fluxo de uma requisição

```
POST /documents/upload (multipart file)
  → Route: valida Content-Type e tamanho
  → FileTextParser: extrai texto do PDF/Markdown
  → Document.create(): gera entidade com UUID e timestamps
  → DocumentRepository.create_document(): persiste no banco
  ← Document (JSON)
```

## Setup

```bash
# Dependências
uv sync

# Variáveis de ambiente
cp .env.example .env   # editar DATABASE_URL se necessário

# Migrations
alembic upgrade head

# Executar
uv run doc-ingest
```