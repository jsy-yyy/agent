import type { DashboardState } from "../hooks/useDashboardState";

interface StatusBarProps {
  state: DashboardState;
}

export function StatusBar({ state }: StatusBarProps) {
  const compression =
    state.summary.compressionRatio === null
      ? "N/A"
      : `${Math.round(state.summary.compressionRatio * 100)}%`;

  return (
    <header className="status-bar">
      <strong>Knowledge Integration Agent</strong>
      <span>{state.summary.textbookCount} textbooks</span>
      <span>{state.summary.nodeCount} nodes</span>
      <span>{state.summary.chunkCount} chunks</span>
      <span>{compression} compression</span>
      <span>{state.currentTask?.status ?? "idle"}</span>
      <button
        type="button"
        className="reset-btn"
        onClick={() => { if (confirm("Clear all uploaded textbooks, parsed data, graphs, and indexes?")) void state.resetData(); }}
        title="Reset all data"
      >
        Reset
      </button>
    </header>
  );
}
