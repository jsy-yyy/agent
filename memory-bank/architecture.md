# Architecture Memory

This file is the source of truth for the implemented architecture. It must be read before any code is written and updated after every major feature, milestone, schema change, API change, module-boundary change, or data-flow change.

## Current Status

- Implementation status: Frontend P0 loop is wired through upload, parse, graph build/view, integration run/decision list, RAG indexing/query, teacher feedback, and report preview. Backend integration now enforces the 30% compression budget, creates automatic `remove` decisions when needed, exposes an integrated graph projection, and generates reports from the same statistics source as `/api/integration/stats`.
- Provider status: The repository now supports provider-specific LLM request flags through configuration. ModelScope is verified with `LLM_MODEL=Qwen/Qwen3-30B-A3B`, `LLM_ENABLE_THINKING=false`, `EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B`, and `EMBEDDING_DIMENSION=1024`; live connectivity checks returned `OK` for the LLM and a 1024-dimensional embedding vector.
- Config status: settings now load from explicit env-file search instead of depending on the process working directory. The repository root `.env` is the primary source, `backend/.env` is only a fallback, and empty exported environment variables no longer override non-empty file values.
- Integration status: the cross-textbook integration path now uses batched query embeddings during similarity search instead of issuing one embedding API request per node. Provider failures from embedding or LLM calls are converted into structured API errors and failed task states instead of uncaught ASGI exceptions.
- Codebase status: FastAPI backend includes upload/parsing, graph extraction, strict integration compression, merged-graph projection, RAG, chat, report, admin reset, OpenAI-compatible LLM/embedding providers, SQLite persistence, and FAISS index services. React/Vite frontend includes the three-column workbench with live textbook, graph, integration, RAG, feedback, and report panels.
- Database status: SQLite schema iteration 1 is implemented for textbooks, chapters, graph nodes, graph edges, integration decisions, merged nodes, RAG chunks, chat sessions, chat messages, and tasks.
- API note: `GET /api/textbooks/{textbook_id}` now returns a contest-aligned flattened textbook structure with top-level `textbook_id`, `filename`, `title`, `total_pages`, `total_chars`, and `chapters`, rather than nesting textbook metadata under a `textbook` field.
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
│   │   │   ├── admin.py
│   │   │   ├── chat.py
│   │   │   ├── graph.py
│   │   │   ├── health.py
│   │   │   ├── integration.py
│   │   │   ├── rag.py
│   │   │   ├── report.py
│   │   │   ├── router.py
│   │   │   ├── tasks.py
│   │   │   ├── textbooks.py
│   │   │   └── .gitkeep
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   ├── task_status.py
│   │   │   └── .gitkeep
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── records.py
│   │   │   └── .gitkeep
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   ├── health.py
│   │   │   ├── tasks.py
│   │   │   ├── textbooks.py
│   │   │   └── .gitkeep
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py
│   │   │   ├── embedding/
│   │   │   ├── graph_service.py
│   │   │   ├── integration_engine.py
│   │   │   ├── integration_projection.py
│   │   │   ├── integration_service.py
│   │   │   ├── knowledge_extractor.py
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── provider.py
│   │   │   │   └── service.py
│   │   │   ├── parsing/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── markdown_parser.py
│   │   │   │   ├── models.py
│   │   │   │   ├── parser_service.py
│   │   │   │   ├── pdf_parser.py
│   │   │   │   └── text_parser.py
│   │   │   ├── rag_pipeline.py
│   │   │   ├── rag_service.py
│   │   │   ├── report_service.py
│   │   │   ├── task_service.py
│   │   │   ├── textbook_service.py
│   │   │   ├── textbook_workflow.py
│   │   │   ├── time.py
│   │   │   └── .gitkeep
│   │   ├── prompts/
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── files.py
│   │   │   ├── schema.py
│   │   │   └── .gitkeep
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── .gitkeep
│   ├── tests/
│   │   ├── test_phase2_backend_skeleton.py
│   │   ├── test_phase3_persistence.py
│   │   ├── test_phase5_6_upload_parsing.py
│   │   └── test_phase7_1_llm_provider_boundary.py
│   ├── requirements.txt
│   └── .gitkeep
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── .gitkeep
│   │   ├── components/
│   │   │   ├── Panel.tsx
│   │   │   ├── StatusBar.tsx
│   │   │   └── .gitkeep
│   │   ├── features/
│   │   │   ├── textbooks/
│   │   │   │   ├── TextbookPanel.tsx
│   │   │   │   └── .gitkeep
│   │   │   ├── graph/
│   │   │   │   ├── GraphWorkspace.tsx
│   │   │   │   └── .gitkeep
│   │   │   ├── integration/
│   │   │   │   ├── IntegrationPanel.tsx
│   │   │   │   └── .gitkeep
│   │   │   ├── rag/
│   │   │   │   ├── RagPanel.tsx
│   │   │   │   └── .gitkeep
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   └── .gitkeep
│   │   │   └── report/
│   │   │       ├── ReportPanel.tsx
│   │   │       └── .gitkeep
│   │   ├── hooks/
│   │   │   ├── useDashboardState.ts
│   │   │   └── .gitkeep
│   │   ├── types/
│   │   │   ├── domain.ts
│   │   │   └── .gitkeep
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   ├── vite-env.d.ts
│   │   └── .gitkeep
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
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

