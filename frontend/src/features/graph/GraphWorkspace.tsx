import { useEffect, useRef, useState } from "react";
import cytoscape, { type Core, type EventObject } from "cytoscape";
import type { Chapter, GraphEdge, GraphNode, Textbook } from "../../types/domain";

interface GraphWorkspaceProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  textbooks: Textbook[];
  chapters: Chapter[];
  onBuildGraph?: () => void;
  hasTextbook?: boolean;
}

const TEXTBOOK_COLORS = [
  "#4A90D9", "#E8734A", "#50B86C", "#B07CD8",
  "#D9B84A", "#4AD9C8", "#D94A8B", "#8BD94A",
];

function getTextbookColor(textbookId: string): string {
  let hash = 0;
  for (let i = 0; i < textbookId.length; i++) {
    hash = textbookId.charCodeAt(i) + ((hash << 5) - hash);
  }
  return TEXTBOOK_COLORS[Math.abs(hash) % TEXTBOOK_COLORS.length];
}

interface NodeDetail {
  name: string;
  definition: string;
  category: string;
  textbookId: string;
  textbookTitle: string;
  chapterId: string | null | undefined;
  chapterTitle: string;
  page: number | null | undefined;
  sourceExcerpt: string;
}

function getTextbookTitle(textbooks: Textbook[], id: string): string {
  const tb = textbooks.find((t) => t.textbook_id === id);
  return tb?.title ?? id;
}

function getChapterTitle(chapters: Chapter[], id: string | null | undefined): string {
  if (!id) {
    return "Unknown chapter";
  }
  const chapter = chapters.find((item) => item.chapter_id === id);
  return chapter?.title ?? id;
}

