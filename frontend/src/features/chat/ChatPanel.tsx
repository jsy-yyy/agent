import { useState } from "react";

import { Panel } from "../../components/Panel";
import type { ChatMessage, IntegrationDecision } from "../../types/domain";

interface ChatPanelProps {
  messages: ChatMessage[];
  decisions: IntegrationDecision[];
  isLoading: boolean;
  onSend: (message: string, decisionId?: string | null) => Promise<void>;
}

export function ChatPanel({ messages, decisions, isLoading, onSend }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [decisionId, setDecisionId] = useState("");

  async function submit() {
    if (!message.trim()) return;
    await onSend(message, decisionId || null);
    setMessage("");
  }

  return (
    <Panel title="Feedback">
      <div className="message-list">
        {messages.length === 0 ? (
          <p className="muted">No messages</p>
        ) : (
          messages.map((item, index) => (
            <p key={`${item.message_id ?? item.role}-${index}`} className={`chat-message ${item.role}`}>
              <strong>{item.role}</strong>: {item.content}
            </p>
          ))
        )}
      </div>
      <select
        aria-label="Decision to modify"
        value={decisionId}
        onChange={(event) => setDecisionId(event.target.value)}
      >
        <option value="">Auto / only active decision</option>
        {decisions.map((decision) => (
          <option key={decision.decision_id} value={decision.decision_id}>
            {decision.action} · {decision.decision_id}
          </option>
        ))}
      </select>
      <input
        aria-label="Feedback message"
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") void submit();
        }}
        placeholder="例如：请保留这个知识点，或把这两个概念拆分"
      />
      <button type="button" onClick={() => void submit()} disabled={!message.trim() || isLoading}>
        Send Feedback
      </button>
    </Panel>
  );
}
