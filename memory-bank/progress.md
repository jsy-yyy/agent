# Progress Tracker

This file tracks implementation progress at the same small-step granularity as `memory-bank/implementation-plan.md`. Update it whenever a step is completed, blocked, skipped, or revised.

Status legend:

- `todo`: not started.
- `doing`: actively in progress.
- `done`: completed and verified.
- `blocked`: cannot proceed without clarification or dependency.
- `skipped`: intentionally skipped with reason.

## Current Summary

| Field | Value |
| --- | --- |
| Current phase | Phase 18: Testing and quality |
| Current step | 18.15 |
| Overall status | Backend integration-critical logic is fixed and verified: strict 30% compression, automatic remove decisions, merged graph projection, and report/stat consistency. The textbook detail API is aligned with the contest example shape. Parsing now prioritizes `第X章` / `绪论` headings and supplements them with TOC-inferred chapter titles such as `推荐阅读`. Provider config is verified end-to-end against the real ModelScope endpoint with `Qwen/Qwen3-30B-A3B` plus `LLM_ENABLE_THINKING=false` and `Qwen/Qwen3-Embedding-0.6B` at 1024 dimensions, settings now reliably load root `.env` even when the backend is started from `backend/`, and integration now batches embedding queries plus returns structured rate-limit errors instead of crashing. Remaining work: full browser E2E, required docs, benchmark, and deployment polish. |
| Last updated | 2026-05-10 |

## Phase 0: Project Memory And Rules

| Step | Status | Notes |
| --- | --- | --- |
| 0.1 | done | memory-bank contains the required English-named documents. |
| 0.2 | done | AGENTS.md was reviewed and path references were aligned. |
| 0.3 | done | memory-bank/tech-stack.md was reviewed. |
| 0.4 | done | memory-bank/design-document.md was reviewed and renamed from the Chinese planning filename. |
| 0.5 | done | Path conflicts were resolved; implementation now uses memory-bank documents as the design source. |

## Phase 1: Repository Structure

| Step | Status | Notes |
| --- | --- | --- |
| 1.1 | done | Created top-level `backend/`, `frontend/`, `data/`, and `report/`; `memory-bank/` already existed and remains the planning source. |
| 1.2 | done | Created backend module directories under `backend/app/`: `api/`, `core/`, `models/`, `schemas/`, `services/`, `prompts/`, and `storage/`. |
| 1.3 | done | Created frontend module directories under `frontend/src/`: `api/`, `components/`, `features/`, `hooks/`, and `types/`, including feature folders for textbooks, graph, integration, RAG, chat, and report. |
| 1.4 | done | Added `.gitignore` rules for secrets, uploads, PDFs, database files, vector indexes, caches, dependency folders, and generated runtime data; `git check-ignore` verified representative runtime paths. |
| 1.5 | done | Added `.env.example` with OpenAI-compatible provider variables, model names, data directory, and SQLite database URL. |
| 1.6 | done | Updated `memory-bank/architecture.md` with the actual Phase 1 repository structure and file roles. |
| 1.7 | done | Recorded Phase 1 completion and verification notes here for the next developer. |

## Phase 2: Backend Minimal Skeleton

| Step | Status | Notes |
| --- | --- | --- |
| 2.1 | done | Added `backend/app/main.py` with `create_app()`, FastAPI app assembly, router inclusion, and `GET /health`; verified through TestClient. |
| 2.2 | done | Added centralized settings in `backend/app/core/config.py`; environment overrides for `DATA_DIR` and `DATABASE_URL` were verified in tests. |
| 2.3 | done | Added `backend/app/core/errors.py` with structured error envelopes for application and validation errors; verified 404 and 422 shapes. |
| 2.4 | done | Added task status constants, task schemas, task service, and simulated task endpoints for create, read, and fail; verified pending and failed states. |
| 2.5 | done | Added minimal `backend/requirements.txt` for the Phase 2 FastAPI backend without unrelated frameworks. |
| 2.6 | done | Updated `memory-bank/architecture.md` with backend startup, configuration, errors, task status, API routes, and file roles. |
| 2.7 | done | Ran `PYTHONPATH=backend pytest backend/tests`; 5 tests passed and Phase 2 was recorded here for the next developer. |
| 2.8 | done | Settings loader now reads the repository root `.env` independent of working directory, treats `backend/.env` as fallback only, and ignores empty exported env vars when a non-empty file value exists. |

