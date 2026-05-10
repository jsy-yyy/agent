import { useCallback, useEffect, useMemo, useState } from "react";

import { apiClient } from "../api/client";
import type {
  Chapter,
  ChatMessage,
  GraphEdge,
  GraphNode,
  IntegrationDecision,
  IntegrationStats,
  RagAnswer,
  RagChunk,
  ReportState,
  Task,
  Textbook
} from "../types/domain";

export interface DashboardState {
  textbooks: Textbook[];
  chapters: Chapter[];
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  decisions: IntegrationDecision[];
  integrationStats: IntegrationStats | null;
  chunks: RagChunk[];
  ragAnswer: RagAnswer | null;
  ragStatus: {
    indexed_chunks: number;
    is_loaded: boolean;
  };
  chatMessages: ChatMessage[];
  chatSessionId: string | null;
  report: ReportState;
  currentTask: Task | null;
  selectedTextbookId: string | null;
  graphViewMode: "single" | "merged";
  isLoading: boolean;
  errorMessage: string | null;
  summary: {
    textbookCount: number;
    nodeCount: number;
    edgeCount: number;
    chunkCount: number;
    compressionRatio: number | null;
  };
  refreshTextbooks: () => Promise<void>;
  selectTextbook: (textbookId: string) => Promise<void>;
  uploadTextbooks: (files: File[]) => Promise<void>;
  parseSelectedTextbook: () => Promise<void>;
  buildGraph: () => Promise<void>;
  refreshGraph: () => Promise<void>;
  setGraphViewMode: (mode: "single" | "merged") => Promise<void>;
  runIntegration: () => Promise<void>;
  refreshIntegration: () => Promise<void>;
  buildRagIndex: () => Promise<void>;
  askRag: (question: string) => Promise<void>;
  sendFeedback: (message: string, decisionId?: string | null) => Promise<void>;
  generateReport: () => Promise<void>;
  refreshReport: () => Promise<void>;
  resetData: () => Promise<void>;
}