Future implementation steps are expected to add concrete LLM provider configuration, prompt management, knowledge extraction, real backend endpoints for graphs/integration/RAG/chat/report, Cytoscape rendering, and README/docs.

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
| `backend/requirements.txt` | Backend dependency list: FastAPI, Uvicorn, multipart support, Pydantic, pydantic-settings, and PyMuPDF for full PDF extraction. |
| `backend/app/__init__.py` | Marks `app` as the backend Python package. |
| `backend/app/main.py` | FastAPI entrypoint. Defines `create_app()`, registers error handlers, includes the API router, and exposes the module-level `app` used by Uvicorn. |
| `backend/app/api/__init__.py` | Marks the backend route package. |
| `backend/app/api/router.py` | Aggregates backend routers so `main.py` has one route inclusion point. |
| `backend/app/api/health.py` | Thin health route module. `GET /health` returns basic service status and app name from centralized settings. |
| `backend/app/api/tasks.py` | Thin simulated task route module. Exposes create, read, and fail endpoints under `/api/tasks/*` and delegates logic to `TaskService`. |
| `backend/app/api/textbooks.py` | Thin textbook route module. Exposes upload, list, detail, and parse endpoints under `/api/textbooks/*` and delegates workflow behavior to services. |
| `backend/app/core/__init__.py` | Marks the backend core package. |
| `backend/app/core/config.py` | Centralized settings loader. Uses `pydantic-settings` when installed and a small environment fallback otherwise; exposes cached `get_settings()` and `clear_settings_cache()` for tests. |
| `backend/app/core/errors.py` | Shared application error type and FastAPI exception handlers. All handled errors return `{"error": {"code": "...", "message": "...", "details": ...}}`. |
| `backend/app/core/task_status.py` | Canonical task status enum with `pending`, `running`, `completed`, and `failed`. |
| `backend/app/schemas/__init__.py` | Marks the typed schema package. |
| `backend/app/schemas/health.py` | Pydantic response schema for the health endpoint. |
| `backend/app/schemas/tasks.py` | Pydantic request and response schemas for simulated task operations. |
| `backend/app/services/__init__.py` | Marks the backend service package. |
| `backend/app/services/task_service.py` | SQLite-backed task service. It creates simulated pending tasks, retrieves tasks, marks tasks failed, and raises structured `AppError` for missing task IDs. |
| `backend/tests/test_phase2_backend_skeleton.py` | Phase 2 verification tests covering health, environment override behavior, structured error envelopes, and simulated task create/read/fail behavior. |

## Phase 3 Backend File Roles