## Phase 3: Database And Persistence

| Step | Status | Notes |
| --- | --- | --- |
| 3.1 | done | Implemented the first SQLite schema in `backend/app/storage/schema.py` for textbooks, chapters, tasks, graph nodes, graph edges, integration decisions, merged nodes, RAG chunks, chat sessions, and chat messages. |
| 3.2 | done | Added `backend/app/storage/database.py` and wired `initialize_database()` into FastAPI app creation; repeated initialization preserves existing rows. |
| 3.3 | done | Added `TextbookService` create/read/list behavior for textbook metadata. |
| 3.4 | done | Added ordered chapter persistence under `TextbookService` with character counts. |
| 3.5 | done | Added `GraphService` persistence for graph nodes, edges, and provenance fields. |
| 3.6 | done | Added `IntegrationService` persistence and status updates for merge, keep, and remove decisions. |
| 3.7 | done | Added `RagService` chunk persistence, `ChatService` session/message persistence, and moved simulated task state from memory to SQLite. |
| 3.8 | done | Updated `memory-bank/architecture.md` with the concrete Phase 3 schema, persistence services, and file roles. |
| 3.9 | done | Ran `PYTHONPATH=backend pytest backend/tests`; Phase 2 and Phase 3 backend tests passed together. |

## Phase 4: Frontend Minimal Skeleton

| Step | Status | Notes |
| --- | --- | --- |
| 4.1 | done | Added React, Vite, TypeScript, package scripts, `index.html`, and frontend entrypoint files; `npm run build` passed. |
| 4.2 | done | Added a responsive three-column workbench with textbook rail, graph workspace, and right-side function panels. |
| 4.3 | done | Added centralized API client in `frontend/src/api/client.ts`; UI components do not build raw request URLs. |
| 4.4 | done | Added shared TypeScript domain types in `frontend/src/types/domain.ts`. |
| 4.5 | done | Added `useDashboardState()` as lightweight feature state for upload, graph, integration, RAG, and chat surfaces. |
| 4.6 | done | Updated `memory-bank/architecture.md` with frontend module boundaries, startup/build commands, and file roles. |
| 4.7 | done | Verified `npm run build`, verified Vite dev server returned HTTP 200 at `http://127.0.0.1:5173/`, then stopped the server. |

## Phase 5: Textbook Upload And File Management

| Step | Status | Notes |
| --- | --- | --- |
| 5.1 | done | Added `POST /api/textbooks/upload` for multi-file uploads and a workflow service that stores uploaded files under `data/uploads/`. |
| 5.2 | done | Validated accepted formats: PDF, Markdown, and TXT; unsupported files return a structured `unsupported_textbook_format` error. |
| 5.3 | done | Persisted textbook metadata: original filename, normalized format, file size, saved path, parse status, total pages, and total characters. |
| 5.4 | done | Added frontend drag-and-drop upload support in `TextbookPanel`. |
| 5.5 | done | Added frontend click-to-select upload and centralized upload API client behavior. |
| 5.6 | done | Added frontend textbook list with selectable rows, status display, and refresh behavior. |
| 5.7 | done | Verified runtime files remain ignored by git; representative `data/`, `node_modules/`, `dist/`, and cache paths are covered by `.gitignore`. |
| 5.8 | done | Updated architecture and progress with upload flow details and verification notes. |

## Phase 6: Textbook Parsing

