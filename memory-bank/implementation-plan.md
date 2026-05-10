# Implementation Plan

This document gives AI developers a small-step implementation plan. It is based on `memory-bank/design-document.md`, `memory-bank/tech-stack.md`, `memory-bank/architecture.md`, `memory-bank/progress.md`, and `AGENTS.md`.

No code belongs in this document. Every step must be completed with its verification before moving on.

## Global Rules

| Step | Instruction | Verification |
| --- | --- | --- |
| G-01 | Before writing any code, fully read `memory-bank/architecture.md`. | The developer can summarize current modules, data flow, storage strategy, and known database decisions. |
| G-02 | Before writing any code, fully read `memory-bank/design-document.md`. | The developer can summarize the P0 product loop and acceptance expectations. |
| G-03 | Before writing any code, fully read `memory-bank/tech-stack.md`. | The developer can confirm the approved stack and the technologies that should not be introduced. |
| G-04 | Before writing any code, check `memory-bank/progress.md`. | The developer can identify the current step and does not duplicate completed work. |
| G-05 | Keep the project modular and multi-file. | New or changed files have clear single responsibilities and no giant all-in-one implementation appears. |
| G-06 | After every major feature, milestone, schema change, API change, or data-flow change, update `memory-bank/architecture.md`. | The architecture document reflects the implemented reality, not stale intent. |
| G-07 | After every completed step, update `memory-bank/progress.md`. | The relevant step status changes to `done`, `blocked`, or `skipped` with a short note. |

## Phase 0: Memory Bank Alignment

| Step | Instruction | Verification |
| --- | --- | --- |
| 0.1 | Confirm the memory bank contains `architecture.md`, `design-document.md`, `implementation-plan.md`, `tech-stack.md`, and `progress.md`. | All five files exist under `memory-bank/`. |
| 0.2 | Confirm `architecture.md` is non-empty and says database schema can evolve incrementally. | The document contains current architecture principles and planned entities. |
| 0.3 | Confirm `design-document.md` is the product planning source. | The document contains the P0 loop and feature requirements. |
| 0.4 | Confirm `implementation-plan.md` uses English file names only. | No references to old Chinese file names remain. |
| 0.5 | Confirm `progress.md` tracks implementation at step-level granularity. | Progress entries align with this plan’s step numbers. |

## Phase 1: Repository Structure

| Step | Instruction | Verification |
| --- | --- | --- |
| 1.1 | Create the top-level implementation directories: backend, frontend, data, report, and memory-bank. | The repository root has those directories and no duplicate planning directory. |
| 1.2 | Create backend module folders for API, configuration, models, schemas, services, prompts, and storage. | Backend responsibilities are split by folder, not placed into one file. |
| 1.3 | Create frontend module folders for API client, reusable components, feature areas, hooks, and shared types. | Frontend responsibilities are split by folder, not placed into one component. |
| 1.4 | Add repository ignore rules for uploaded textbooks, PDF files, database files, indexes, caches, secrets, and runtime data. | Git status does not show generated runtime files after a local test artifact is created. |
| 1.5 | Add environment example documentation for model keys, OpenAI-compatible base URL, model names, data directory, and database path. | A developer can identify required environment variables without reading source code. |
| 1.6 | Update `memory-bank/architecture.md` with the actual repository structure. | Architecture paths match the created directories. |
| 1.7 | Update `memory-bank/progress.md`. | Phase 1 completed steps are marked with verification notes. |

## Phase 2: Backend Skeleton

| Step | Instruction | Verification |
| --- | --- | --- |
| 2.1 | Initialize the FastAPI backend entrypoint. | Backend starts and exposes a basic health response. |
| 2.2 | Add centralized configuration loading. | Environment variables override defaults without changing application code. |
| 2.3 | Add a consistent error response convention. | Invalid requests return structured errors with a clear message. |
| 2.4 | Add task status handling for pending, running, completed, and failed. | A simulated task can be created, queried, and marked failed with an error reason. |
| 2.5 | Add the minimal backend dependency file. | Dependencies install without unrelated frameworks. |
| 2.6 | Update `memory-bank/architecture.md` with backend startup, configuration, and task status design. | Architecture matches the implemented backend skeleton. |
| 2.7 | Update `memory-bank/progress.md`. | Phase 2 completed steps are marked with verification notes. |

## Phase 3: Database And Persistence