| File | Role |
| --- | --- |
| `backend/app/models/__init__.py` | Marks the backend persistence-facing model package. |
| `backend/app/models/records.py` | Pydantic record models for rows returned by persistence services: textbooks, chapters, graph nodes, graph edges, integration decisions, RAG chunks, chat sessions, chat messages, and tasks. |
| `backend/app/storage/__init__.py` | Marks the backend storage package. |
| `backend/app/storage/database.py` | SQLite URL parsing, connection management, foreign key activation, schema initialization, and test reset helpers. |
| `backend/app/storage/schema.py` | Source of truth for SQLite schema iteration 1. It uses `CREATE TABLE IF NOT EXISTS` so repeated startup does not erase existing data. |
| `backend/app/services/time.py` | Shared UTC timestamp helpers used by persistence services. |
| `backend/app/services/textbook_service.py` | SQLite-backed textbook metadata service and ordered chapter persistence service. |
| `backend/app/services/graph_service.py` | SQLite-backed graph node and graph edge persistence with source provenance fields. |
| `backend/app/services/integration_service.py` | SQLite-backed integration decision persistence. Affected node IDs are stored as JSON text and restored as lists. |
| `backend/app/services/rag_service.py` | SQLite-backed RAG chunk persistence with textbook, chapter, page, and token-count metadata. |
| `backend/app/services/chat_service.py` | SQLite-backed chat session and chat message persistence for future teacher feedback flows. |
| `backend/tests/test_phase3_persistence.py` | Phase 3 verification tests covering schema creation, repeated initialization, textbook/chapter storage, graph storage, integration decisions, RAG chunks, chat history, and task persistence across app recreation. |

## Phase 5 And 6 Backend File Roles

| File | Role |
| --- | --- |
| `backend/app/schemas/textbooks.py` | Pydantic API schemas for textbook metadata, chapter responses, detailed textbook responses, and upload responses. |
| `backend/app/storage/files.py` | Upload storage helper. Validates textbook filename extensions, maps them to internal formats, creates `data/uploads/`, and writes uploaded files to unique paths. |
| `backend/app/services/textbook_workflow.py` | Upload and parsing orchestration service. It validates uploads, persists textbook metadata, starts parse tasks, calls parsers, replaces chapter records, and updates textbook/task status. |
| `backend/app/services/parsing/__init__.py` | Marks the parser package. |
| `backend/app/services/parsing/models.py` | Parser result models: `ParsedTextbook` and `ParsedChapter`. |
| `backend/app/services/parsing/chapter_headings.py` | Shared chapter-heading rules for TXT, Markdown, and PDF. It prioritizes `第X章` and `绪论`, infers supplemental chapter titles from TOC lines, and filters TOC entries so they do not become body chapters. |
| `backend/app/services/parsing/text_parser.py` | TXT parser with shared chapter heading detection, TOC-aware supplemental titles, chapter-title deduplication, and one-chapter fallback. |
| `backend/app/services/parsing/markdown_parser.py` | Markdown parser that reuses the shared heading splitter for `#`, `##`, and `###` headings. |
| `backend/app/services/parsing/pdf_parser.py` | PDF parser. It prefers PyMuPDF for page-by-page text extraction, filters repeated page headers/footers, detects chapter headings, supplements them with TOC-inferred titles such as `推荐阅读`, and falls back to simple literal-string extraction when PyMuPDF is unavailable. |
| `backend/app/services/parsing/parser_service.py` | Format dispatcher that selects TXT, Markdown, or PDF parsing based on stored textbook format. |
| `backend/tests/test_phase5_6_upload_parsing.py` | Phase 5/6 verification tests covering multi-file upload, unsupported format errors, TXT parsing, Markdown parsing, simple PDF parsing, chapter persistence, and completed parse tasks. |

## Phase 7 Backend File Roles

