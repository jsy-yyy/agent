# 学科知识整合智能体 (Knowledge Integration Agent)

## Overview

A web application that automatically parses multiple textbooks, builds knowledge graphs, performs cross-textbook deduplication and integration, provides RAG-based question answering with citations, and supports teacher feedback for iterative refinement.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your LLM provider credentials
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | API key for OpenAI-compatible provider |
| `OPENAI_BASE_URL` | Base URL (e.g., `https://api-inference.modelscope.cn/v1`) |
| `LLM_MODEL` | Model for text/JSON generation |
| `LLM_ENABLE_THINKING` | Optional provider flag, set `false` for Qwen3 on ModelScope |
| `EMBEDDING_MODEL` | Model for embeddings |
| `EMBEDDING_DIMENSION` | Embedding vector dimension used by FAISS |
| `DATA_DIR` | Runtime data directory (default: `./data`) |
| `DATABASE_URL` | SQLite database URL |

## Features

- **Textbook Upload**: PDF, Markdown, TXT with drag-and-drop
- **Chapter Parsing**: Heading detection, page extraction, header/footer filtering
- **Knowledge Graph**: Per-chapter LLM extraction with nodes, edges, and provenance
- **Graph Visualization**: Cytoscape.js with source colors, search, node details
- **Cross-Textbook Integration**: Embedding similarity + LLM review for merge/keep decisions
- **RAG Q&A**: Chunking, FAISS indexing, retrieval with citations
- **Teacher Feedback**: Chat interface for reviewing and modifying integration decisions
- **Report Generation**: Markdown integration report with statistics

## API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/api/textbooks/upload` | Upload textbooks |
| `GET` | `/api/textbooks` | List textbooks |
| `GET` | `/api/textbooks/{id}` | Textbook detail with chapters |
| `POST` | `/api/textbooks/{id}/parse` | Parse textbook |
| `POST` | `/api/graph/build` | Build knowledge graph |
| `GET` | `/api/graph/{id}` | Get graph data |
| `POST` | `/api/integration/run` | Run cross-textbook integration |
| `GET` | `/api/integration/decisions` | List integration decisions |
| `GET` | `/api/integration/stats` | Integration statistics |
| `POST` | `/api/rag/index` | Build RAG index |
| `GET` | `/api/rag/status` | Index status |
| `POST` | `/api/rag/query` | Query with citations |
| `POST` | `/api/chat` | Teacher feedback chat |
| `GET` | `/api/chat/history` | Chat history |
| `POST` | `/api/report/generate` | Generate report |
| `GET` | `/api/report` | Get report content |

## Testing

```bash
PYTHONPATH=backend pytest backend/tests/
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # HTTP route handlers
│   │   ├── core/         # Configuration, errors, task status
│   │   ├── models/       # Pydantic record models
│   │   ├── schemas/      # Request/response schemas
│   │   ├── services/     # Business logic
│   │   │   ├── embedding/ # Embedding provider + FAISS
│   │   │   ├── llm/      # LLM provider + prompts
│   │   │   └── parsing/  # PDF/MD/TXT parsers
│   │   ├── prompts/      # LLM prompt templates
│   │   └── storage/      # SQLite + file storage
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/          # Typed API client
│       ├── components/   # Reusable UI components
│       ├── features/     # Feature panels
│       ├── hooks/        # State management
│       └── types/        # TypeScript types
├── data/                 # Runtime data (git-ignored)
├── memory-bank/          # Design docs + progress tracking
└── report/               # Generated reports
```

## Tech Stack

- **Frontend**: React, Vite, TypeScript, Cytoscape.js
- **Backend**: FastAPI, Pydantic
- **Database**: SQLite
- **Vector Index**: FAISS
- **LLM**: OpenAI-compatible API (configurable)
- **File Parsing**: PyMuPDF (PDF), native (MD/TXT)
