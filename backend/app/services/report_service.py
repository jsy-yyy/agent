from pathlib import Path

from app.core.config import get_settings
from app.services.integration_projection import integration_projection_service
from app.services.integration_service import integration_service
from app.services.textbook_service import textbook_service


class ReportService:
    def generate(self) -> Path:
        stats = integration_projection_service.build_stats()
        textbooks = [t for t in textbook_service.list_textbooks() if t.parse_status == "parsed"]
        decisions = [d for d in integration_service.list_decisions() if d.status == "active"]
        ratio = (
            f"{stats.compression_ratio:.2%}"
            if stats.compression_ratio is not None
            else "N/A"
        )

        report_lines = [
            "# 学科知识整合报告",
            "",
            "## 整合概览",
            f"- 教材数量: {len(textbooks)}",
            f"- 教材列表: {', '.join(t.title for t in textbooks) or '无'}",
            f"- 原始字符数: {stats.total_source_chars}",
            f"- 整合后字符数: {stats.integrated_chars}",
            f"- 压缩目标字符数: {stats.target_chars}",
            f"- 压缩比: {ratio}",
            f"- 是否满足 30% 压缩目标: {'是' if stats.target_met else '否'}",
            f"- 整合决策总数: {stats.total_decisions}",
            f"- 合并: {stats.merge_count}, 保留: {stats.keep_count}, 移除: {stats.remove_count}",
            "",
            "## 图谱统计",
            f"- 原始图谱节点数: {stats.source_node_count}",
            f"- 原始图谱边数: {stats.source_edge_count}",
            f"- 整合后图谱节点数: {stats.integrated_node_count}",
            f"- 整合后图谱边数: {stats.integrated_edge_count}",
            "",
            "## 决策摘要",
        ]

        if decisions:
            for decision in decisions:
                nodes = ", ".join(decision.affected_node_ids)
                report_lines.append(
                    f"- **{decision.action}** `{decision.decision_id}` "
                    f"[{nodes}]: {decision.reason} (置信度: {decision.confidence:.0%})"
                )
        else:
            report_lines.append("- 暂无整合决策。")

        report_lines.extend([
            "",
            "## 教学完整性说明",
            "整合过程优先保留跨教材共享概念、核心概念和前置依赖相关节点；低优先级内容会在超出 30% 预算时生成 remove 决策。",
        ])

        report_dir = Path(get_settings().data_dir) / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "整合报告.md"
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        return report_path

    def read(self) -> str | None:
        report_path = Path(get_settings().data_dir) / "reports" / "整合报告.md"
        if report_path.exists():
            return report_path.read_text(encoding="utf-8")
        return None


report_service = ReportService()