| File | Role |
| --- | --- |
| `backend/app/services/llm/__init__.py` | Exports the LLM service boundary, provider protocol, provider error type, factory, and OpenAI-compatible provider for business services. |
| `backend/app/services/llm/provider.py` | Defines `LLMProvider` protocol, `CallMetadata` dataclass (latency, token counts), `LLMProviderError`, and `NotConfiguredLLMProvider`. |
| `backend/app/services/llm/service.py` | Business-facing LLM service wrapper. It delegates text and JSON generation to an injected `LLMProvider` so downstream graph, RAG, integration, and chat services do not import vendor-specific SDKs directly. |
| `backend/app/services/llm/openai_provider.py` | Concrete `OpenAICompatibleProvider` implementation using the `openai` SDK. Accepts configurable `api_key`, `base_url`, and `model`. Uses `parse_and_repair()` for JSON responses. Raises `LLMProviderError` on missing configuration, API errors, or unrepairable JSON. |
| `backend/app/services/llm/json_repair.py` | JSON repair utility for LLM outputs. `extract_json_candidate()` strips markdown fences and surrounding text. `parse_and_repair()` does a two-pass parse: direct then common-fix (trailing commas, single-quoted keys/values), raising descriptive `ValueError` on failure. |
| `backend/app/services/llm/factory.py` | Provider factory `create_llm_provider()` that reads settings and returns `OpenAICompatibleProvider` when configured or `NotConfiguredLLMProvider` when settings are missing. |
| `backend/tests/test_phase7_1_llm_provider_boundary.py` | Phase 7.1 verification tests proving the service delegates text and JSON generation through the provider abstraction and fails clearly when no provider is configured. |
| `backend/tests/test_phase7_2_openai_provider.py` | Phase 7.2 verification tests covering provider construction validation, config-driven factory selection, text/JSON delegation to the OpenAI client, and error wrapping. |
| `backend/app/prompts/__init__.py` | Exports a module-level `prompts` registry instance for the whole backend. |
| `backend/app/prompts/registry.py` | `PromptRegistry` class that maps prompt names to templates, supports `get()`, `format(**kwargs)`, and `list_prompts()`. |
| `backend/app/prompts/extraction.py` | Knowledge extraction prompt templates for generating graph nodes and relations from chapter content. |
| `backend/app/prompts/alignment.py` | Cross-textbook alignment prompt templates for concept equivalence checking and integration decision review. |
| `backend/app/prompts/rag.py` | RAG prompt templates for grounded answering with citations and benchmark question generation. |
| `backend/app/prompts/feedback.py` | Teacher feedback prompt templates for decision explanation, intent parsing, and conversational response. |
| `backend/tests/test_phase7_3_prompt_management.py` | Phase 7.3 verification tests covering registry completeness, template substitution, error handling, and prompt import isolation. |
| `backend/tests/test_phase7_4_json_repair.py` | Phase 7.4 verification tests covering JSON extraction from markdown/text, two-pass repair (trailing commas, single quotes, nested objects), error cases (arrays, strings, broken JSON), and provider integration. |
| `backend/tests/test_phase7_5_call_metadata.py` | Phase 7.5 verification tests covering `CallMetadata` model, latency/token tracking on text and JSON calls, error-path recording, multi-call accumulation, copy isolation, and missing usage info. |

## Phase 4 Frontend File Roles

| File | Role |
| --- | --- |
| `frontend/package.json` | Frontend package manifest with React, Vite, TypeScript, Cytoscape, and scripts for dev, build, preview, and typecheck. |
| `frontend/package-lock.json` | Locked npm dependency graph generated by `npm install` for reproducible frontend installs. |
| `frontend/tsconfig.json` | TypeScript configuration for strict React source compilation. |
| `frontend/tsconfig.node.json` | TypeScript configuration for Vite config compilation. |
| `frontend/vite.config.ts` | Vite configuration with React plugin, local dev server host/port, and `/api` plus `/health` proxies to the FastAPI backend. |
| `frontend/index.html` | Vite HTML entrypoint mounting the React app at `#root`. |
| `frontend/src/vite-env.d.ts` | Vite client type references. |
| `frontend/src/main.tsx` | React runtime entrypoint that mounts `App`. |
| `frontend/src/App.tsx` | Top-level frontend shell composing the status bar, textbook rail, graph workspace, and right-side function panels. |
| `frontend/src/styles.css` | Global responsive workbench styling for the Phase 4 skeleton. |
| `frontend/src/api/client.ts` | Centralized typed API client for health, simulated task calls, textbook upload, textbook list/detail retrieval, and parse triggers. Components should use this boundary instead of raw request code. |
| `frontend/src/types/domain.ts` | Shared TypeScript domain types for tasks, textbooks, chapters including content summaries, graph data, integration decisions, RAG chunks, and citations. |
| `frontend/src/hooks/useDashboardState.ts` | Lightweight frontend state hook that loads textbook metadata, tracks selected textbook and task status, uploads files, triggers parsing, refreshes chapter data, and derives dashboard summary values. |
| `frontend/src/components/StatusBar.tsx` | Reusable top status bar showing high-level counts and task status. |
| `frontend/src/components/Panel.tsx` | Reusable section wrapper used by feature panels. |
| `frontend/src/features/textbooks/TextbookPanel.tsx` | Textbook feature panel with drag-and-drop upload, click-to-select upload, selectable textbook list, parse button, error display, and chapter summaries. |
| `frontend/src/features/graph/GraphWorkspace.tsx` | Graph workspace shell with view controls, search input, and a static visual placeholder. Real Cytoscape rendering belongs to later graph phases. |
| `frontend/src/features/integration/IntegrationPanel.tsx` | Integration summary shell for merge, keep, and remove counts. |
| `frontend/src/features/rag/RagPanel.tsx` | RAG panel shell with question input and indexed chunk count. |
| `frontend/src/features/chat/ChatPanel.tsx` | Teacher feedback chat panel shell. |
| `frontend/src/features/report/ReportPanel.tsx` | Report preview panel shell pointing at the eventual generated report path. |