| Step | Status | Notes |
| --- | --- | --- |
| 6.1 | done | Added TXT parsing with heading-based splitting and single-chapter fallback. |
| 6.2 | done | Added Markdown parsing by `#`, `##`, and `###` headings using the shared heading splitter. |
| 6.3 | done | Added PDF parsing that prefers PyMuPDF and falls back to simple literal-string extraction when PyMuPDF is unavailable. |
| 6.4 | done | Added PDF chapter heading detection using the shared chapter heading pattern. |
| 6.5 | done | Added PDF fallback chapter splitting into one usable chapter when headings are not detected. |
| 6.6 | done | Added basic repeated header/footer filtering across PDF pages. |
| 6.7 | done | Connected parsing to SQLite task status and textbook parse status transitions: parsing, parsed, or failed. |
| 6.8 | done | Added frontend chapter list and content summaries after selecting or parsing a textbook. |
| 6.9 | done | Updated architecture and progress with parsing flow details; `PYTHONPATH=backend pytest backend/tests` and `npm run build` passed. |
| 6.10 | done | Added shared heading rules that prioritize `第X章` / `绪论`, infer supplemental chapter titles from TOC entries such as `推荐阅读`, filter TOC lines from body splitting, and cover TXT/Markdown/PDF with dedicated regression tests. |

## Phase 7: LLM Provider And Prompt Management

| Step | Status | Notes |
| --- | --- | --- |
| 7.1 | done | Added `LLMProvider` protocol, `LLMService` delegation boundary, and `NotConfiguredLLMProvider`; verified business code can depend on the provider abstraction without vendor-specific code. |
| 7.2 | done | Added `OpenAICompatibleProvider` using the `openai` SDK, a `create_llm_provider()` factory wired into `main.py`, and 8 backend tests covering construction, config-driven selection, text/JSON delegation, and error handling. |
| 7.3 | done | Created prompt modules organized by task (extraction, alignment, rag, feedback), a `PromptRegistry` with `get()` and `format()` methods, and 11 backend tests covering registry access, template substitution, error handling, and import isolation. |
| 7.4 | done | Added `parse_and_repair()` in `json_repair.py` with two-pass strategy (direct parse then common-fix repair), handling markdown fences, trailing commas, single-quoted keys/values, and non-object results. Integrated into `OpenAICompatibleProvider.generate_json`. 19 tests cover extraction, repair, and provider integration. |
| 7.5 | done | Added `CallMetadata` dataclass with latency, token counts, and schema name. `OpenAICompatibleProvider` records call history (success and failure) with timing via `time.monotonic()` and token usage from API response. Exposes `call_history` (copy) and `last_call` properties. 10 tests cover metadata model, tracking on success/failure, multi-call accumulation, and missing usage info. |
| 7.6 | done | Architecture.md and progress.md have been updated after every Phase 7 step. Provider boundary, factory wiring, prompt registry, JSON repair, and call metadata are all documented. |

## Phase 8: Single-Textbook Knowledge Graph

| Step | Status | Notes |
| --- | --- | --- |
| 8.1 | done | Created `GraphNodeRequest` and `GraphNodeResponse` schemas in `backend/app/schemas/graph.py` with id, name, definition, category, textbook, chapter, page, and source excerpt fields. |
| 8.2 | done | Created `GraphEdgeResponse` schema with required relation types: prerequisite, parallel, contains, applies_to. Added request/response schemas for build, search, and graph data. |
| 8.3 | done | `KnowledgeExtractor._extract_nodes()` calls LLM per chapter using `extraction.nodes` prompt and persists nodes via `GraphService`. |
| 8.4 | done | `KnowledgeExtractor._extract_relations()` calls LLM using `extraction.relations` prompt, accepts both temp-ID and legacy index-based edge references, normalizes relation types, and persists edges. |
| 8.5 | done | `KnowledgeExtractor.extract()` wraps each chapter in try/except, recording failures in `failed_chapters` without stopping other chapters. |
| 8.6 | done | Graph persistence uses existing `GraphService.create_node()` and `create_edge()` with textbook/chapter provenance. |
| 8.7 | done | Added `POST /api/graph/build` and `GET /api/graph/{textbook_id}` endpoints with proper error handling for missing textbooks and missing chapters. |
| 8.8 | done | Architecture and progress updated with graph extraction flow, knowledge extractor, graph API endpoints, and test coverage. |

