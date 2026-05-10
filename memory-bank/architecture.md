# Architecture Memory

This file is the source of truth for the implemented architecture. It must be read before any code is written and updated after every major feature, milestone, schema change, API change, module-boundary change, or data-flow change.

## Current Status

- Implementation status: Phase 2 backend minimal skeleton completed and verified.
- Codebase status: FastAPI backend entrypoint, health route, centralized settings, structured errors, in-memory task status service, and backend tests exist; no database persistence, upload flow, parsing, graph, RAG, or frontend runtime code has been implemented yet.
- Database status: SQLite is selected, but the final schema will be defined and updated incrementally during implementation.
- Required product source: `memory-bank/design-document.md`.
- Required execution source: `memory-bank/implementation-plan.md`.
- Required technical source: `memory-bank/tech-stack.md`.
- Progress tracker: `memory-bank/progress.md`.

## Architecture Principles

- Use a modular monolith, not microservices.
- Keep backend route handlers thin and put business logic in service modules.
- Keep frontend API calls outside UI components.
- Keep prompts in dedicated prompt files or prompt-focused service modules.
- Keep generated runtime data out of git.
- Do not create monolithic giant files.
- Prefer simple, reliable implementation over broad framework abstractions.

## Selected Tech Stack

- Frontend: React, Vite, TypeScript.
- Frontend graph visualization: Cytoscape.js.
- Backend: FastAPI.
- Database: SQLite.
- File storage: local filesystem under `data/`.
- Vector index: FAISS.
- Keyword search: rank-bm25 as an optional enhancement.
- LLM and embedding access: OpenAI-compatible provider interface.
- Background jobs: FastAPI BackgroundTasks for the initial implementation.
- Configuration: `.env` and `.env.example`.