## Backend Startup And Verification

The backend app object is `app.main:app` when `PYTHONPATH=backend` is set. A local developer can start the Phase 2 backend with:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

Phase 2 verification command:

```bash
PYTHONPATH=backend pytest backend/tests
```

Current backend verified result: 18 tests passed.

The frontend shell is built from `frontend/` with:

```bash
npm install
npm run build
```

The Vite dev server is configured to proxy `/api` and `/health` to `http://127.0.0.1:8000`.

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
| `POST` | `/api/textbooks/upload` | Uploads one or more PDF, Markdown, or TXT files, saves them under `data/uploads/`, and creates textbook metadata records. |
| `GET` | `/api/textbooks` | Lists uploaded textbooks with metadata and parse status. |
| `GET` | `/api/textbooks/{textbook_id}` | Returns one textbook plus its parsed chapters. |
| `POST` | `/api/textbooks/{textbook_id}/parse` | Parses the stored textbook synchronously, updates chapters and textbook status, and returns the parse task status. |
| `POST` | `/api/graph/build` | Triggers knowledge extraction for a parsed textbook, creating graph nodes and edges via LLM. |
| `GET` | `/api/graph/{textbook_id}` | Returns graph nodes and edges for a textbook. |
| `GET` | `/api/graph/merged` | Returns the integrated graph projection built from active merge/keep/remove decisions. |
| `POST` | `/api/integration/run` | Runs cross-textbook integration with embedding similarity, LLM review for ambiguous matches, automatic keep/remove decisions, and strict 30% compression enforcement. |
| `GET` | `/api/integration/decisions` | Lists all integration decisions (merge, keep, remove). |
| `GET` | `/api/integration/stats` | Returns integration statistics: decision counts, source/integrated characters, target budget, compression status, and source/integrated graph counts. |
| `POST` | `/api/rag/index` | Chunks textbook chapters and builds FAISS vector index. |
| `GET` | `/api/rag/status` | Returns index status (chunk count, loaded state). |
| `POST` | `/api/rag/query` | Queries the RAG index and returns grounded answer with citations. |
| `POST` | `/api/chat` | Sends a teacher feedback message, returns LLM response. |
| `GET` | `/api/chat/history` | Returns chat session and message history. |
| `POST` | `/api/report/generate` | Generates `data/reports/整合报告.md` with integration overview, graph statistics, compression data, and decision details. |
| `GET` | `/api/report` | Returns generated report content or not-generated status. |
| `POST` | `/api/admin/reset` | Clears all database tables and runtime files (uploads, parsed, graphs, indexes, reports). |

## Implemented Backend Conventions

- Configuration is centralized in `backend/app/core/config.py`.
- Environment variables currently supported by settings are `DATA_DIR`, `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`, `LLM_ENABLE_THINKING`, `EMBEDDING_MODEL`, and `EMBEDDING_DIMENSION`.
- Settings resolve values in this order: non-empty process environment variable, repository root `.env`, fallback `backend/.env`, then code default.
- Application errors and validation errors use one envelope shape: `{"error": {"code": string, "message": string, "details": optional}}`.
- Provider-backed integration failures use structured API errors too: embedding failures surface as `embedding_unavailable`, LLM failures surface as `llm_unavailable`, and the integration task is persisted as `failed`.
- Task state is persisted in SQLite.
- FastAPI enables CORS for the local Vite origins `http://127.0.0.1:5173` and `http://localhost:5173`.
- Upload validation accepts `.pdf`, `.md`, `.markdown`, and `.txt`. Unsupported extensions return `unsupported_textbook_format`.
- Parsing status uses textbook states `uploaded`, `parsing`, `parsed`, and `failed`; parse tasks use `running`, `completed`, or `failed`.
- Business services that need model output should depend on `backend/app/services/llm/LLMProvider` through `LLMService`; direct vendor SDK imports belong only inside concrete provider implementations.

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