export function useDashboardState(): DashboardState {
  const [textbooks, setTextbooks] = useState<Textbook[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [decisions, setDecisions] = useState<IntegrationDecision[]>([]);
  const [integrationStats, setIntegrationStats] = useState<IntegrationStats | null>(null);
  const [ragAnswer, setRagAnswer] = useState<RagAnswer | null>(null);
  const [ragStatus, setRagStatus] = useState({ indexed_chunks: 0, is_loaded: false });
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [report, setReport] = useState<ReportState>({ status: "not_generated", content: null });
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [selectedTextbookId, setSelectedTextbookId] = useState<string | null>(null);
  const [graphViewMode, setGraphViewModeState] = useState<"single" | "merged">("single");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshTextbooks = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setTextbooks(await apiClient.listTextbooks());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load textbooks");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectTextbook = useCallback(async (textbookId: string) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const detail = await apiClient.getTextbook(textbookId);
      setSelectedTextbookId(textbookId);
      setChapters(detail.chapters);
      setTextbooks((current) =>
        current.map((textbook) =>
          textbook.textbook_id === textbookId
            ? {
                ...textbook,
                textbook_id: detail.textbook_id,
                filename: detail.filename,
                title: detail.title,
                total_pages: detail.total_pages,
                total_chars: detail.total_chars
              }
            : textbook
        )
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load textbook");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadTextbooks = useCallback(
    async (files: File[]) => {
      if (files.length === 0) {
        return;
      }
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const response = await apiClient.uploadTextbooks(files);
        const first = response.textbooks[0];
        if (first) {
          const detail = await apiClient.getTextbook(first.textbook_id);
          setSelectedTextbookId(first.textbook_id);
          setChapters(detail.chapters);
        }
        await refreshTextbooks();
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to upload textbooks");
      } finally {
        setIsLoading(false);
      }
    },
    [refreshTextbooks]
  );

  const parseSelectedTextbook = useCallback(async () => {
    if (!selectedTextbookId) {
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const task = await apiClient.parseTextbook(selectedTextbookId);
      setCurrentTask(task);
      await refreshTextbooks();
      await selectTextbook(selectedTextbookId);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to parse textbook");
    } finally {
      setIsLoading(false);
    }
  }, [refreshTextbooks, selectTextbook, selectedTextbookId]);

  const refreshGraph = useCallback(async () => {
    try {
      if (graphViewMode === "merged") {
        const data = await apiClient.getMergedGraph();
        if (!data) { setGraphNodes([]); setGraphEdges([]); return; }
        setGraphNodes(data.nodes);
        setGraphEdges(data.edges);
      } else {
        // Load ALL textbooks' graphs for cross-textbook frequency
        const parsed = textbooks.filter((t) => t.parse_status === "parsed");
        const allNodes: GraphNode[] = [];
        const allEdges: GraphEdge[] = [];
        for (const tb of parsed) {
          try {
            const data = await apiClient.getGraph(tb.textbook_id);
            allNodes.push(...data.nodes);
            allEdges.push(...data.edges);
          } catch { /* textbook may not have a graph yet */ }
        }
        setGraphNodes(allNodes);
        setGraphEdges(allEdges);
      }
    } catch {
      setGraphNodes([]);
      setGraphEdges([]);
    }
  }, [graphViewMode, textbooks]);

  const setGraphViewMode = useCallback(async (mode: "single" | "merged") => {
    setGraphViewModeState(mode);
    if (mode === "merged") {
      try {
        const data = await apiClient.getMergedGraph();
        setGraphNodes(data.nodes);
        setGraphEdges(data.edges);
      } catch { setGraphNodes([]); setGraphEdges([]); }
    } else {
      const parsed = textbooks.filter((t) => t.parse_status === "parsed");
      const allNodes: GraphNode[] = [];
      const allEdges: GraphEdge[] = [];
      for (const tb of parsed) {
        try {
          const data = await apiClient.getGraph(tb.textbook_id);
          allNodes.push(...data.nodes);
          allEdges.push(...data.edges);
        } catch { /* ignore */ }
      }
      setGraphNodes(allNodes);
      setGraphEdges(allEdges);
    }
  }, [selectedTextbookId]);

  const refreshIntegration = useCallback(async () => {
    try {
      const [decisionResponse, stats] = await Promise.all([
        apiClient.listIntegrationDecisions(),
        apiClient.getIntegrationStats()
      ]);
      setDecisions(decisionResponse.decisions);
      setIntegrationStats(stats);
    } catch {
      setDecisions([]);
      setIntegrationStats(null);
    }
  }, []);

  const buildGraph = useCallback(async () => {
    if (!selectedTextbookId) {
      setErrorMessage("Please select a textbook first.");
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await apiClient.buildGraph(selectedTextbookId);
      setCurrentTask({ task_id: result.task_id, task_type: "graph_extraction", status: result.status as Task["status"], progress: 100 });
      if (result.status === "failed") {
        setErrorMessage("Graph extraction failed. Make sure OPENAI_API_KEY and LLM_MODEL are configured in .env.");
      }
      await refreshGraph();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to build graph");
    } finally {
      setIsLoading(false);
    }
  }, [refreshGraph, selectedTextbookId]);

  const runIntegration = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await apiClient.runIntegration();
      setCurrentTask({
        task_id: result.task_id,
        task_type: "integration",
        status: result.status as Task["status"],
        progress: 100
      });
      setIntegrationStats(result);
      await refreshIntegration();
      if (graphViewMode === "merged") {
        await refreshGraph();
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run integration");
    } finally {
      setIsLoading(false);
    }
  }, [graphViewMode, refreshGraph, refreshIntegration]);

  const buildRagIndex = useCallback(async () => {
    if (!selectedTextbookId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await apiClient.buildRagIndex(selectedTextbookId);
      setRagStatus({ indexed_chunks: result.chunk_count, is_loaded: true });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to build RAG index");
    } finally {
      setIsLoading(false);
    }
  }, [selectedTextbookId]);

  const askRag = useCallback(async (question: string) => {
    if (!question.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setRagAnswer(await apiClient.queryRag(question.trim()));
      setRagStatus(await apiClient.getRagStatus());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to query RAG");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendFeedback = useCallback(async (message: string, decisionId?: string | null) => {
    if (!message.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    const userMessage: ChatMessage = { role: "user", content: message.trim(), session_id: chatSessionId ?? undefined };
    setChatMessages((current) => [...current, userMessage]);
    try {
      const response = await apiClient.sendChatMessage(message.trim(), chatSessionId, decisionId);
      setChatSessionId(response.session_id);
      setChatMessages((current) => [
        ...current,
        {
          message_id: response.message_id,
          session_id: response.session_id,
          role: response.role,
          content: response.content
        }
      ]);
      await refreshIntegration();
      await refreshGraph();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to send feedback");
    } finally {
      setIsLoading(false);
    }
  }, [chatSessionId, refreshGraph, refreshIntegration]);

  const refreshReport = useCallback(async () => {
    try {
      setReport(await apiClient.getReport());
    } catch {
      setReport({ status: "not_generated", content: null });
    }
  }, []);

  const generateReport = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      await apiClient.generateReport();
      await refreshReport();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate report");
    } finally {
      setIsLoading(false);
    }
  }, [refreshReport]);

  const selectTextbookAndGraph = useCallback(async (textbookId: string) => {
      await selectTextbook(textbookId);
      if (graphViewMode === "single") {
        try {
          const data = await apiClient.getGraph(textbookId);
          setGraphNodes(data.nodes);
          setGraphEdges(data.edges);
        } catch {
          setGraphNodes([]);
          setGraphEdges([]);
        }
      }
  }, [graphViewMode, selectTextbook]);

  useEffect(() => {
    void refreshTextbooks();
  }, [refreshTextbooks]);

  useEffect(() => {
    void refreshIntegration();
    void apiClient.getRagStatus().then(setRagStatus).catch(() => undefined);
    void refreshReport();
  }, [refreshIntegration, refreshReport]);

  const resetData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      await apiClient.resetAllData();
      setTextbooks([]);
      setChapters([]);
      setGraphNodes([]);
      setGraphEdges([]);
      setDecisions([]);
      setIntegrationStats(null);
      setRagAnswer(null);
      setRagStatus({ indexed_chunks: 0, is_loaded: false });
      setChatMessages([]);
      setChatSessionId(null);
      setReport({ status: "not_generated", content: null });
      setSelectedTextbookId(null);
      setCurrentTask(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to reset data");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const summary = useMemo(
    () => ({
      textbookCount: textbooks.length,
      nodeCount: graphNodes.length,
      edgeCount: graphEdges.length,
      chunkCount: ragStatus.indexed_chunks,
      compressionRatio: integrationStats?.compression_ratio ?? null
    }),
    [textbooks.length, graphNodes.length, graphEdges.length, ragStatus.indexed_chunks, integrationStats?.compression_ratio]
  );

  return {
    textbooks,
    chapters,
    graphNodes,
    graphEdges,
    decisions,
    integrationStats,
    chunks: ragAnswer?.citations.map((citation, index) => ({
      chunk_id: citation.chunk_id,
      textbook_id: citation.textbook_id ?? citation.textbook ?? "",
      chapter_id: citation.chapter_id ?? citation.chapter,
      chunk_index: index,
      text: citation.text ?? "",
      page_start: citation.page,
      page_end: citation.page
    })) ?? [],
    ragAnswer,
    ragStatus,
    chatMessages,
    chatSessionId,
    report,
    currentTask,
    selectedTextbookId,
    graphViewMode,
    isLoading,
    errorMessage,
    summary,
    refreshTextbooks,
    selectTextbook: selectTextbookAndGraph,
    uploadTextbooks,
    parseSelectedTextbook,
    buildGraph,
    refreshGraph,
    setGraphViewMode,
    runIntegration,
    refreshIntegration,
    buildRagIndex,
    askRag,
    sendFeedback,
    generateReport,
    refreshReport,
    resetData
  };
}