export function GraphWorkspace({
  nodes,
  edges,
  textbooks,
  chapters,
  onBuildGraph,
  hasTextbook,
}: GraphWorkspaceProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const textbooksRef = useRef(textbooks);
  const chaptersRef = useRef(chapters);
  const [selectedNode, setSelectedNode] = useState<NodeDetail | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [viewMode, setViewMode] = useState<"single" | "merged">("single");

  useEffect(() => {
    textbooksRef.current = textbooks;
  }, [textbooks]);

  useEffect(() => {
    chaptersRef.current = chapters;
  }, [chapters]);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            label: "data(label)",
            "text-valign": "bottom",
            "text-halign": "center",
            "font-size": "10px",
            color: "#333",
            "text-wrap": "wrap",
            "text-max-width": "120px",
            width: "data(size)",
            height: "data(size)",
          },
        },
        {
          selector: "node.highlighted",
          style: {
            "border-width": 3,
            "border-color": "#FFD700",
          },
        },
        {
          selector: "node.dimmed",
          style: {
            opacity: 0.2,
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#999",
            "target-arrow-color": "#999",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": "8px",
            color: "#666",
          },
        },
        {
          selector: "edge.highlighted",
          style: {
            width: 3,
            "line-color": "#FFD700",
            "target-arrow-color": "#FFD700",
          },
        },
        {
          selector: "edge.dimmed",
          style: {
            opacity: 0.1,
          },
        },
      ],
      layout: {
        name: "cose",
        animate: false,
        nodeRepulsion: () => 4000,
        idealEdgeLength: () => 100,
      },
      wheelSensitivity: 0.3,
    });

    cy.on("tap", "node", (evt: EventObject) => {
      const node = evt.target;
      const tbId = node.data("textbookId") ?? "";
      const chapterId = node.data("chapterId");
      setSelectedNode({
        name: node.data("name") ?? "",
        definition: node.data("definition") ?? "",
        category: node.data("category") ?? "",
        textbookId: tbId,
        textbookTitle: getTextbookTitle(textbooksRef.current, tbId),
        chapterId,
        chapterTitle: getChapterTitle(chaptersRef.current, chapterId),
        page: node.data("page"),
        sourceExcerpt: node.data("sourceExcerpt") ?? "",
      });
    });

    cy.on("tap", (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    // Count node name frequencies for sizing
    const nameCounts = new Map<string, number>();
    nodes.forEach((n) => {
      nameCounts.set(n.name, (nameCounts.get(n.name) ?? 0) + 1);
    });

    const nodeElements = nodes.map((n) => {
      const freq = nameCounts.get(n.name) ?? 1;
      const size = Math.min(24 + freq * 6, 50);
      return {
        group: "nodes" as const,
        data: {
          id: n.node_id,
          label: n.name,
          name: n.name,
          definition: n.definition,
          category: n.category,
          textbookId: n.textbook_id,
          chapterId: n.chapter_id,
          page: n.page,
          sourceExcerpt: n.source_excerpt,
          color: getTextbookColor(n.textbook_id),
          size,
        },
      };
    });

    const edgeElements = edges.map((e) => ({
      group: "edges" as const,
      data: {
        id: e.edge_id,
        source: e.source_node_id,
        target: e.target_node_id,
        label: e.relation_type,
        relationType: e.relation_type,
        description: e.description,
      },
    }));

    cy.json({ elements: [...nodeElements, ...edgeElements] });
    cy.layout({ name: "cose", animate: true, nodeRepulsion: () => 4000 }).run();
  }, [nodes, edges]);

  function handleSearch() {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("highlighted dimmed");

    if (!searchTerm.trim()) return;

    const matched = cy.nodes().filter((n) =>
      n.data("name").toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (matched.length === 0) return;

    matched.addClass("highlighted");
    matched.connectedEdges().addClass("highlighted");

    cy.nodes().not(matched).addClass("dimmed");
    cy.edges().not(matched.connectedEdges()).addClass("dimmed");
  }

  function handleClearSearch() {
    setSearchTerm("");
    const cy = cyRef.current;
    if (cy) {
      cy.elements().removeClass("highlighted dimmed");
    }
  }

  return (
    <main className="graph-workspace" aria-label="Graph workspace">
      <div className="graph-toolbar">
        <div className="segmented-control" aria-label="Graph view">
          <button
            type="button"
            aria-pressed={viewMode === "single"}
            onClick={() => setViewMode("single")}
          >
            Single
          </button>
          <button
            type="button"
            aria-pressed={viewMode === "merged"}
            onClick={() => setViewMode("merged")}
          >
            Merged
          </button>
        </div>
        <div className="graph-search-group">
          <input
            aria-label="Graph search"
            placeholder="Search concepts"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleSearch(); }}
          />
          <button type="button" onClick={handleSearch} className="search-btn">
            Search
          </button>
          <button type="button" onClick={handleClearSearch} className="clear-btn">
            Clear
          </button>
        </div>
        {hasTextbook && onBuildGraph && (
          <button type="button" onClick={onBuildGraph} className="build-btn">
            Build Graph
          </button>
        )}
      </div>
      <div className="graph-stage">
        <div className="graph-canvas" ref={containerRef} />
        <aside className="node-detail-panel" aria-live="polite">
          {selectedNode ? (
            <>
              <h3>{selectedNode.name}</h3>
              <p className="node-definition">{selectedNode.definition}</p>
              <dl className="node-detail-list">
                <dt>Category</dt>
                <dd>{selectedNode.category}</dd>
                <dt>Textbook</dt>
                <dd>{selectedNode.textbookTitle}</dd>
                <dt>Chapter</dt>
                <dd>{selectedNode.chapterTitle}</dd>
                {selectedNode.page ? (
                  <>
                    <dt>Page</dt>
                    <dd>{selectedNode.page}</dd>
                  </>
                ) : null}
              </dl>
              <div className="node-source-block">
                <h4>Source excerpt</h4>
                <p className="node-excerpt">{selectedNode.sourceExcerpt}</p>
              </div>
            </>
          ) : (
            <div className="node-detail-empty">
              <h3>Node details</h3>
              <p>Select a concept node to inspect its definition, chapter, and source excerpt.</p>
            </div>
          )}
        </aside>
      </div>
      <footer className="graph-footer">
        <span>{nodes.length} nodes</span>
        <span>{edges.length} edges</span>
      </footer>
    </main>
  );
}