1. User uploads one or more textbooks through the frontend upload panel.
2. Frontend sends files through `frontend/src/api/client.ts` to `POST /api/textbooks/upload`.
3. Backend stores uploaded files under `data/uploads/` and creates textbook records with `uploaded` status.
4. User selects a textbook and triggers parsing from the frontend.
5. Backend creates a parse task, sets textbook status to `parsing`, parses TXT/Markdown/PDF, replaces chapter records, sets textbook status to `parsed`, and completes the task.
6. Frontend refreshes textbook metadata and displays chapter titles, character counts, and content summaries.
7. Knowledge extraction builds textbook graph nodes and edges.
8. Integration clears stale integration outputs, groups equivalent cross-textbook concepts, ranks candidate kept content, enforces the 30% character budget, persists merge/keep/remove decisions, and creates merged-node records.
9. `IntegrationProjectionService` derives the integrated graph and statistics from active decisions so `/api/graph/merged`, `/api/integration/stats`, and report generation share one data source.
10. RAG, teacher feedback, and report endpoints read from the persisted graph, chunk, chat, and integration tables.

## Database Strategy

SQLite is initialized from `backend/app/storage/schema.py` during FastAPI app creation. The current schema is iteration 1 and can evolve in later phases, but code must not invent fields without updating this file.

Implemented entities:

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

## SQLite Schema Iteration 1

| Table | Columns |
| --- | --- |
| `textbooks` | `textbook_id` PK, `filename`, `title`, `file_format`, `file_size`, `saved_path`, `parse_status`, `total_pages`, `total_chars`, `created_at`, `updated_at`. |
| `chapters` | `chapter_id` PK, `textbook_id` FK, `title`, `order_index`, `page_start`, `page_end`, `content`, `char_count`, `created_at`. |
| `graph_nodes` | `node_id` PK, `textbook_id` FK, `chapter_id` nullable FK, `name`, `definition`, `category`, `page`, `source_excerpt`, `created_at`. |
| `graph_edges` | `edge_id` PK, `textbook_id` FK, `source_node_id` FK, `target_node_id` FK, `relation_type`, `description`, `created_at`. |
| `integration_decisions` | `decision_id` PK, `action`, `affected_node_ids` JSON text, `result_node_id`, `reason`, `confidence`, `status`, `created_at`, `updated_at`. |
| `merged_nodes` | `merged_node_id` PK, `name`, `definition`, `source_node_ids` JSON text, `created_at`, `updated_at`. |
| `rag_chunks` | `chunk_id` PK, `textbook_id` FK, `chapter_id` nullable FK, `chunk_index`, `text`, `page_start`, `page_end`, `token_count`, `created_at`. |
| `chat_sessions` | `session_id` PK, `title`, `created_at`, `updated_at`. |
| `chat_messages` | `message_id` PK, `session_id` FK, `role`, `content`, `created_at`. |
| `tasks` | `task_id` PK, `task_type`, `status`, `progress`, `error_message`, `created_at`, `updated_at`. |

Foreign keys are enabled per SQLite connection with `PRAGMA foreign_keys = ON`. Runtime database files are ignored by git under the existing `.gitignore` policy.

## File Storage Strategy

Runtime files live under `data/` and must not be committed.

Implemented storage directories:

```text
data/
  uploads/
  parsed/
  graphs/
  indexes/
  reports/
```

The `.gitignore` policy ignores generated files under these directories while keeping only `.gitkeep` placeholders tracked.

Uploaded textbooks are written to `data/uploads/` with unique generated filenames. The original filename remains in SQLite metadata.

## Implemented Parsing Strategy