| Step | Instruction | Verification |
| --- | --- | --- |
| 3.1 | Define the first SQLite schema iteration for textbooks, chapters, tasks, graph nodes, graph edges, integration decisions, RAG chunks, chat sessions, and chat messages. | `memory-bank/architecture.md` records the concrete schema before or alongside implementation. |
| 3.2 | Add database initialization. | First backend startup creates the database, and repeated startup does not erase data. |
| 3.3 | Add persistence for textbook metadata. | A textbook record can be created and read back. |
| 3.4 | Add persistence for parsed chapters. | Multiple chapters can be stored and retrieved in order for a textbook. |
| 3.5 | Add persistence for graph nodes and edges. | Nodes and edges can be stored and retrieved with provenance. |
| 3.6 | Add persistence for integration decisions. | Merge, keep, and remove decisions can be stored and updated. |
| 3.7 | Add persistence for RAG chunks and chat history. | Chunks and chat messages survive backend restart. |
| 3.8 | Update `memory-bank/architecture.md` with final Phase 3 schema details. | All implemented tables and fields are documented. |
| 3.9 | Update `memory-bank/progress.md`. | Phase 3 completed steps are marked with verification notes. |

## Phase 4: Frontend Skeleton

| Step | Instruction | Verification |
| --- | --- | --- |
| 4.1 | Initialize React, Vite, and TypeScript. | Frontend starts and renders a basic page. |
| 4.2 | Build the three-column layout: textbook management, graph canvas, and function panel. | The layout is usable at 1920 by 1080 resolution. |
| 4.3 | Add a centralized frontend API client. | Components do not construct raw request details directly. |
| 4.4 | Add shared frontend types for textbooks, chapters, graph nodes, graph edges, decisions, chunks, citations, and tasks. | Components use typed data shapes instead of ad hoc fields. |
| 4.5 | Add lightweight feature state handling. | Upload, graph, integration, RAG, and chat areas can share needed state without a heavy state library. |
| 4.6 | Update `memory-bank/architecture.md` with frontend module boundaries. | Architecture names the feature folders and responsibilities. |
| 4.7 | Update `memory-bank/progress.md`. | Phase 4 completed steps are marked with verification notes. |

## Phase 5: Textbook Upload

| Step | Instruction | Verification |
| --- | --- | --- |
| 5.1 | Implement backend multi-file upload. | Uploading a small TXT file creates a textbook record and stores the file. |
| 5.2 | Validate accepted formats: PDF, Markdown, TXT, and optionally DOCX. | Unsupported files fail with a clear error. |
| 5.3 | Store file metadata: original name, format, size, saved path, and parse status. | Textbook list returns all metadata fields. |
| 5.4 | Add frontend drag-and-drop upload. | Dragging one or more files into the upload zone submits them. |
| 5.5 | Add frontend click-to-select upload. | Selecting one or more files through the file picker submits them. |
| 5.6 | Add a textbook list with status display. | Uploaded files show name, format, size, and status after refresh. |
| 5.7 | Verify runtime files are ignored. | Uploaded test files do not appear as tracked Git changes. |
| 5.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Upload flow and progress are current. |

## Phase 6: Textbook Parsing

| Step | Instruction | Verification |
| --- | --- | --- |
| 6.1 | Implement TXT parsing. | A TXT sample produces at least one chapter and character count. |
| 6.2 | Implement Markdown parsing by headings. | A Markdown sample with headings produces chapter records. |
| 6.3 | Implement PDF page-by-page text extraction. | A PDF sample reports total pages and extracted characters. |
| 6.4 | Add PDF chapter heading detection. | A PDF containing chapter headings produces chapter boundaries. |
| 6.5 | Add PDF fallback chapter splitting. | A PDF without recognizable headings still produces usable chapters. |
| 6.6 | Add basic repeated header and footer filtering. | Repeated page noise is reduced in extracted chapter content. |
| 6.7 | Connect parsing to task status. | Parsing state changes from running to completed or failed. |
| 6.8 | Show chapter tree and summaries in the frontend. | Selecting a textbook displays chapter title, page range, and character count. |
| 6.9 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Parsing flow and progress are current. |

## Phase 7: LLM Provider And Prompts

