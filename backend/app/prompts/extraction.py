# Knowledge extraction prompts with few-shot examples

EXTRACT_KNOWLEDGE_NODES = """你是一位学科知识专家，正在分析一本教材的章节内容。请从以下章节中提取核心知识点。

## 输出格式
返回一个 JSON 对象，包含 "nodes" 数组。每个节点必须包含以下字段：
- id: 知识点编号，格式为 "node_001", "node_002" ...
- name: 知识点简明名称
- definition: 1-2 句清晰的定义
- category: 分类，可选值："核心概念"、"方法技能"、"事实知识"、"原理论证"
- page: 知识点所在页码（如果能从内容中推断）

## Few-shot 示例

输入章节内容：
"第二章 细胞的基本功能
细胞膜由磷脂双分子层构成，具有选择透过性...
动作电位是指细胞受到刺激后，膜电位发生的一次快速而可逆的倒转..."

输出：
```json
{{
  "nodes": [
    {{
      "id": "node_001",
      "name": "动作电位",
      "definition": "细胞受到刺激后，膜电位发生的一次快速而可逆的倒转，是细胞兴奋性的标志。",
      "category": "核心概念",
      "page": 35
    }},
    {{
      "id": "node_002",
      "name": "静息电位",
      "definition": "细胞在未受刺激时，膜内外两侧存在的电位差，通常为-70mV左右。",
      "category": "核心概念",
      "page": 32
    }}
  ]
}}
```

## 规则
- 每章最多提取 10 个知识点
- 只提取有教学价值的概念，跳过引言性质的描述
- 名称尽量使用中文
- 分类务必准确

## 章节内容
{chapter_content}

请只返回 JSON，不要输出其他内容。"""


EXTRACT_KNOWLEDGE_RELATIONS = """你是一位学科知识专家。以下是已从某章节提取的知识点列表和章节原文。请识别这些知识点之间的关系。

## 关系类型（至少使用三种）
| 关系类型 | 说明 | 示例 |
|---------|------|------|
| prerequisite | 学习 B 之前必须先掌握 A | "动作电位" 依赖 "静息电位" |
| parallel | 同一层级的平行概念 | "有丝分裂" 与 "减数分裂" |
| contains | 上位概念包含下位概念 | "免疫系统" 包含 "T细胞" |
| applies_to | 某知识点是另一个的应用场景 | "抗体" 应用于 "体液免疫" |

## 输出格式
返回 JSON 对象，包含 "edges" 数组。每条边包含：
- source: 源知识点的 id（使用下面给出的 id）
- target: 目标知识点的 id
- relation_type: 关系类型
- description: 用中文简要描述两者关系

## Few-shot 示例

已知知识点：
[
  {{"id": "node_001", "name": "动作电位", "definition": "..."}},
  {{"id": "node_002", "name": "静息电位", "definition": "..."}}
]

输出：
```json
{{
  "edges": [
    {{
      "source": "node_001",
      "target": "node_002",
      "relation_type": "prerequisite",
      "description": "理解动作电位需要先掌握静息电位的概念"
    }}
  ]
}}
```

## 已知知识点
{nodes_json}

## 章节内容
{chapter_content}

请只返回 JSON，不要输出其他内容。"""
