import { Panel } from "../../components/Panel";
import type { ReportState } from "../../types/domain";

interface ReportPanelProps {
  report: ReportState;
  isLoading: boolean;
  onGenerate: () => Promise<void>;
}

export function ReportPanel({ report, isLoading, onGenerate }: ReportPanelProps) {
  return (
    <Panel title="Report">
      <button type="button" onClick={() => void onGenerate()} disabled={isLoading}>
        Generate Report
      </button>
      <div className="report-preview">
        {report.content ? (
          <pre>{report.content}</pre>
        ) : (
          <span>{report.status === "not_generated" ? "No report generated yet." : report.status}</span>
        )}
      </div>
    </Panel>
  );
}