| Step | Instruction | Verification |
| --- | --- | --- |
| 7.1 | Add an OpenAI-compatible LLM provider boundary. | Business services call the provider abstraction, not vendor-specific code. |
| 7.2 | Support configurable base URL, API key, and model names. | Switching compatible providers does not require business logic changes. |
| 7.3 | Organize prompts by task: extraction, alignment, RAG answering, and teacher feedback. | Prompts are not scattered through route handlers or UI components. |
| 7.4 | Add JSON validation and one repair attempt for structured LLM outputs. | Invalid model output is either repaired or fails with a clear error. |
| 7.5 | Track LLM call latency and approximate token usage when available. | A completed LLM task has observable call metadata. |
| 7.6 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Provider and prompt architecture are current. |

## Phase 8: Knowledge Graph Extraction

| Step | Instruction | Verification |
| --- | --- | --- |
| 8.1 | Define the graph node data contract. | Nodes include id, name, definition, category, textbook, chapter, page, and source excerpt. |
| 8.2 | Define the graph edge data contract. | Edges support at least three required relation types. |
| 8.3 | Extract knowledge nodes chapter by chapter. | A short sample chapter produces structured nodes. |
| 8.4 | Extract relationships chapter by chapter. | Extracted edges point to valid nodes. |
| 8.5 | Isolate chapter-level extraction failures. | One failed chapter does not stop other chapters. |
| 8.6 | Persist graph nodes, edges, and provenance. | Graph query returns source-backed nodes and edges. |
| 8.7 | Add single-textbook graph retrieval. | Frontend can request graph data for a selected textbook. |
| 8.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Graph extraction architecture and progress are current. |

## Phase 9: Graph Visualization

| Step | Instruction | Verification |
| --- | --- | --- |
| 9.1 | Render a mock graph with Cytoscape.js. | Nodes and edges appear in the graph area. |
| 9.2 | Render real graph data from the backend. | Selecting a processed textbook shows its graph. |
| 9.3 | Add node click details. | Clicking a node shows definition, chapter, page, and source excerpt. |
| 9.4 | Add zoom and canvas dragging. | Mouse interactions work without page errors. |
| 9.5 | Add node dragging. | Individual nodes can be repositioned. |
| 9.6 | Add textbook source color mapping. | Nodes from different textbooks are visually distinct. |
| 9.7 | Add frequency-based size or shade mapping. | More frequent concepts appear more prominent. |
| 9.8 | Add graph search and highlight. | Keyword matches are highlighted and can be cleared. |
| 9.9 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Visualization rules and progress are current. |

## Phase 10: Embedding And Vector Index

| Step | Instruction | Verification |
| --- | --- | --- |
| 10.1 | Add an OpenAI-compatible embedding provider boundary. | Retrieval services call the provider abstraction. |
| 10.2 | Support configurable embedding model and base URL. | Compatible providers can be swapped by configuration. |
| 10.3 | Leave a documented local embedding fallback path. | Missing local dependencies fail clearly if local mode is selected. |
| 10.4 | Add FAISS index save and load. | An index can be built, saved, and loaded after restart. |
| 10.5 | Add internal vector retrieval. | A query returns similar items with scores. |
| 10.6 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Embedding and index architecture are current. |

## Phase 11: Cross-Textbook Integration

| Step | Instruction | Verification |
| --- | --- | --- |
| 11.1 | Add concept normalization. | Simple spelling, spacing, and casing differences normalize consistently. |
| 11.2 | Generate embeddings for graph nodes. | Nodes can be compared semantically. |
| 11.3 | Recall similar concepts across textbooks. | Given one concept, similar candidates from other textbooks are returned. |
| 11.4 | Generate merge, keep, and remove decisions. | Decisions include affected nodes, result node when relevant, reason, confidence, and status. |
| 11.5 | Use LLM review for medium-confidence candidates. | Ambiguous matches receive model-backed reasoning. |
| 11.6 | Generate merged result nodes. | Merged concepts preserve source list and provenance. |
| 11.7 | Compute compression statistics. | Original characters, integrated characters, and compression percentage are shown. |
| 11.8 | Enforce the 30 percent compression target. | Integrated content does not exceed the target unless explicitly marked as unresolved. |
| 11.9 | Add integration decision retrieval. | Frontend can list decisions and details. |
| 11.10 | Show decisions and compression stats in the frontend. | User sees merge, keep, remove counts and compression ratio. |
| 11.11 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Integration architecture and progress are current. |

## Phase 12: RAG Chunking