- TXT and Markdown parsing use a shared heading splitter plus a shared heading-rules module. The parser first prioritizes chapter-level titles such as `第X章 ...`, `Chapter N`, and `绪论`.
- When a TOC marker such as `目录` or `Contents` is present, the parser scans nearby TOC entries, identifies chapter-level items, and then treats sibling TOC entries that later reappear as standalone body titles as valid chapters too. This supports textbook sections such as `推荐阅读` without treating the TOC page itself as chapter content.
- TXT files without recognized headings produce one fallback chapter.
- Markdown files split by headings and preserve heading titles without leading `#` markers.
- PDF parsing prefers PyMuPDF (`fitz`) for page-by-page text extraction.
- When PyMuPDF is unavailable, PDF parsing uses a conservative fallback that extracts simple literal text strings from the PDF bytes. This is enough for lightweight local smoke tests, while production-quality PDF extraction should use PyMuPDF from `backend/requirements.txt`.
- PDF heading detection combines regex, font-size/bold cues, and TOC-inferred supplemental titles so standalone sections like `推荐阅读` can still become chapters.
- Repeated PDF page header/footer lines are removed when enough pages are present to identify repeated edge lines.
- `_clean_extracted_text()` removes control characters (including `\x08` backspace) and unmapped glyphs (`�`) from PyMuPDF output, then collapses whitespace.
- PDF files without recognized chapter headings produce one fallback chapter covering the available pages.
- Knowledge extraction remains chapter-based, and the extractor now accepts both temp-ID relation outputs (`source` / `target`) and older index-based relation outputs (`source_node_index` / `target_node_index`) for compatibility.

## Implemented LLM Provider Boundary

- `LLMProvider` is the backend protocol for model calls. It currently exposes `generate_text(prompt)` and `generate_json(prompt, schema_name)`.
- `LLMService` is the business-facing wrapper used by future graph extraction, integration review, RAG answering, and teacher feedback services.
- `NotConfiguredLLMProvider` raises `LLMProviderError` with a clear message when no concrete provider has been wired yet.
- `OpenAICompatibleProvider` is the concrete implementation using the `openai` SDK. It accepts configurable `api_key`, `base_url`, and `model` at construction time.
- `create_llm_provider()` is the factory wired into `main.py`. It reads `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`, and optional `LLM_ENABLE_THINKING` from settings and returns the appropriate provider. The resulting `LLMService` is stored on `app.state.llm_service` for route access.
- `IndexService` is created with a configured embedding dimension from settings instead of assuming OpenAI's default 1536 dimensions. This allows the same FAISS pipeline to work with ModelScope/OpenAI-compatible embedding models that return other sizes, including the verified 1024-dimensional `Qwen/Qwen3-Embedding-0.6B`.
- `IndexService.retrieve_many()` batches multiple query embeddings into one provider call and performs FAISS search per row on the resulting embedding matrix. `retrieve()` delegates to the batched path for consistency.
- `CallMetadata` captures call type, schema name, latency in ms, and optional prompt/completion/total token counts. `OpenAICompatibleProvider` records metadata on every call (success or failure) and exposes `call_history` and `last_call` properties.

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

## Implemented Frontend P0 Loop

- `frontend/src/api/client.ts` now exposes typed calls for integration, RAG, chat, and report APIs in addition to textbook and graph APIs.
- `frontend/src/hooks/useDashboardState.ts` owns live state for integration decisions/stats, RAG status/answers, chat messages/session, and report content.
- `IntegrationPanel` can run cross-textbook integration, display merge/keep/remove counts, show compression ratio, and list decision cards with IDs, status, reasons, affected node counts, and confidence.
- `RagPanel` can build an index for the selected textbook, submit a question, render the grounded answer, and expand citations with chunk preview text.
- `ChatPanel` sends teacher feedback with an optional selected decision ID and shows local conversation history. Feedback refreshes integration decisions and graph data after submission.
- `ReportPanel` can trigger report generation and preview the returned Markdown content in the browser.
- `StatusBar` summary now reflects indexed chunk count and integration compression ratio when available.

## Implemented Teacher Feedback Decision Updates

- `backend/app/api/chat.py` accepts optional `session_id` and `decision_id` fields.
- Chat messages are persisted with `ChatService.add_message()`.
- Feedback text can modify an integration decision without relying on LLM availability:
  - keep/保留 feedback changes the target decision action to `keep`.
  - split/拆分/不是同一个 feedback changes the target decision action to `keep` and status to `teacher_split`.
  - merge/合并 feedback changes the target decision action to `merge`.
  - remove/删除 feedback changes the target decision action to `remove`.
