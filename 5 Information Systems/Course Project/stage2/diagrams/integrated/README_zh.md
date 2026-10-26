# 两张完整总图

本目录包含当前两张完整总图，精炼版报告已采用它们。早期分图仅供历史参考，当前提交以总图为准。

| 图 | 内容 | 文件 |
|---|---|---|
| ER 总图 | 10 个概念实体、19 条关系；美容师与沙龙服务直接用 M:N 表示 | `er_model.svg`、`er_model.png`、`er_model.drawio` |
| 数据逻辑模型总图 | 14 张 PostgreSQL 表、全部 25 个外键；包含字段类型、主键、外键标号、可空性、唯一性和主要约束 | `logical_model.svg`、`logical_model.png`、`logical_model.drawio` |

每张图中的每个实体或表只出现一次。主体关系线全部由水平和垂直线段组成。ER 图有 3 处交叉，数据逻辑图有 2 处交叉，均使用跨线桥表示，跨越的两条线互不连接。

实体框按各自字段文字实际定宽、按字段和约束行数定高，不再使用统一的大框。ER 字段维持 22px、逻辑模型字段维持 20px；压缩留白时没有缩小字号。逻辑模型的评价表放在预约表右侧，以缩短整张图。

数据逻辑图左侧独立键列使用加粗的 PK、FK 和 UQ；右侧字段名保持常规字重，数据类型加粗。NN / NULL 表示可空性，G 表示计算列；F01–F25 与外键连线一致。图底部的说明已经删除，符号说明置于报告正文中。

ER 图不把“美容师—服务”画为独立业务实体框：这是一条带 `is_active` 属性的 M:N 关系。在关系模型中，该关系由 `master_service` 中间表实现。因此，ER 图的 10 个业务实体、M:N 关系、两项照片多值属性和邀请技术关系，最终仍对应现有的 14 张物理表；没有改动数据库结构。

照片在 ER 图中仍为沙龙或美容师的复合多值属性。数据逻辑模型将其分别展开为 `salon_photo`、`master_photo`，邀请使用 `master_invitation`。评价的作者及具体美容师、沙龙仍通过预约推导。审核的四种目标遵守 XOR。

查看高清 PNG 可直接预览；放大或排版建议使用 SVG；`.drawio` 文件可在 diagrams.net 中继续编辑。`*_preview.png` 是缩小预览。

`geometry_checks.json` 保存实体唯一性、关系完整性、交叉位置及独立绘图操作未改写报告的 SHA-256 快照。`er_layout.json`、`logical_layout.json` 保存最终位置和正交路径。

重新生成图件：

```powershell
python .\stage2\scripts\draw_integrated_models.py
```

生成工具需要 Pillow、reportlab 和 Windows Arial 字体。原始布局在 `stage2/scripts/diagram_layouts/`；独立绘图命令不改写报告正文或 SQL，只生成图件及供报告排版使用的矢量 PDF。