| Step | Instruction | Verification |
| --- | --- | --- |
| 12.1 | Chunk chapter text. | Long chapters split into multiple chunks. |
| 12.2 | Use a default chunk size around 500 to 800 Chinese characters. | Most chunks fall within the target range. |
| 12.3 | Use overlap around 50 to 100 Chinese characters. | Adjacent chunks share enough text to avoid boundary loss. |
| 12.4 | Preserve chunk metadata. | Every chunk has textbook, chapter, page, and chunk id. |
| 12.5 | Persist chunks. | Chunks remain queryable after restart. |
| 12.6 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Chunking architecture and progress are current. |

## Phase 13: RAG Retrieval

| Step | Instruction | Verification |
| --- | --- | --- |
| 13.1 | Add RAG index build trigger. | Indexing task reaches completed status for parsed textbooks. |
| 13.2 | Embed chunks and write FAISS index. | Index size matches stored chunk count. |
| 13.3 | Add index status query. | Frontend sees indexed textbook count and chunk count. |
| 13.4 | Retrieve top five chunks for a question. | Relevant questions return ranked chunks. |
| 13.5 | Include relevance scores. | Results are sortable by score. |
| 13.6 | Optionally add BM25 keyword retrieval. | Keyword-heavy questions retrieve matching chunks. |
| 13.7 | Optionally merge vector and BM25 results. | Merged results are deduplicated. |
| 13.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Retrieval architecture and progress are current. |

## Phase 14: RAG Answering

| Step | Instruction | Verification |
| --- | --- | --- |
| 14.1 | Create grounded answering behavior. | Unanswerable questions return “当前知识库中未找到相关信息”. |
| 14.2 | Use only retrieved chunks as answer context. | No answer depends on unprovided model knowledge. |
| 14.3 | Generate answer text. | Relevant textbook questions receive readable answers. |
| 14.4 | Generate citation list. | Citations include textbook, chapter, page, relevance score, and chunk id. |
| 14.5 | Prevent fabricated citations. | Every citation maps to an existing stored chunk. |
| 14.6 | Add frontend RAG question and answer UI. | User can ask and see an answer. |
| 14.7 | Add citation expansion. | User can expand a citation to see original chunk text. |
| 14.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | RAG answering architecture and progress are current. |

## Phase 15: Teacher Feedback

| Step | Instruction | Verification |
| --- | --- | --- |
| 15.1 | Persist chat sessions and messages. | Conversation survives page refresh. |
| 15.2 | Explain integration decisions. | Asking why a decision happened returns decision reason and affected nodes. |
| 15.3 | Support feedback to keep a removed node. | Decision and graph update after the instruction. |
| 15.4 | Support feedback to split an incorrect merge. | Merge decision is revised or disabled. |
| 15.5 | Support feedback to force merge nodes. | New or updated merge decision appears. |
| 15.6 | Add frontend teacher chat panel. | User can send messages and see history. |
| 15.7 | Refresh graph and statistics after feedback. | Visible graph, decisions, and compression stats stay consistent. |
| 15.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Feedback architecture and progress are current. |

## Phase 16: Report Generation

| Step | Instruction | Verification |
| --- | --- | --- |
| 16.1 | Add report generation service. | A Markdown report appears under `report/`. |
| 16.2 | Include integration overview. | Report shows textbook count, original characters, integrated characters, and compression ratio. |
| 16.3 | Include decision summary. | Report shows merge, keep, and remove counts. |
| 16.4 | Include graph statistics. | Report shows node and edge changes before and after integration. |
| 16.5 | Include three to five key cases. | Each case includes action, affected nodes, reason, and source. |
| 16.6 | Include teaching completeness analysis. | Report explains whether learning chains remain intact. |
| 16.7 | Add frontend report preview. | User can view generated report content or status. |
| 16.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Report architecture and progress are current. |

## Phase 17: Required Documentation

| Step | Instruction | Verification |
| --- | --- | --- |
| 17.1 | Write README. | A new developer can install, configure, run, and use the app. |
| 17.2 | Write `memory-bank/requirements-analysis.md`. | It covers concept granularity, duplicate criteria, teaching continuity, compression, and RAG chunking. |
| 17.3 | Write `memory-bank/system-design.md`. | It covers architecture, data flow, technical choices, and API overview. |
| 17.4 | Write `memory-bank/agent-architecture.md`. | It covers architecture overview, design decisions, call chain, tradeoffs, and innovation points. |
| 17.5 | Optionally write `memory-bank/api-documentation.md`. | It documents major endpoints and response shapes. |
| 17.6 | Check documentation consistency. | Documentation matches implemented behavior. |
| 17.7 | Update `memory-bank/progress.md`. | Documentation progress is current. |