## Implemented Top-Level Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── router.py
│   │   │   ├── tasks.py
│   │   │   └── .gitkeep
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   ├── task_status.py
│   │   │   └── .gitkeep
│   │   ├── models/
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── tasks.py
│   │   │   └── .gitkeep
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py
│   │   │   └── .gitkeep
│   │   ├── prompts/
│   │   ├── storage/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── .gitkeep
│   ├── tests/
│   │   └── test_phase2_backend_skeleton.py
│   ├── requirements.txt
│   └── .gitkeep
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── textbooks/
│   │   │   ├── graph/
│   │   │   ├── integration/
│   │   │   ├── rag/
│   │   │   ├── chat/
│   │   │   └── report/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── .gitkeep
│   └── .gitkeep
├── data/
│   ├── uploads/
│   ├── parsed/
│   ├── graphs/
│   ├── indexes/
│   ├── reports/
│   └── .gitkeep
├── memory-bank/
├── report/
├── .env.example
├── .gitignore
└── AGENTS.md
```

Future implementation steps are expected to add database modules, upload/parsing services, `frontend/package.json`, `frontend/src/App.tsx`, and README/docs. They do not exist yet because Phase 2 only establishes the minimal backend skeleton.

## Phase 1 File Roles

| File | Role |
| --- | --- |
| `.gitignore` | Keeps local secrets, uploaded textbooks, PDFs, SQLite databases, vector indexes, dependency folders, caches, and generated runtime artifacts out of git while allowing directory placeholders. |
| `.env.example` | Documents the OpenAI-compatible provider settings, model names, `DATA_DIR`, and `DATABASE_URL` expected by later backend configuration code. |
| `AGENTS.md` | Repository-level AI coding rules. It requires reading `memory-bank/architecture.md` and `memory-bank/design-document.md` before code changes and keeping architecture memory current. |
| `backend/.gitkeep` | Retains the backend root in git alongside the Phase 2 backend files. |
| `backend/app/.gitkeep` | Retains the backend application package root in git alongside runtime modules. |
| `backend/app/api/.gitkeep` | Retains the HTTP route directory in git alongside implemented route modules. |
| `backend/app/core/.gitkeep` | Retains the backend core directory in git alongside implemented configuration, error, and status modules. |
| `backend/app/models/.gitkeep` | Tracks the future SQLite model and persistence access boundary. |
| `backend/app/schemas/.gitkeep` | Retains the schema directory in git alongside implemented response and task schemas. |
| `backend/app/services/.gitkeep` | Retains the service directory in git alongside the implemented task service. |
| `backend/app/prompts/.gitkeep` | Tracks the future prompt-template boundary for LLM tasks. |
| `backend/app/storage/.gitkeep` | Tracks the future local storage helper boundary. |
| `frontend/.gitkeep` | Tracks the frontend root before Vite package files are added. |
| `frontend/src/.gitkeep` | Tracks the frontend source root before React source files are added. |
| `frontend/src/api/.gitkeep` | Tracks the future typed frontend API client boundary. |
| `frontend/src/components/.gitkeep` | Tracks the future reusable presentation component boundary. |
| `frontend/src/features/textbooks/.gitkeep` | Tracks the future textbook upload, file list, parsing status, and chapter tree feature area. |
| `frontend/src/features/graph/.gitkeep` | Tracks the future Cytoscape graph canvas, search, and node details feature area. |
| `frontend/src/features/integration/.gitkeep` | Tracks the future integration decision and compression statistics feature area. |
| `frontend/src/features/rag/.gitkeep` | Tracks the future RAG question, answer, citation, and source chunk feature area. |
| `frontend/src/features/chat/.gitkeep` | Tracks the future teacher feedback conversation feature area. |
| `frontend/src/features/report/.gitkeep` | Tracks the future report generation and preview feature area. |
| `frontend/src/hooks/.gitkeep` | Tracks the future frontend state and polling hooks boundary. |
| `frontend/src/types/.gitkeep` | Tracks the future shared TypeScript type boundary. |
| `data/.gitkeep` | Tracks the runtime data root while generated contents remain ignored. |
| `data/uploads/.gitkeep` | Tracks the upload storage directory while uploaded textbooks remain ignored. |
| `data/parsed/.gitkeep` | Tracks the parsed artifact directory while generated parsed files remain ignored. |
| `data/graphs/.gitkeep` | Tracks the graph artifact directory while generated graph files remain ignored. |
| `data/indexes/.gitkeep` | Tracks the vector index directory while generated FAISS/index files remain ignored. |
| `data/reports/.gitkeep` | Tracks the generated report artifact directory while generated report files remain ignored. |
| `report/.gitkeep` | Tracks the final human-facing report directory before `report/整合报告.md` is generated in a later phase. |

## Phase 2 Backend File Roles

| File | Role |
| --- | --- |
| `backend/requirements.txt` | Minimal backend dependency list for the Phase 2 FastAPI skeleton: FastAPI, Uvicorn, multipart support, Pydantic, and pydantic-settings. |
| `backend/app/__init__.py` | Marks `app` as the backend Python package. |
| `backend/app/main.py` | FastAPI entrypoint. Defines `create_app()`, registers error handlers, includes the API router, and exposes the module-level `app` used by Uvicorn. |
| `backend/app/api/__init__.py` | Marks the backend route package. |
| `backend/app/api/router.py` | Aggregates backend routers so `main.py` has one route inclusion point. |
| `backend/app/api/health.py` | Thin health route module. `GET /health` returns basic service status and app name from centralized settings. |
| `backend/app/api/tasks.py` | Thin simulated task route module. Exposes create, read, and fail endpoints under `/api/tasks/*` and delegates logic to `TaskService`. |
| `backend/app/core/__init__.py` | Marks the backend core package. |
| `backend/app/core/config.py` | Centralized settings loader. Uses `pydantic-settings` when installed and a small environment fallback otherwise; exposes cached `get_settings()` and `clear_settings_cache()` for tests. |
| `backend/app/core/errors.py` | Shared application error type and FastAPI exception handlers. All handled errors return `{"error": {"code": "...", "message": "...", "details": ...}}`. |
| `backend/app/core/task_status.py` | Canonical task status enum with `pending`, `running`, `completed`, and `failed`. |
| `backend/app/schemas/__init__.py` | Marks the typed schema package. |
| `backend/app/schemas/health.py` | Pydantic response schema for the health endpoint. |
| `backend/app/schemas/tasks.py` | Pydantic request and response schemas for simulated task operations. |
| `backend/app/services/__init__.py` | Marks the backend service package. |
| `backend/app/services/task_service.py` | In-memory task service for Phase 2. It creates simulated pending tasks, retrieves tasks, marks tasks failed, and raises structured `AppError` for missing task IDs. This is intentionally non-persistent until Phase 3. |
| `backend/tests/test_phase2_backend_skeleton.py` | Phase 2 verification tests covering health, environment override behavior, structured error envelopes, and simulated task create/read/fail behavior. |

## Backend Startup And Verification

The backend app object is `app.main:app` when `PYTHONPATH=backend` is set. A local developer can start the Phase 2 backend with:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

Phase 2 verification command:

```bash
PYTHONPATH=backend pytest backend/tests
```

Current verified result: 5 tests passed.

## Planned Backend Modules

| Module | Responsibility |
| --- | --- |
| `api/` | HTTP routes and request/response boundaries. |
| `core/` | Configuration, app setup, shared errors, task status constants. |
| `models/` | SQLite persistence models or database access structures. |
| `schemas/` | Typed request/response and domain schemas. |
| `services/parsing` | PDF, Markdown, TXT, and optional DOCX parsing. |
| `services/graph` | Knowledge node and edge extraction orchestration. |
| `services/integration` | Cross-textbook alignment, merge/keep/remove decisions, compression stats. |
| `services/rag` | Chunking, embedding, FAISS index management, retrieval, answer generation. |
| `services/chat` | Teacher feedback, conversation persistence, decision updates. |
| `services/reporting` | Markdown report generation. |
| `prompts/` | LLM prompts for extraction, alignment, RAG answering, and feedback interpretation. |
| `storage/` | Local file storage, uploaded files, generated artifacts, index files. |

## Implemented Backend API Surface

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check returning `status` and configured `app_name`. |
| `POST` | `/api/tasks/simulated` | Creates an in-memory simulated task in `pending` status. |
| `GET` | `/api/tasks/{task_id}` | Retrieves a simulated task by ID or returns a structured `task_not_found` error. |
| `POST` | `/api/tasks/{task_id}/fail` | Marks a simulated task as `failed` with a provided `error_message`. |

## Implemented Backend Conventions

- Configuration is centralized in `backend/app/core/config.py`.
- Environment variables currently supported by settings are `DATA_DIR`, `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`, and `EMBEDDING_MODEL`.
- Application errors and validation errors use one envelope shape: `{"error": {"code": string, "message": string, "details": optional}}`.
- Phase 2 task state is in-memory only. It proves the status contract and API shape; durable task persistence belongs to Phase 3.

## Planned Frontend Modules

| Module | Responsibility |
| --- | --- |
| `api/` | Typed client functions for backend endpoints. |
| `components/` | Reusable presentation components. |
| `features/textbooks` | Upload, file list, parsing status, chapter tree. |
| `features/graph` | Cytoscape graph canvas, node details, search, visual encoding. |
| `features/integration` | Integration decisions, compression stats, manual decision controls. |
| `features/rag` | Question input, answer view, citations, source chunk expansion. |
| `features/chat` | Teacher feedback conversation and history. |
| `features/report` | Report generation and preview. |
| `hooks/` | Feature-specific state and polling hooks. |
| `types/` | Shared frontend TypeScript types matching backend schemas. |

## Planned Data Flow

1. User uploads one or more textbooks through the frontend.
2. Backend stores uploaded files under `data/uploads/` and creates textbook records.
3. Parser extracts structured chapters and stores chapter records.
4. Knowledge extraction service processes chapters and stores graph nodes and edges.
5. Graph endpoint returns textbook graph data to the frontend Cytoscape canvas.
6. Integration service aligns cross-textbook nodes, creates decisions, and computes compression stats.
7. RAG service chunks textbook content, creates embeddings, builds a FAISS index, and stores chunk metadata.
8. RAG query retrieves top chunks and sends only retrieved context to the LLM.
9. Answer service returns answer text with citations backed by chunk metadata.
10. Teacher feedback service updates integration decisions and triggers graph/stat refresh.
11. Report service generates `report/整合报告.md` from stored system data.

## Database Strategy

The final SQLite schema will be defined during implementation and must be updated here before or alongside schema implementation. Database structure can evolve step by step, but code must not invent fields without updating this file.

Planned entities:

| Entity | Purpose |
| --- | --- |
| `textbooks` | Uploaded textbook metadata, file info, parse status, total pages, total characters. |
| `chapters` | Parsed chapter structure with page range, content, and character count. |
| `graph_nodes` | Extracted knowledge points with definition, category, source chapter, page, and source excerpt. |
| `graph_edges` | Relationships between knowledge points. |
| `integration_decisions` | Merge, keep, and remove decisions with reasons, confidence, and status. |
| `merged_nodes` | Result nodes after cross-textbook integration. |
| `rag_chunks` | Chunk text and metadata for retrieval and citation. |
| `chat_sessions` | Teacher feedback session metadata. |
| `chat_messages` | User and assistant messages for feedback history. |
| `tasks` | Background task status, progress, error message, and timestamps. |

## File Storage Strategy

Runtime files live under `data/` and must not be committed.

Implemented Phase 1 storage directories:

```text
data/
  uploads/
  parsed/
  graphs/
  indexes/
  reports/
```

The `.gitignore` policy ignores generated files under these directories while keeping only `.gitkeep` placeholders tracked.

## API Surface Draft

These API groups are planned and may be refined during implementation:

| Group | Purpose |
| --- | --- |
| `/api/textbooks/*` | Upload, list, parse, and inspect textbooks. |
| `/api/graph/*` | Build and retrieve textbook or merged graph data. |
| `/api/integration/*` | Run integration, list decisions, update decisions, retrieve compression stats. |
| `/api/rag/*` | Build index, get index status, query with citations. |
| `/api/chat/*` | Teacher feedback conversation and history. |
| `/api/report/*` | Generate and retrieve integration reports. |

## Open Decisions

- Exact SQLite table columns will be finalized incrementally during implementation.
- The first implementation may use mock LLM outputs only if explicitly approved for MVP bootstrapping.
- DOCX support is optional and should not block PDF, Markdown, and TXT support.
- Docker Compose is optional unless time allows after P0 is complete.

## Update Log

| Date | Change |
| --- | --- |
| 2026-05-10 | Initialized architecture memory from planning documents and user clarifications. |
| 2026-05-10 | Completed Phase 1 repository structure, added ignore rules and environment example, and documented every current scaffold file role. |
| 2026-05-10 | Completed Phase 2 backend skeleton with FastAPI startup, centralized settings, structured error responses, in-memory simulated task status endpoints, backend requirements, and tests. |
