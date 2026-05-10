import { useState } from "react";

import { Panel } from "../../components/Panel";
import type { RagAnswer } from "../../types/domain";

interface RagPanelProps {
  indexedChunks: number;
  isIndexed: boolean;
  answer: RagAnswer | null;
  isLoading: boolean;
  hasTextbook: boolean;
  onBuildIndex: () => Promise<void>;
  onAsk: (question: string) => Promise<void>;
}

export function RagPanel({
  indexedChunks,
  isIndexed,
  answer,
  isLoading,
  hasTextbook,
  onBuildIndex,
  onAsk
}: RagPanelProps) {
  const [question, setQuestion] = useState("");

  return (
    <Panel title="RAG">
      <div className="row">
        <span>Index status</span>
        <strong>{isIndexed ? "Ready" : "Not built"}</strong>
      </div>
      <div className="row">
        <span>Indexed chunks</span>
        <strong>{indexedChunks}</strong>
      </div>
      <button type="button" onClick={() => void onBuildIndex()} disabled={!hasTextbook || isLoading}>
        Build Index
      </button>
      <textarea
        aria-label="Question"
        rows={4}
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask a question grounded in indexed textbooks"
      />
      <button type="button" onClick={() => void onAsk(question)} disabled={!question.trim() || !isIndexed || isLoading}>
        Ask
      </button>
      {answer && (
        <div className="rag-answer">
          <h4>Answer</h4>
          <p>{answer.answer}</p>
          <h4>Citations</h4>
          {answer.citations.length === 0 ? (
            <p className="muted">No citations returned.</p>
          ) : (
            answer.citations.map((citation) => (
              <details key={citation.chunk_id} className="citation-card">
                <summary>
                  {citation.textbook ?? citation.textbook_id}, {citation.chapter ?? citation.chapter_id ?? "chapter"}, page {citation.page ?? "?"} · {Math.round(citation.relevance_score * 100)}%
                </summary>
                <p>{citation.text ?? "No preview text returned."}</p>
              </details>
            ))
          )}
        </div>
      )}
    </Panel>
  );
}