## Phase 18: Testing And Quality

| Step | Instruction | Verification |
| --- | --- | --- |
| 18.1 | Prepare repeatable TXT, Markdown, and PDF samples. | Each sample can be uploaded and parsed locally. |
| 18.2 | Test upload and parsing. | Status, chapters, and character counts appear in the frontend. |
| 18.3 | Test graph construction. | Nodes, edges, and node details appear. |
| 18.4 | Test cross-textbook integration. | At least one duplicate concept produces a merge decision. |
| 18.5 | Test compression statistics. | UI numbers match persisted statistics. |
| 18.6 | Test RAG answering. | Relevant questions cite correct chunks; unrelated questions say not found. |
| 18.7 | Test teacher feedback. | A feedback message changes at least one decision and refreshes graph or stats. |
| 18.8 | Test report generation. | Report numbers match system statistics. |
| 18.9 | Check modularity. | No giant file or mixed-responsibility module was introduced. |
| 18.10 | Check repository cleanliness. | Git does not include data files, secrets, indexes, caches, or uploaded textbooks. |

## Phase 19: RAG Benchmark Enhancement

| Step | Instruction | Verification |
| --- | --- | --- |
| 19.1 | Prepare 20 benchmark questions. | Questions cover factual, comparative, reasoning, and cross-textbook cases. |
| 19.2 | Label expected answer points. | Each question has a ground-truth answer outline. |
| 19.3 | Label expected citations. | Each question has expected source chapters or pages where possible. |
| 19.4 | Run benchmark. | Each question records answer, citations, latency, and hit status. |
| 19.5 | Compute metrics. | Accuracy, citation hit rate, and average latency are summarized. |
| 19.6 | Optionally compare chunk sizes. | At least two chunk settings have comparable metrics. |
| 19.7 | Write results into memory-bank documentation. | Benchmark findings are visible to reviewers and developers. |
| 19.8 | Update `memory-bank/architecture.md` and `memory-bank/progress.md`. | Benchmark role and progress are current. |

## Phase 20: Deployment And Final Acceptance

| Step | Instruction | Verification |
| --- | --- | --- |
| 20.1 | Prepare local startup instructions. | A new developer can start backend and frontend from README. |
| 20.2 | Optionally prepare Docker Compose. | Docker startup works if included. |
| 20.3 | Verify missing environment variable behavior. | Missing model configuration fails clearly, not silently. |
| 20.4 | Run the full P0 demo flow. | Upload, parse, graph, integrate, index, answer, feedback, and report all work. |
| 20.5 | Run browser smoke testing. | Refresh, textbook switching, graph search, citation expansion, and report preview work. |
| 20.6 | Check README against real commands and behavior. | README does not contain stale setup instructions. |
| 20.7 | Check `memory-bank/agent-architecture.md`. | It clearly explains the modular single-agent orchestration decision. |
| 20.8 | Check `report/整合报告.md`. | It contains overview, decision summary, graph stats, key cases, and teaching completeness. |
| 20.9 | Final-check `memory-bank/architecture.md`. | It matches the final implementation, especially database and API boundaries. |
| 20.10 | Final-check git status. | Only source and intended documentation are ready to commit. |

## Minimum Demo Standard

| Capability | Verification |
| --- | --- |
| Upload | Batch PDF, Markdown, and TXT upload shows metadata and status. |
| Parsing | At least one PDF produces chapters, with fallback for hard PDFs. |
| Graph | At least one textbook produces nodes and edges in the browser. |
| Graph interaction | Node details, zoom, drag, source colors, and search work. |
| Integration | At least two textbooks produce decisions and compression stats. |
| RAG | A question returns answer, citations, scores, and expandable chunks. |
| Feedback | A teacher message modifies at least one integration decision. |
| Report | `report/整合报告.md` is generated from actual system data. |
| Documentation | README and memory-bank documents match implementation. |
| Architecture memory | `memory-bank/architecture.md` reflects final database, APIs, modules, and data flow. |
