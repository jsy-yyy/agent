# Architecture Memory

This file is the source of truth for the implemented architecture. It must be read before any code is written and updated after every major feature, milestone, schema change, API change, module-boundary change, or data-flow change.

## Current Status

- Implementation status: planning and documentation stage.
- Codebase status: no application code has been implemented yet.
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

## Planned Top-Level Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── prompts/
│   │   ├── storage/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
├── data/
├── memory-bank/
├── report/
├── .env.example
├── .gitignore
└── README.md
```

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

Planned directories:

```text
data/
  uploads/
  parsed/
  graphs/
  indexes/
  reports/
```

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
