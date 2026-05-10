import { Panel } from "../../components/Panel";
import type { Chapter, Textbook } from "../../types/domain";

interface TextbookPanelProps {
  textbooks: Textbook[];
  chapters: Chapter[];
  selectedTextbookId: string | null;
  isLoading: boolean;
  errorMessage: string | null;
  onUpload: (files: File[]) => Promise<void>;
  onSelectTextbook: (textbookId: string) => Promise<void>;
  onParseSelected: () => Promise<void>;
}

export function TextbookPanel({
  textbooks,
  chapters,
  selectedTextbookId,
  isLoading,
  errorMessage,
  onUpload,
  onSelectTextbook,
  onParseSelected
}: TextbookPanelProps) {
  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    void onUpload(Array.from(event.currentTarget.files ?? []));
    event.currentTarget.value = "";
  };

  const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    void onUpload(Array.from(event.dataTransfer.files));
  };

  return (
    <Panel title="Textbooks">
      <label
        className="upload-surface"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          aria-label="Upload textbooks"
          multiple
          onChange={handleFileInput}
          type="file"
          accept=".pdf,.md,.markdown,.txt"
        />
        <span>PDF</span>
        <span>MD</span>
        <span>TXT</span>
      </label>
      <button
        className="primary-action"
        type="button"
        onClick={() => void onParseSelected()}
        disabled={!selectedTextbookId || isLoading}
      >
        Parse
      </button>
      {errorMessage ? <p className="error-text">{errorMessage}</p> : null}
      <div className="list-block">
        {textbooks.length === 0 ? (
          <p className="muted">No textbooks</p>
        ) : (
          textbooks.map((textbook) => (
            <button
              className="row row-button"
              key={textbook.textbook_id}
              type="button"
              aria-pressed={textbook.textbook_id === selectedTextbookId}
              onClick={() => void onSelectTextbook(textbook.textbook_id)}
            >
              <strong>{textbook.title}</strong>
              <span>{textbook.parse_status}</span>
            </button>
          ))
        )}
      </div>
      <div className="chapter-list">
        {chapters.length === 0 ? (
          <p className="muted">No chapters</p>
        ) : (
          chapters.map((chapter) => (
            <div className="chapter-card" key={chapter.chapter_id}>
              <div className="chapter-header">
                <strong>{chapter.title}</strong>
                <span className="chapter-pages">
                  pp. {chapter.page_start ?? "?"} – {chapter.page_end ?? "?"}
                </span>
              </div>
              <div className="chapter-meta">
                <span>{chapter.char_count.toLocaleString()} chars</span>
              </div>
              <p className="chapter-preview">{chapter.content.slice(0, 200)}</p>
            </div>
          ))
        )}
      </div>
    </Panel>
  );
}
