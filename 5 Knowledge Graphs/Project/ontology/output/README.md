# 本体实验输出导航

本目录按用途分类。全量版的逐步操作见 [全量版实验完整教程](../FULL_VERSION_TUTORIAL_ZH.md)。

| 目录 | 内容 | 文件数 |
| --- | --- | --- |
| [ontologies](ontologies/) | OWL 本体和 Turtle 数据；包含实验版、全量版及推理结果 | 9 |
| [results](results/) | 查询匹配、解释路径、逆关系和效果证据 CSV | 8 |
| [visualizations/reactodia](visualizations/reactodia/) | 三个英雄的图形布局和 Lux 的 SVG 关系图 | 4 |
| [visualizations/webvowl](visualizations/webvowl/) | WebVOWL 模型与布局 JSON、两张结构图 SVG | 3 |
| [verification](verification/) | 构建统计、查询核验、HermiT 日志及可移植构建记录 | 5 |

## 按操作选择文件

- **使用全量版完成本阶段演示**：查看 [完整教程](../FULL_VERSION_TUTORIAL_ZH.md)，打开 [lol_full.owl](ontologies/lol_full.owl)；Reactodia 加载 [全量推理 Turtle](ontologies/lol_full_inferred.ttl)。

- **在 Protégé 中开始实验**：打开 [lol_demo.owl](ontologies/lol_demo.owl)，然后启动 HermiT。
- **复制 DL Query 表达式**：查看 [DL 查询与预期结果](../queries/DL_queries.txt)。
- **查看已有推理结果**：打开 [lol_demo_inferred.owl](ontologies/lol_demo_inferred.owl)。
- **在 Reactodia 中恢复图形**：先载入 [推理结果 Turtle](ontologies/lol_demo_inferred.ttl)，再载入 [Lux 布局](visualizations/reactodia/lux_relations.reactodia.json)；也可选择 [Karma 布局](visualizations/reactodia/karma_relations.reactodia.json) 或 [Morgana 布局](visualizations/reactodia/morgana_relations.reactodia.json)。
- **在 WebVOWL 中恢复结构图**：载入 [WebVOWL JSON](visualizations/webvowl/lol_demo.webvowl.json)。
- **直接看图**：[Lux 关系图](visualizations/reactodia/lux_relations.svg)、[全部命名类结构图](visualizations/webvowl/lol_schema_webvowl_full.svg)、[简化结构图](visualizations/webvowl/lol_schema_webvowl.svg)。
- **解释查询结果**：查看 [demo_query_explanations.csv](results/demo_query_explanations.csv)，包含三个英雄的七条解释路径。
- **检查逻辑验证记录**：查看 [HermiT 实验版日志](verification/hermit_demo_verification.txt) 和 [查询核验摘要](verification/query_validation.json)。

## 文件名与数据范围

- `demo`：Lux、Karma、Morgana，共 15 条主要技能、66 个个体。
- `full`：173 个英雄、865 条主要技能；机制标注仍仅覆盖上述三个英雄。
- `inferred`：包含 HermiT 推理导出的新增事实。
- `schema`：类、属性及逻辑定义。
- `.owl` 与对应 `.ttl` 是相同版本知识图谱的不同序列化格式。
- Reactodia JSON 只保存图形视图，需要配合 Turtle 数据加载。

重新构建、导出与生成图形的方法见 [项目使用说明](../README.md)。脚本已使用本目录的新路径。
