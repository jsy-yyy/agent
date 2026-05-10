# Tech Stack

## 目标

本项目采用“最简单但最健壮”的技术栈：优先保证 5 小时内可完成、可部署、可演示、可复现。原则是少引入组件，避免微服务和复杂基础设施，把主要复杂度留给教材解析、知识图谱、整合决策和 RAG 质量。

## 推荐最终选型

| 层级 | 技术 | 选择理由 |
| --- | --- | --- |
| 前端框架 | React + Vite + TypeScript | 启动快、生态成熟、类型安全，适合快速做 SPA。 |
| UI 实现 | 原生 CSS + 少量组件封装 | 避免 UI 库配置成本，减少样式冲突，比赛中更可控。 |
| 图谱可视化 | Cytoscape.js | 专注图谱交互，节点点击、缩放、拖拽、布局能力稳定。 |
| 后端框架 | FastAPI | API 开发快，自带 Swagger，适合文件上传、异步任务和 Python AI 生态。 |
| 文件解析 | PyMuPDF + Markdown/TXT 原生读取 | PyMuPDF 解析 PDF 稳定且速度快，MD/TXT 无额外依赖。 |
| DOCX 解析 | python-docx，可选 | 作为加分项保留，不阻塞 P0 主链路。 |
| 数据库 | SQLite | 零运维、单文件、部署简单，足够支撑比赛数据规模。 |
| 文件存储 | 本地文件系统 | 上传教材、中间 JSON、报告和索引用目录管理，简单可靠。 |
| 向量索引 | FAISS | 本地运行、轻量、速度快，不需要额外服务。 |
| 关键词检索 | rank-bm25，可选 | 用于 P1 混合检索，加分明显，实现成本低。 |
| Embedding | OpenAI Embedding API 优先，本地 BGE 作为备选 | API 方案最省时间；如果网络或 Key 不可用，可切换本地模型。 |
| LLM | 统一 Provider 层适配 OpenAI / DeepSeek / 通义千问 | 避免模型绑定，降低 API 不稳定风险。 |
| 后台任务 | FastAPI BackgroundTasks | 不引入 Celery/Redis，足够处理解析、抽取、索引构建。 |
| 配置管理 | `.env` + `.env.example` | 统一管理 API Key、模型名、上传目录和索引目录。 |
| 部署 | Docker Compose，可选；本地启动脚本必须有 | 本地可复现优先，Docker 作为加分和部署兜底。 |

## 技术栈取舍

### 前端

采用 React + Vite + TypeScript。React 负责页面状态和组件组织，Vite 保证开发启动快，TypeScript 降低接口字段变更带来的隐性 bug。

不使用复杂状态管理库。全局状态优先用 React Context 或简单 hooks 管理，因为本项目页面虽大，但状态主要围绕教材、图谱、整合决策、RAG 会话四类数据，不需要 Redux/Zustand 这类额外抽象。

图谱使用 Cytoscape.js，而不是 D3.js。D3 自由度高但开发成本更高；Cytoscape.js 对节点、边、布局、点击、缩放、拖拽的支持更直接，更适合黑客松快速稳定交付。

### 后端

采用 FastAPI 单体后端。所有功能通过一个后端服务提供，包括上传、解析、知识抽取、图谱构建、整合、RAG、对话和报告生成。

不拆微服务，不引入消息队列。解析和索引用 FastAPI BackgroundTasks 处理即可，前端通过状态接口轮询任务进度。这样部署最简单，也减少比赛现场服务互相连不上的风险。

### 存储

结构化数据放 SQLite，原始文件和中间产物放本地目录。

推荐目录：

```text
data/
  uploads/
  parsed/
  graphs/
  indexes/
  reports/
```

SQLite 适合保存教材元信息、章节、知识点、关系、整合决策、RAG chunk、聊天历史和任务状态。大文本和向量索引不直接塞进数据库，避免数据库文件膨胀和读写变慢。

### AI 与检索

