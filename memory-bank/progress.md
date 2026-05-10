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
| Current phase | Phase 1: repository structure |
| Current step | 1.1 |
| Overall status | Memory-bank alignment complete; ready for implementation structure |
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
| 1.1 | todo | Create backend, frontend, data, report, and memory-bank structure. |
| 1.2 | todo | Create backend module directories. |
| 1.3 | todo | Create frontend module directories. |
| 1.4 | todo | Establish ignored runtime data strategy. |
| 1.5 | todo | Create environment variable example. |
| 1.6 | todo | Update architecture with initial project boundaries. |

## Phase 2: Backend Minimal Skeleton

| Step | Status | Notes |
| --- | --- | --- |
| 2.1 | todo | Initialize FastAPI backend entrypoint. |
| 2.2 | todo | Add configuration module. |
| 2.3 | todo | Add unified error response convention. |
| 2.4 | todo | Add task status model. |
| 2.5 | todo | Add backend dependency list. |
| 2.6 | todo | Update architecture with backend skeleton. |

## Phase 3: Database And Persistence

| Step | Status | Notes |
| --- | --- | --- |
| 3.1 | todo | Design SQLite tables incrementally. |
| 3.2 | todo | Add database initialization flow. |
| 3.3 | todo | Add textbook metadata read/write service. |
| 3.4 | todo | Add chapter read/write service. |
| 3.5 | todo | Add graph node and edge read/write service. |
| 3.6 | todo | Add integration decision read/write service. |
| 3.7 | todo | Add RAG chunk and chat history read/write service. |
| 3.8 | todo | Update architecture with concrete database structure. |

## Phase 4: Frontend Minimal Skeleton

| Step | Status | Notes |
| --- | --- | --- |
| 4.1 | todo | Initialize React, Vite, TypeScript frontend. |
| 4.2 | todo | Build three-column layout. |
| 4.3 | todo | Create frontend API client module. |
| 4.4 | todo | Create base frontend types. |
| 4.5 | todo | Create feature hooks or lightweight global state. |
| 4.6 | todo | Update architecture with frontend boundaries. |

## Phase 5: Textbook Upload And File Management

| Step | Status | Notes |
| --- | --- | --- |
| 5.1 | todo | Implement backend multi-file upload. |
| 5.2 | todo | Add file format validation. |
| 5.3 | todo | Store file metadata and parse status. |
| 5.4 | todo | Implement drag-and-drop and click upload. |
| 5.5 | todo | Implement frontend file list. |
| 5.6 | todo | Verify runtime data is ignored by git. |
| 5.7 | todo | Update architecture with upload flow. |

## Phase 6: Textbook Parsing

| Step | Status | Notes |
| --- | --- | --- |
| 6.1 | todo | Implement TXT parsing. |
| 6.2 | todo | Implement Markdown parsing. |
| 6.3 | todo | Implement PDF page-by-page text extraction. |
| 6.4 | todo | Implement PDF chapter title detection. |
| 6.5 | todo | Implement PDF fallback chapter splitting. |
| 6.6 | todo | Implement basic header/footer filtering. |
| 6.7 | todo | Connect parsing to task status. |
| 6.8 | todo | Show chapter tree and summaries in frontend. |
| 6.9 | todo | Update architecture with parsing flow. |

## Phase 7: LLM Provider And Prompt Management

| Step | Status | Notes |
| --- | --- | --- |
| 7.1 | todo | Create OpenAI-compatible LLM provider abstraction. |
| 7.2 | todo | Support configurable model and base URL. |
| 7.3 | todo | Create prompt management directory. |
| 7.4 | todo | Add JSON validation and repair flow. |
| 7.5 | todo | Record LLM call size and latency. |
| 7.6 | todo | Update architecture with provider and prompt boundaries. |

## Phase 8: Single-Textbook Knowledge Graph

| Step | Status | Notes |
| --- | --- | --- |
| 8.1 | todo | Define knowledge node schema. |
| 8.2 | todo | Define knowledge edge schema. |
| 8.3 | todo | Extract knowledge points by chapter. |
| 8.4 | todo | Extract relationships by chapter. |
| 8.5 | todo | Isolate chapter extraction failures. |
| 8.6 | todo | Persist graph nodes, edges, and provenance. |
| 8.7 | todo | Add single-textbook graph query endpoint. |
| 8.8 | todo | Update architecture with graph extraction flow. |

## Phase 9: Graph Visualization

| Step | Status | Notes |
| --- | --- | --- |
| 9.1 | todo | Render mock graph with Cytoscape.js. |
| 9.2 | todo | Render real textbook graph. |
| 9.3 | todo | Add node detail interaction. |
| 9.4 | todo | Add zoom and canvas drag. |
| 9.5 | todo | Add node drag. |
| 9.6 | todo | Add textbook source color mapping. |
| 9.7 | todo | Add frequency size or shade mapping. |
| 9.8 | todo | Add graph search and highlight. |
| 9.9 | todo | Update architecture with graph visualization rules. |