## Phase 9: Graph Visualization

| Step | Status | Notes |
| --- | --- | --- |
| 9.1 | done | Cytoscape.js renders nodes and edges from backend data in `GraphWorkspace`. |
| 9.2 | done | Real graph data fetched via `GET /api/graph/{textbook_id}` and rendered, with "Build Graph" button. |
| 9.3 | done | Node click shows detail panel with name, definition, category, page, and source excerpt. |
| 9.4 | done | Cytoscape built-in zoom (wheel) and canvas pan (drag background) enabled. |
| 9.5 | done | Cytoscape built-in node dragging enabled. |
| 9.6 | done | `getTextbookColor()` maps textbook IDs to 8 distinct colors for visual source distinction. |
| 9.7 | done | Node size scales with name frequency (24-50px range) for visual prominence. |
| 9.8 | done | Search bar highlights matching nodes/edges and dims others; Clear button resets. |
| 9.9 | done | Architecture and progress updated with Cytoscape visualization, API client additions, and hook changes. |

## Phase 10: Embedding And Vector Index

| Step | Status | Notes |
| --- | --- | --- |
| 10.1 | done | Created `EmbeddingProvider` protocol with `embed_texts()` and `NotConfiguredEmbeddingProvider` fallback. |
| 10.2 | done | `OpenAIEmbeddingProvider` uses configurable `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `EMBEDDING_MODEL`, and app wiring now supports provider-specific `EMBEDDING_DIMENSION` for non-1536 embeddings. |
| 10.3 | done | Architecture documents local embedding as a future fallback path; `NotConfiguredEmbeddingProvider` fails clearly when no config is set. |
| 10.4 | done | `IndexService.save()` and `load()` persist FAISS index plus chunk ID mapping to `data/indexes/`. |
| 10.5 | done | `IndexService.retrieve()` returns top-k chunk IDs with cosine similarity scores via FAISS inner product search. |
| 10.6 | done | Architecture and progress updated with embedding provider boundary, FAISS index service, and wiring into main.py. |

## Phase 11: Cross-Textbook Graph Integration

| Step | Status | Notes |
| --- | --- | --- |
| 11.1 | done | `normalize_concept_name()` handles spaces, casing, and parentheticals. |
| 11.2 | done | Nodes indexed via `IndexService.build()` with name+definition text. |
| 11.3 | done | `IndexService.retrieve()` finds similar nodes; threshold >0.86 auto-merge, >0.72 LLM review. |
| 11.4 | done | `IntegrationEngine.integrate()` generates merge/keep/remove decisions with `IntegrationService`. |
| 11.5 | done | `_llm_review_equivalence()` calls LLM via `alignment.concepts` prompt for ambiguous pairs. |
| 11.6 | done | `IntegrationService.create_merged_node()` persists merged nodes with source provenance. |
| 11.7 | done | `IntegrationResult` computes total_source_chars, integrated_chars, compression_ratio, target_chars, and target_met. |
| 11.8 | done | Strict 30% compression enforcement implemented: candidates are ranked by shared frequency, graph degree, prerequisite participation, category, and evidence length; over-budget candidates become remove decisions. |
| 11.9 | done | `GET /api/integration/decisions` returns all decisions; `GET /api/integration/stats` returns decision counts, source/integrated chars, compression target, target status, and graph counts. |
| 11.10 | done | Frontend `IntegrationPanel` can run integration, list decisions, and display merge/keep/remove counts plus compression ratio. |
| 11.11 | done | Architecture updated with `IntegrationEngine`, `create_merged_node`, integration API endpoints. |
| 11.12 | done | Added `IntegrationProjectionService` and `GET /api/graph/merged`; merged graph maps active merge decisions to merged nodes, active keep decisions to source nodes, excludes remove decisions, and rewrites surviving edges. |
| 11.13 | done | Integration similarity search now batches query embeddings with `retrieve_many()` to avoid one embedding API request per node, and `/api/integration/run` converts embedding/LLM provider failures into structured task-aware API errors. |

## Phase 12: RAG Chunking

| Step | Status | Notes |
| --- | --- | --- |
| 12.1 | done | `chunk_text()` splits chapter content into overlapping chunks (600 char, 80 overlap). |
| 12.2 | done | Default chunk size 600 characters, configurable via parameter. |
| 12.3 | done | 80 character overlap between adjacent chunks preserves context at boundaries. |
| 12.4 | done | Chunk metadata includes textbook_id, chapter_id, page_start, page_end, chunk_index. |
| 12.5 | done | `RagPipeline.index_chapters()` persists chunks via `rag_service.create_chunk()`. |
| 12.6 | done | Architecture updated with chunking strategy and `RagPipeline`. |

## Phase 13: RAG Index And Retrieval

| Step | Status | Notes |
| --- | --- | --- |
| 13.1 | done | `POST /api/rag/index` triggers chunking and FAISS index build. |
| 13.2 | done | `IndexService.build()` embeds chunks and writes FAISS index. |
| 13.3 | done | `GET /api/rag/status` returns indexed chunk count and load state; frontend displays both. |
| 13.4 | done | `RagPipeline.retrieve()` returns top-k chunks with similarity scores. |
| 13.5 | done | Retrieval results include relevance scores from FAISS inner product. |
| 13.6 | done | BM25 left as optional enhancement; vector retrieval is primary. |
| 13.7 | done | Deduplication handled at retrieval level. |
| 13.8 | done | Architecture updated with RAG retrieval flow. |

## Phase 14: RAG Answering With Citations

| Step | Status | Notes |
| --- | --- | --- |
| 14.1 | done | `RagPipeline.answer()` returns "当前知识库中未找到相关信息" when no context found. |
| 14.2 | done | Only retrieved chunks injected into answer prompt; model instructed not to use outside knowledge. |
| 14.3 | done | Answer generated via `rag.answer` prompt with context chunks. |
| 14.4 | done | Citations include textbook_id, chapter_id, page, relevance_score, and chunk_id. |
| 14.5 | done | All citations mapped to stored chunks via `rag_service.get_chunk()`. |
| 14.6 | done | `POST /api/rag/query` endpoint returns answer + citations; frontend can submit questions. |
| 14.7 | done | Citation response includes first 200 chars of chunk text for preview, and frontend expands citations inline. |
| 14.8 | done | Architecture updated with RAG answering flow. |

## Phase 15: Teacher Feedback

| Step | Status | Notes |
| --- | --- | --- |
| 15.1 | done | `POST /api/chat` creates or reuses a session and stores user/assistant messages via `chat_service`. |
| 15.2 | done | LLM generates explanatory responses for integration decision queries. |
| 15.3 | done | Chat endpoint accepts feedback messages and applies keep/remove/merge/split intent to the selected integration decision. |
| 15.4 | done | Split feedback changes the target decision action to keep and status to `teacher_split`. |
| 15.5 | done | Force-merge feedback changes the target decision action to merge and marks it teacher-modified. |
| 15.6 | done | `GET /api/chat/history` returns session messages when a session ID is provided. |
| 15.7 | done | Frontend `ChatPanel` sends feedback, keeps local conversation state, and refreshes graph/decisions after submission. |
| 15.8 | done | Architecture updated with feedback chat API and decision modification behavior. |

## Phase 16: Integration Report

| Step | Status | Notes |
| --- | --- | --- |
| 16.1 | done | `POST /api/report/generate` creates `data/reports/整合报告.md` with integration overview. |
| 16.2 | done | Report includes textbook count, decision summary, graph statistics, source/integrated characters, compression target, compression ratio, and target status from `IntegrationProjectionService`. |
| 16.3 | done | Decision summary lists merge/keep/remove counts per action. |
| 16.4 | done | Graph statistics section included in report template. |
| 16.5 | done | Report lists each decision with action, reason, and confidence. |
| 16.6 | done | Teaching completeness analysis section confirms prerequisite chains preserved. |
| 16.7 | done | `GET /api/report` returns report content if generated; frontend `ReportPanel` can generate and preview Markdown content. |
| 16.8 | done | Architecture updated with report generation path, shared stats source, and frontend report preview. |

## Phase 17: Core Documentation

| Step | Status | Notes |
| --- | --- | --- |
| 17.1 | done | Wrote README.md with setup, configuration, API reference, project structure, and tech stack. |
| - | done | Added `POST /api/admin/reset` endpoint to clear all data and runtime files. Added Reset button in StatusBar with confirmation dialog. Added `_clean_extracted_text()` to PDF parser for control-char/glyph cleanup. |
| 17.2 | todo | Write memory-bank/requirements-analysis.md. |
| 17.3 | todo | Write memory-bank/system-design.md. |
| 17.4 | todo | Write memory-bank/agent-architecture.md. |
| 17.5 | todo | Optionally write memory-bank/api-documentation.md. |
| 17.6 | todo | Check all docs against implementation. |

## Phase 18: Testing And Quality

| Step | Status | Notes |
| --- | --- | --- |
| 18.1 | todo | Prepare sample TXT, Markdown, and PDF files. |
| 18.2 | todo | Test upload and parsing flow. |
| 18.3 | todo | Test graph construction flow. |
| 18.4 | done | Added backend tests for cross-textbook integration producing merge/remove decisions under a fake similarity index. |
| 18.5 | done | Added backend tests proving integrated_chars/compression_ratio stay within the 30% target and stats match the active decisions. |
| 18.6 | todo | Test RAG question answering. |
| 18.7 | todo | Test teacher feedback updates. |
| 18.8 | done | Added endpoint coverage for `/api/report/generate` and `/api/report`, verifying report data matches integration stats. |
| 18.9 | todo | Check modularity constraints. Current integration/report fixes are split across engine, projection, persistence, report service, and thin route handlers. |
| 18.10 | todo | Check repository cleanliness. |

## Latest Verification

| Date | Result |
| --- | --- |
| 2026-05-10 | `PYTHONPATH=backend pytest backend/tests` passed: 117 tests, 3 FAISS/SWIG deprecation warnings. |
| 2026-05-10 | `npm run build` passed in `frontend/`; Vite warns that one bundle chunk is larger than 500 kB. |

## Phase 19: RAG Benchmark

| Step | Status | Notes |
| --- | --- | --- |
| 19.1 | todo | Prepare 20 test questions. |
| 19.2 | todo | Label expected answer points. |
| 19.3 | todo | Label expected citations. |
| 19.4 | todo | Run RAG evaluation. |
| 19.5 | todo | Compute metrics. |
| 19.6 | todo | Optionally compare chunk sizes. |
| 19.7 | todo | Write benchmark results into memory-bank docs. |
| 19.8 | todo | Update architecture with benchmark role. |

## Phase 20: Deployment And Final Acceptance

| Step | Status | Notes |
| --- | --- | --- |
| 20.1 | todo | Prepare local start instructions. |
| 20.2 | todo | Optionally prepare Docker Compose. |
| 20.3 | todo | Verify missing environment variable errors. |
| 20.4 | todo | Run full P0 demo flow. |
| 20.5 | todo | Run browser smoke test. |
| 20.6 | todo | Check README against actual start flow. |
| 20.7 | todo | Check memory-bank/agent-architecture.md depth. |
| 20.8 | todo | Check report completeness. |
| 20.9 | todo | Final architecture consistency check. |
| 20.10 | todo | Final git cleanliness check. |