LLM 和 Embedding 都通过 Provider 层调用。业务代码只依赖内部接口，不直接依赖某个厂商 SDK。

推荐接口：

```python
class LLMProvider:
    def generate_json(self, prompt: str, schema_name: str) -> dict: ...
    def generate_text(self, prompt: str) -> str: ...

class EmbeddingProvider:
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
```

Embedding 默认使用 OpenAI API，原因是接入最快、效果稳定、部署包更轻。本地模型作为备选，可以选择 BGE-small-zh 或 paraphrase-multilingual-MiniLM-L12-v2，但不建议一开始就把本地模型作为唯一方案，因为模型下载、依赖和部署环境会增加风险。

向量库选择 FAISS。它不需要单独启动服务，索引可以保存到 `data/indexes/`，非常适合单机演示。

## 不推荐引入的技术

- 不推荐 LangChain 全家桶：抽象多、调试成本高，比赛中容易被框架问题拖慢。
- 不推荐 CrewAI/AutoGen：多 Agent 编排很酷，但本赛题更需要稳定闭环，硬拆 Agent 风险大。
- 不推荐 Neo4j：图数据库很适合知识图谱，但部署和查询成本高，前端展示并不依赖它。
- 不推荐 PostgreSQL：比 SQLite 更强，但需要额外服务，当前规模用不上。
- 不推荐 Redis/Celery：任务量不需要分布式队列，BackgroundTasks 足够。
- 不推荐 Next.js：本项目不需要 SSR，Vite SPA 更轻。
- 不推荐 ChromaDB/Qdrant 作为首选：能力强，但多一个服务或持久化组件，FAISS 更简单。

## 最小依赖清单

### Python

```text
fastapi
uvicorn[standard]
python-multipart
pydantic
pydantic-settings
PyMuPDF
python-docx
numpy
faiss-cpu
openai
rank-bm25
```

可选依赖：

```text
sentence-transformers
```

### Node

```text
react
react-dom
vite
typescript
cytoscape
```

可选依赖：

```text
@vitejs/plugin-react
```

## 环境变量

```bash
OPENAI_API_KEY=
OPENAI_BASE_URL=
LLM_MODEL=
EMBEDDING_MODEL=
DATA_DIR=./data
DATABASE_URL=sqlite:///./data/app.db
```

如果接入 DeepSeek 或通义千问，可以继续使用兼容 OpenAI API 的 `OPENAI_BASE_URL`，从而避免改业务代码。

## 推荐项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   ├── hooks/
│   │   └── App.tsx
│   └── package.json
├── data/
│   └── .gitkeep
├── memory-bank/
├── report/
├── .env.example
├── .gitignore
└── README.md
```

## 健壮性设计

- 所有 LLM JSON 输出必须做 schema 校验，失败后自动请求模型修复一次。
- 每个后台任务都有状态：`pending`、`running`、`completed`、`failed`。
- 文件解析失败不影响其他文件，前端逐文件显示失败原因。
- PDF 章节识别失败时，按页数自动兜底切分。
- RAG 找不到足够上下文时，固定回答“当前知识库中未找到相关信息”。
- 所有引用必须来自 chunk 元数据，不允许模型自由编造引用。
- 所有上传教材和 PDF 文件必须加入 `.gitignore`。

## 实施顺序

1. 搭 FastAPI + React/Vite 基础骨架。
2. 实现上传、解析、SQLite 存储和文件状态。
3. 实现知识抽取和 Cytoscape.js 图谱。
4. 实现 embedding、FAISS 索引和 RAG 问答。
5. 实现跨教材整合决策和压缩比统计。
6. 实现教师反馈修改决策。
7. 补齐文档、报告、`.env.example` 和部署说明。

## 最终结论

最稳妥的方案是单体 FastAPI 后端 + React SPA 前端 + SQLite + 本地文件系统 + FAISS。它牺牲了一些大型系统的扩展性，但换来了更低的开发成本、更少的部署风险和更高的比赛现场稳定性。对于本赛题，完成度和可解释闭环比技术堆叠更重要。