## Phase 10: Embedding And Vector Index

| Step | Status | Notes |
| --- | --- | --- |
| 10.1 | todo | Create embedding provider abstraction. |
| 10.2 | todo | Support OpenAI-compatible embedding configuration. |
| 10.3 | todo | Reserve local embedding fallback path. |
| 10.4 | todo | Add FAISS save/load service. |
| 10.5 | todo | Add internal vector retrieval service. |
| 10.6 | todo | Update architecture with embedding and index design. |

## Phase 11: Cross-Textbook Graph Integration

| Step | Status | Notes |
| --- | --- | --- |
| 11.1 | todo | Implement concept normalization. |
| 11.2 | todo | Generate embeddings for graph nodes. |
| 11.3 | todo | Recall similar cross-textbook candidates. |
| 11.4 | todo | Generate integration decisions. |
| 11.5 | todo | Add LLM review for medium-confidence candidates. |
| 11.6 | todo | Generate merged result nodes. |
| 11.7 | todo | Compute compression statistics. |
| 11.8 | todo | Enforce 30 percent compression limit. |
| 11.9 | todo | Add integration decision list endpoint. |
| 11.10 | todo | Show decisions and compression stats in frontend. |
| 11.11 | todo | Update architecture with integration strategy. |

## Phase 12: RAG Chunking

| Step | Status | Notes |
| --- | --- | --- |
| 12.1 | todo | Chunk chapter body text. |
| 12.2 | todo | Use default 500 to 800 character chunk size. |
| 12.3 | todo | Use default 50 to 100 character overlap. |
| 12.4 | todo | Preserve chunk metadata. |
| 12.5 | todo | Persist chunks. |
| 12.6 | todo | Update architecture with chunking strategy. |

## Phase 13: RAG Index And Retrieval

| Step | Status | Notes |
| --- | --- | --- |
| 13.1 | todo | Add RAG index build endpoint. |
| 13.2 | todo | Embed chunks and write FAISS index. |
| 13.3 | todo | Add index status endpoint. |
| 13.4 | todo | Add question embedding and top-5 retrieval. |
| 13.5 | todo | Add relevance scores. |
| 13.6 | todo | Optionally add BM25 search. |
| 13.7 | todo | Optionally merge vector and BM25 results. |
| 13.8 | todo | Update architecture with retrieval flow. |

## Phase 14: RAG Answering With Citations

| Step | Status | Notes |
| --- | --- | --- |
| 14.1 | todo | Create grounded answering prompt. |
| 14.2 | todo | Inject only top retrieved chunks into answer context. |
| 14.3 | todo | Generate answer text. |
| 14.4 | todo | Generate citation list. |
| 14.5 | todo | Prevent fabricated citations. |
| 14.6 | todo | Add frontend RAG question and answer UI. |
| 14.7 | todo | Expand citations to show source chunks. |
| 14.8 | todo | Update architecture with RAG answer flow. |

## Phase 15: Teacher Feedback

| Step | Status | Notes |
| --- | --- | --- |
| 15.1 | todo | Persist chat sessions and messages. |
| 15.2 | todo | Explain integration decisions. |
| 15.3 | todo | Parse feedback to keep removed nodes. |
| 15.4 | todo | Parse feedback to split incorrect merges. |
| 15.5 | todo | Parse feedback to force merge nodes. |
| 15.6 | todo | Add frontend teacher chat panel. |
| 15.7 | todo | Refresh graph and stats after feedback. |
| 15.8 | todo | Update architecture with feedback flow. |

## Phase 16: Integration Report

| Step | Status | Notes |
| --- | --- | --- |
| 16.1 | todo | Add report generation service. |
| 16.2 | todo | Include integration overview. |
| 16.3 | todo | Include decision summary. |
| 16.4 | todo | Include graph statistics. |
| 16.5 | todo | Include 3 to 5 key cases. |
| 16.6 | todo | Include teaching completeness analysis. |
| 16.7 | todo | Add frontend report preview. |
| 16.8 | todo | Update architecture with report generation path. |

## Phase 17: Core Documentation

| Step | Status | Notes |
| --- | --- | --- |
| 17.1 | todo | Write README. |
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
| 18.4 | todo | Test cross-textbook integration flow. |
| 18.5 | todo | Test compression statistics. |
| 18.6 | todo | Test RAG question answering. |
| 18.7 | todo | Test teacher feedback updates. |
| 18.8 | todo | Test report generation. |
| 18.9 | todo | Check modularity constraints. |
| 18.10 | todo | Check repository cleanliness. |

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
