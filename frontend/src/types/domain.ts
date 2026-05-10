export type TaskStatus = "pending" | "running" | "completed" | "failed";

export interface Task {
  task_id: string;
  task_type: string;
  status: TaskStatus;
  progress: number;
  error_message?: string | null;
}

export interface Textbook {
  textbook_id: string;
  filename: string;
  title: string;
  file_format: string;
  file_size: number;
  saved_path: string;
  parse_status: string;
  total_pages: number;
  total_chars: number;
}

export interface Chapter {
  chapter_id: string;
  textbook_id: string;
  title: string;
  order_index: number;
  page_start?: number | null;
  page_end?: number | null;
  content: string;
  char_count: number;
}

export interface GraphNode {
  node_id: string;
  textbook_id: string;
  chapter_id?: string | null;
  name: string;
  definition: string;
  category: string;
  page?: number | null;
  source_excerpt: string;
  frequency?: number;
}

export interface GraphEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  description: string;
}

export interface IntegrationDecision {
  decision_id: string;
  action: "merge" | "keep" | "remove" | string;
  affected_node_ids: string[];
  result_node_id?: string | null;
  reason: string;
  confidence: number;
  status: string;
}

export interface IntegrationStats {
  total_decisions: number;
  merge_count: number;
  keep_count: number;
  remove_count: number;
  total_source_chars?: number;
  integrated_chars?: number;
  compression_ratio?: number | null;
}

export interface RagChunk {
  chunk_id: string;
  textbook_id: string;
  chapter_id?: string | null;
  chunk_index: number;
  text: string;
  page_start?: number | null;
  page_end?: number | null;
}

export interface Citation {
  textbook?: string;
  textbook_id?: string;
  chapter?: string;
  chapter_id?: string | null;
  page?: number | null;
  relevance_score: number;
  chunk_id: string;
  text?: string;
}

export interface RagAnswer {
  answer: string;
  citations: Citation[];
}

export interface ChatMessage {
  message_id?: string;
  session_id?: string;
  role: "user" | "assistant" | string;
  content: string;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  role: string;
  content: string;
  updated_decision_id?: string | null;
}

export interface ReportState {
  status: string;
  content: string | null;
}
