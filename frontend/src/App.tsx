import { StatusBar } from "./components/StatusBar";
import { ChatPanel } from "./features/chat/ChatPanel";
import { GraphWorkspace } from "./features/graph/GraphWorkspace";
import { IntegrationPanel } from "./features/integration/IntegrationPanel";
import { RagPanel } from "./features/rag/RagPanel";
import { ReportPanel } from "./features/report/ReportPanel";
import { TextbookPanel } from "./features/textbooks/TextbookPanel";
import { useDashboardState } from "./hooks/useDashboardState";

export function App() {
  const state = useDashboardState();

  return (
    <div className="app-shell">
      <StatusBar state={state} />
      <div className="workspace-grid">
        <aside className="left-rail">
          <TextbookPanel
            textbooks={state.textbooks}
            chapters={state.chapters}
            selectedTextbookId={state.selectedTextbookId}
            isLoading={state.isLoading}
            errorMessage={state.errorMessage}
            onUpload={state.uploadTextbooks}
            onSelectTextbook={state.selectTextbook}
            onParseSelected={state.parseSelectedTextbook}
          />
        </aside>
        <GraphWorkspace
          nodes={state.graphNodes}
          edges={state.graphEdges}
          textbooks={state.textbooks}
          chapters={state.chapters}
          hasTextbook={state.selectedTextbookId !== null}
          onBuildGraph={state.buildGraph}
        />
        <aside className="right-rail">
          <IntegrationPanel
            decisions={state.decisions}
            stats={state.integrationStats}
            isLoading={state.isLoading}
            onRunIntegration={state.runIntegration}
          />
          <RagPanel
            indexedChunks={state.ragStatus.indexed_chunks}
            isIndexed={state.ragStatus.is_loaded}
            answer={state.ragAnswer}
            isLoading={state.isLoading}
            hasTextbook={state.selectedTextbookId !== null}
            onBuildIndex={state.buildRagIndex}
            onAsk={state.askRag}
          />
          <ChatPanel
            messages={state.chatMessages}
            decisions={state.decisions}
            isLoading={state.isLoading}
            onSend={state.sendFeedback}
          />
          <ReportPanel
            report={state.report}
            isLoading={state.isLoading}
            onGenerate={state.generateReport}
          />
        </aside>
      </div>
    </div>
  );
}
