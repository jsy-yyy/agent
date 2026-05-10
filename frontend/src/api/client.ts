import type {
  Chapter,
  ChatMessage,
  ChatResponse,
  GraphEdge,
  GraphNode,
  IntegrationDecision,
  IntegrationStats,
  RagAnswer,
  ReportState,
  Task,
  Textbook
} from "../types/domain";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    ...init
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface HealthResponse {
  status: string;
  app_name: string;
}

export interface UploadTextbooksResponse {
  textbooks: Textbook[];
}

export interface TextbookDetailResponse {
  textbook_id: string;
  filename: string;
  title: string;
  total_pages: number;
  total_chars: number;
  chapters: Chapter[];
}

export interface GraphDataResponse {
  textbook_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface BuildGraphResponse {
  textbook_id: string;
  task_id: string;
  status: string;
}

export interface IntegrationRunResponse extends IntegrationStats {
  task_id: string;
  status: string;
}

export interface DecisionsResponse {
  decisions: IntegrationDecision[];
}

export interface RagStatusResponse {
  indexed_chunks: number;
  is_loaded: boolean;
}

export interface RagIndexResponse {
  textbook_id: string;
  chunk_count: number;
  status: string;
}

export interface ChatHistoryResponse {
  session: unknown;
  messages: ChatMessage[];
}

export const apiClient = {
  getHealth: () => requestJson<HealthResponse>("/health"),
  createSimulatedTask: () =>
    requestJson<Task>("/api/tasks/simulated", {
      method: "POST"
    }),
  getTask: (taskId: string) => requestJson<Task>(`/api/tasks/${taskId}`),
  listTextbooks: () => requestJson<Textbook[]>("/api/textbooks"),
  getTextbook: (textbookId: string) =>
    requestJson<TextbookDetailResponse>(`/api/textbooks/${textbookId}`),
  parseTextbook: (textbookId: string) =>
    requestJson<Task>(`/api/textbooks/${textbookId}/parse`, {
      method: "POST"
    }),
  buildGraph: (textbookId: string) =>
    requestJson<BuildGraphResponse>(`/api/graph/build`, {
      method: "POST",
      body: JSON.stringify({ textbook_id: textbookId })
    }),
  getGraph: (textbookId: string) =>
    requestJson<GraphDataResponse>(`/api/graph/${textbookId}`),
  getMergedGraph: () =>
    requestJson<GraphDataResponse>("/api/graph/merged"),
  runIntegration: () =>
    requestJson<IntegrationRunResponse>("/api/integration/run", {
      method: "POST"
    }),
  listIntegrationDecisions: () =>
    requestJson<DecisionsResponse>("/api/integration/decisions"),
  getIntegrationStats: () =>
    requestJson<IntegrationStats>("/api/integration/stats"),
  buildRagIndex: (textbookId: string) =>
    requestJson<RagIndexResponse>("/api/rag/index", {
      method: "POST",
      body: JSON.stringify({ textbook_id: textbookId })
    }),
  getRagStatus: () => requestJson<RagStatusResponse>("/api/rag/status"),
  queryRag: (question: string, topK = 5) =>
    requestJson<RagAnswer>("/api/rag/query", {
      method: "POST",
      body: JSON.stringify({ question, top_k: topK })
    }),
  sendChatMessage: (content: string, sessionId?: string | null, decisionId?: string | null) =>
    requestJson<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        content,
        session_id: sessionId ?? undefined,
        decision_id: decisionId ?? undefined
      })
    }),
  getChatHistory: (sessionId?: string | null) =>
    requestJson<ChatHistoryResponse>(
      sessionId ? `/api/chat/history?session_id=${encodeURIComponent(sessionId)}` : "/api/chat/history"
    ),
  generateReport: () =>
    requestJson<{ status: string; path: string }>("/api/report/generate", {
      method: "POST"
    }),
  getReport: () => requestJson<ReportState>("/api/report"),
  resetAllData: () =>
    requestJson<{ status: string; message: string }>("/api/admin/reset", {
      method: "POST"
    }),
  uploadTextbooks: async (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    const response = await fetch(`${API_BASE_URL}/api/textbooks/upload`, {
      method: "POST",
      body: formData
    });
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    return response.json() as Promise<UploadTextbooksResponse>;
  }
};