- If no explicit decision ID is supplied and exactly one active decision exists, chat feedback applies to that decision.
- `GET /api/chat/history` can return persisted history for a provided session ID.

## Implemented Integration Compression And Projection

- `IntegrationEngine.integrate()` clears prior integration outputs at the start of a fresh run so stale decisions and merged nodes do not pollute current statistics.
- Source size uses parsed textbook `total_chars`, falling back to chapter character counts and then graph-node text if needed.
- Equivalent concepts are grouped by high embedding similarity, exact normalized-name matches, or LLM review for medium-similarity pairs.
- Candidate integrated content is ranked by cross-textbook frequency, graph degree, prerequisite participation, core-concept category, and source evidence length.
- The engine greedily selects ranked merge/keep candidates while keeping integrated definition characters at or below `30%` of source characters. Candidates that do not fit become active `remove` decisions with an explicit compression reason.
- `IntegrationService.clear_outputs()` removes stale decisions and merged nodes; `IntegrationService.list_merged_nodes()` supports projection, stats, and reporting.
- `IntegrationProjectionService` is the single source for active integration stats and the merged graph projection. It maps merge decisions to `merged_nodes`, keep decisions to original graph nodes, excludes remove decisions, rewrites surviving edges through the merge map, and deduplicates projected edges.
- `GET /api/graph/merged`, `GET /api/integration/stats`, and `ReportService.generate()` all use the projection service, keeping report data consistent with API statistics.

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
| 2026-05-10 | Completed Phase 3 SQLite persistence with schema initialization, record models, persistence services, durable task status, and backend tests. |
| 2026-05-10 | Completed Phase 4 React/Vite/TypeScript frontend skeleton with three-column layout, shared types, API client, lightweight dashboard state, and build/dev-server verification. |
| 2026-05-10 | Completed Phase 5 textbook upload with backend multi-file upload, format validation, file metadata persistence, frontend drag-and-drop/click upload, and textbook list status display. |
| 2026-05-10 | Completed Phase 6 textbook parsing with TXT, Markdown, and PDF parsers, parse task status, chapter persistence, frontend chapter summaries, and tests. |
| 2026-05-10 | Completed Phase 7.1 LLM provider abstraction with a vendor-neutral protocol, injected service boundary, not-configured provider, and backend tests. |
| 2026-05-10 | Completed Phase 7.2 OpenAI-compatible provider with configurable API key, base URL, model, factory wiring into main.py, and 8 backend tests. |
| 2026-05-10 | Completed Phase 7.3 prompt management directory with registry, extraction/alignment/rag/feedback prompt modules, and 11 backend tests. |
| 2026-05-10 | Completed Phase 7.4 JSON validation and repair flow with two-pass parsing, integrated into `OpenAICompatibleProvider`, with 19 backend tests. |
| 2026-05-10 | Completed Phase 7.5 LLM call latency and token tracking with `CallMetadata` dataclass, provider call history, and 10 backend tests. |
| 2026-05-10 | Completed Phase 8 knowledge graph extraction: schemas, `KnowledgeExtractor` service with per-chapter LLM extraction and failure isolation, graph API endpoints, 10 extraction tests, 10 schema tests. |
| 2026-05-10 | Completed Phase 9 graph visualization: Cytoscape.js rendering, node details panel, search/highlight, source-based colors, frequency-based sizing, "Build Graph" button, updated API client and hook. |
| 2026-05-10 | Completed Phase 10 embedding provider and FAISS index: `EmbeddingProvider` protocol, OpenAI implementation, `IndexService` with build/retrieve/save/load, wired into main.py, 13 backend tests. |
| 2026-05-10 | Added `POST /api/admin/reset` endpoint, frontend Reset button in StatusBar, `_clean_extracted_text()` PDF cleanup, and updated architecture.md API surface table. |
| 2026-05-10 | Wired frontend P0 panels for integration, RAG, teacher feedback, and report preview; added chat-driven integration decision updates; improved integration stats and compression display. |
| 2026-05-10 | Fixed backend integration-critical logic: strict 30% compression selection, automatic remove decisions, `/api/graph/merged` projection, and report generation from shared stats; backend tests now cover these paths. |
