from app.schemas.graph import (
    BuildGraphRequest,
    BuildGraphResponse,
    GraphDataResponse,
    GraphEdgeResponse,
    GraphNodeRequest,
    GraphNodeResponse,
    GraphSearchRequest,
    GraphSearchResponse,
    VALID_RELATION_TYPES,
)


class TestGraphNodeContract:
    def test_node_request_has_required_fields(self) -> None:
        node = GraphNodeRequest(
            name="动作电位",
            definition="细胞受到刺激后膜电位发生的一次快速而可逆的倒转",
            category="核心概念",
            page=35,
            source_excerpt="当细胞受到足够强度的刺激时...",
        )
        assert node.name == "动作电位"
        assert node.definition is not None
        assert node.category == "核心概念"
        assert node.page == 35
        assert node.source_excerpt is not None

    def test_node_request_page_is_optional(self) -> None:
        node = GraphNodeRequest(
            name="概念",
            definition="定义",
            category="事实知识",
            source_excerpt="原文...",
        )
        assert node.page is None

    def test_node_response_includes_id_and_provenance(self) -> None:
        node = GraphNodeResponse(
            node_id="n1",
            textbook_id="tb1",
            chapter_id="ch1",
            name="动作电位",
            definition="定义",
            category="核心概念",
            page=35,
            source_excerpt="原文",
            frequency=2,
        )
        assert node.node_id == "n1"
        assert node.textbook_id == "tb1"
        assert node.chapter_id == "ch1"
        assert node.frequency == 2


class TestGraphEdgeContract:
    def test_edge_response_has_required_fields(self) -> None:
        edge = GraphEdgeResponse(
            edge_id="e1",
            textbook_id="tb1",
            source_node_id="n1",
            target_node_id="n2",
            relation_type="prerequisite",
            description="理解动作电位需要先掌握静息电位",
        )
        assert edge.edge_id == "e1"
        assert edge.relation_type == "prerequisite"
        assert edge.source_node_id != edge.target_node_id

    def test_valid_relation_types(self) -> None:
        assert "prerequisite" in VALID_RELATION_TYPES
        assert "parallel" in VALID_RELATION_TYPES
        assert "contains" in VALID_RELATION_TYPES
        assert "applies_to" in VALID_RELATION_TYPES
        assert len(VALID_RELATION_TYPES) >= 3


class TestGraphApiSchemas:
    def test_graph_data_response_wraps_nodes_and_edges(self) -> None:
        data = GraphDataResponse(
            textbook_id="tb1",
            nodes=[
                GraphNodeResponse(
                    node_id="n1", textbook_id="tb1", name="概念A",
                    definition="定义A", category="核心概念", source_excerpt="原文A",
                )
            ],
            edges=[
                GraphEdgeResponse(
                    edge_id="e1", textbook_id="tb1", source_node_id="n1",
                    target_node_id="n2", relation_type="parallel", description="相关",
                )
            ],
        )
        assert len(data.nodes) == 1
        assert len(data.edges) == 1
        assert data.textbook_id == "tb1"

    def test_build_graph_request(self) -> None:
        req = BuildGraphRequest(textbook_id="tb1")
        assert req.textbook_id == "tb1"

    def test_build_graph_response(self) -> None:
        resp = BuildGraphResponse(textbook_id="tb1", task_id="t1", status="pending")
        assert resp.task_id == "t1"
        assert resp.status == "pending"

    def test_graph_search_request(self) -> None:
        req = GraphSearchRequest(textbook_id="tb1", query="电位", limit=10)
        assert req.query == "电位"
        assert req.limit == 10

    def test_graph_search_response(self) -> None:
        resp = GraphSearchResponse(query="电位", matched_nodes=[], total_matches=0)
        assert resp.query == "电位"
        assert resp.total_matches == 0
