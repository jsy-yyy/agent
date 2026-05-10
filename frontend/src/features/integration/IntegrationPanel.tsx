import { Panel } from "../../components/Panel";
import type { IntegrationDecision, IntegrationStats } from "../../types/domain";

interface IntegrationPanelProps {
  decisions: IntegrationDecision[];
  stats: IntegrationStats | null;
  isLoading: boolean;
  onRunIntegration: () => Promise<void>;
}

export function IntegrationPanel({ decisions, stats, isLoading, onRunIntegration }: IntegrationPanelProps) {
  const compression =
    stats?.compression_ratio === null || stats?.compression_ratio === undefined
      ? "N/A"
      : `${Math.round(stats.compression_ratio * 100)}%`;

  return (
    <Panel title="Integration">
      <div className="metric-grid">
        <span>Merge</span>
        <strong>{stats?.merge_count ?? decisions.filter((item) => item.action === "merge").length}</strong>
        <span>Keep</span>
        <strong>{stats?.keep_count ?? decisions.filter((item) => item.action === "keep").length}</strong>
        <span>Remove</span>
        <strong>{stats?.remove_count ?? decisions.filter((item) => item.action === "remove").length}</strong>
        <span>Compression</span>
        <strong>{compression}</strong>
      </div>
      <button type="button" onClick={() => void onRunIntegration()} disabled={isLoading}>
        Run Integration
      </button>
      <div className="decision-list">
        {decisions.length === 0 ? (
          <p className="muted">No integration decisions yet.</p>
        ) : (
          decisions.map((decision) => (
            <article key={decision.decision_id} className="decision-card">
              <div className="row">
                <strong>{decision.action}</strong>
                <span>{decision.status}</span>
              </div>
              <code>{decision.decision_id}</code>
              <p>{decision.reason}</p>
              <small>
                {decision.affected_node_ids.length} nodes · {Math.round(decision.confidence * 100)}%
              </small>
            </article>
          ))
        )}
      </div>
    </Panel>
  );
}
