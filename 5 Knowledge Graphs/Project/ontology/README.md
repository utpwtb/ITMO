# LoL 本体实验：使用与提交说明

本目录对应教材 PDF 第 249–250 页的 `Практическое задание 3_1 / 3_2`。项目主题为英雄、技能及效果机制。输出按本体、查询结果、可视化与验证分类，入口见 [输出目录导航](output/README.md)。三英雄快速演示使用 `output/ontologies/lol_demo.owl`；数据版本为 **Data Dragon 16.20.1 / ru_RU**。

本阶段使用 **`lol_full.owl` 全量版** 的逐步操作、预期结果、中俄讲解词和验收方法，见 [全量版实验完整教程](FULL_VERSION_TUTORIAL_ZH.md)。

## 1. 完成情况

| 教材要求 | 实现与证据 |
| --- | --- |
| 至少 8 个类 | 14 个命名类 |
| 至少 6 个对象属性 | 9 个对象属性 |
| 至少 10 个数据属性 | 18 个数据属性 |
| 填充实例和关系 | 实验版 66 个实例：3 个英雄、15 条技能、28 个效果及机制、目标、来源等 |
| 使用逆关系、传递性等一种或多种关系特性 | 两对逆关系；另有一条属性链。没有给不适合的关系强加传递性 |
| 执行推理，得到新关系 | HermiT 实际验证；15 条技能所属逆关系、28 条效果所属逆关系及英雄机制关系可被推导 |
| 可视化检查 | Reactodia 已导入推理结果并检查 Lux 示例；保存了实例图和原生布局 |
| 导入 VOWL | WebVOWL 已实际导入；界面统计为 14 / 9 / 18 / 66，保存了 SVG、JSON、截图 |
| 使用、注册 Ontodia 原站 | **未完成原站操作**：2026-11-03 内置浏览器访问 `https://ontodia.org` 报 `ERR_CONNECTION_CLOSED`。使用其开源分支 Reactodia 完成实例图检查；这项工具替代是否被课程接受，仍由教师决定 |

`mechanics_annotations.csv` 是按俄语原文逐项整理的 **28 条定性效果标注**，覆盖 Lux、Morgana、Karma 的 15 个主要技能。状态诚实记录为 `reviewed_by_assistant`，未记为已经过本人或教师独立复核。原有 `data/.../mechanics_review.csv` 未改动。

全量版 `lol_full.owl` 导入 **173 个英雄、865 条主要技能**，机制标注仍限于上述三名英雄。它不是全部英雄机制已经标注完成的版本。

## 2. 先打开这些文件

| 文件 | 用途 |
| --- | --- |
| `EXPERIMENT_RU.md`（当前工作目录未保留） | 先前提交包中的俄语实验报告；重新打包前需提供该文件 |
| `output/ontologies/lol_demo.owl` | 在 Protégé 中打开的实验版本体；保留原始断言，适合现场启动推理 |
| `output/ontologies/lol_demo_inferred.owl` | HermiT 物化推理结果，便于查看和使用 SPARQL |
| `output/ontologies/lol_full.owl` | 全量英雄和技能导入版 |
| `output/ontologies/lol_demo_inferred.ttl` | 用于 Reactodia 的 Turtle 格式推理结果 |
| `output/visualizations/webvowl/lol_demo.webvowl.json` | WebVOWL 原生导出文件，含模型、布局和显示设置 |
| `output/visualizations/reactodia/lux_relations.reactodia.json` | Lux 实例图布局；需要先导入 Turtle 数据 |
| `output/visualizations/reactodia/lux_relations.svg` | 从 Reactodia 导出的可缩放实例图 |
| `output/visualizations/webvowl/lol_schema_webvowl_full.svg` | 包含全部命名类的 WebVOWL 结构图；数据属性在图中隐藏以减少拥挤 |
| `output/visualizations/webvowl/lol_schema_webvowl.svg` | 更简略的结构视图，额外隐藏集合运算符及其部分复杂类表示；完整模型以 OWL 为准 |
| `output/results/demo_query_explanations.csv` | 3 名英雄、7 条技能与效果解释路径，附生效条件 |
| `output/verification/hermit_demo_verification.txt` | 实验版推理与反例检查记录 |
| `output/verification/query_validation.json` | 推理前后对照与查询结果检查 |

## 3. 在 Protégé 中演示（约 5 分钟）

1. `File → Open`，打开 `output/ontologies/lol_demo.owl`。如界面已有旧版本，可重新打开该文件。
2. `Active ontology` 查看统计：14 个类、9 个对象属性、18 个数据属性、66 个实例。
3. `Entities` 中查看 `Ability → ActiveAbility / PassiveAbility`，以及 `Mechanic → MovementControlMechanic`。
4. 查看 `hasAbility` 与 `isAbilityOf` 互为逆关系；`hasEffect` 与 `effectOf` 也互为逆关系。
5. `Reasoner → HermiT 1.4.3.456 → Start reasoner`，等待右下角显示 `Reasoner active`。
6. 切换 `DL Query`，只勾选 **Instances**，输入 `SupportControlMage`，点击 `Execute`。结果应为 **Karma、Lux、Morgana**。
7. 输入 `isAbilityOf value Lux`，应得到 Lux 的五个主要技能。这些逆关系在原始 OWL 中没有手工录入。
8. 查看 `Lux_W_Shield_Ally` 的 `conditionText`、`evidenceText` 与 `hasTargetType Ally`。再比较 `Karma_W_Heal_Self`，说明自身治疗与友军效果被分开建模。

其他可复制的 DL 表达式在 `queries/DL_queries.txt`。不要点击 `Add to ontology` 来保存查询结果，查询本身不需要改变本体。

## 4. 重新打开可视化

### WebVOWL

1. 打开 <https://service.tib.eu/webvowl/>。
2. `Ontology` 菜单选择 `output/visualizations/webvowl/lol_demo.webvowl.json`，恢复已保存的模型与布局。也可以选择 `output/ontologies/lol_demo.owl`，通过服务重新转换。
3. 如同名 OWL 更新后仍显示旧图，刷新页面后重新选择文件，或换一个临时文件名。该站会按文件名使用内存缓存。
4. `Statistics` 应显示 **Classes 14 / Object prop. 9 / Datatype prop. 18 / Individuals 66**。图的节点、边数还包含数据类型和逻辑表达式，不等于类、对象属性的数量。

### Reactodia（Ontodia 的开源分支）

1. 打开 <https://reactodia.github.io/playground/rdf-explorer>。
2. 左上角菜单 `Load RDF (Turtle) data`，选择 `output/ontologies/lol_demo_inferred.ttl`。
3. 同一菜单 `Open diagram from file`，选择 `output/visualizations/reactodia/lux_relations.reactodia.json`。
4. 点击 `Fit to Screen`；必要时缩小一级。布局包含 9 个节点、12 条可见关系。长距离的 `canApplyMechanic` 关系仅在该视图中隐藏，仍存在于 RDF 数据中。
5. 可改为载入 `karma_relations.reactodia.json` 或 `morgana_relations.reactodia.json` 查看另两名英雄。对应布局由脚本生成，所示边均已与推理结果逐条核对；实际界面截图和 SVG 以 Lux 图为主。

原生 Reactodia JSON 仅保存视图；不能代替 Turtle / OWL 数据文件。

## 5. 离线重新构建与检查

需要 Python 3.10+。Java 验证脚本使用本机 **JDK 17** 和 **Protégé 5.6.9** 安装目录中的 OWLAPI、HermiT；换机器时修改两个参数。

在本目录打开 PowerShell，按顺序执行：

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe build_ontology.py
.\tools\run_hermit.ps1 -ProtegeDirectory 'C:\develop\Protege-5.6.9' -JdkDirectory 'C:\Program Files\Java\jdk-17'
.venv\Scripts\python.exe export_results.py
.venv\Scripts\python.exe make_diagrams.py
```

构建首先使用项目原有 `data/16.20.1/ru_RU/all/`；如果该路径不存在，使用提交包内 `source/` 的同一份 JSON 快照。所有转换与推理在本地完成，构建不重新采集数据。

`run_hermit.ps1` 将已安装软件中的内嵌依赖复制到本目录 `tools/hermit-libs/`；不修改 Protégé 安装。提交包不包含虚拟环境、Java 程序或这些依赖副本。

`build_ontology.py` 会检查标注证据确实出现在对应技能原文中、版本一致，以及 OWL/Turtle 往返解析保持同一 RDF 图。`VerifyOntology.java` 检查 OWL 2 DL、一致性、推理结果和两个反例；反例只作用于内存副本，不污染提交本体。

## 6. 建模范围

- `Mage / Support` 表示英雄分类，不表示分路。
- `Shield` 包含魔法伤害护盾；Morgana E 的范围在条件中注明，不能解读为抵挡任意伤害。
- `conditionText` 是自然语言条件，当前不模拟一局游戏，也不自动计算命中、距离或蓄力是否成立。
- `{{ ... }}` 中未解析的数值保留原文，没有猜测伤害量、护盾量或持续时间。
- 没查到某个英雄，不等于证明它没有某机制；未标注部分按开放世界理解。
- `hasSource` 允许连接英雄、技能和效果，因此没有设置一个过窄的全局 domain。

## 7. 证据与来源

`evidence/01_protege_metrics.png`、`02_hermit_query_results.png` 为实际 Protégé 操作截图；后续增加了标题、描述注释，类、属性、实例和推理语义保持一致。`03_reactodia_lux.png` 与 `04_webvowl_statistics.png` 为内置浏览器中的实际结果截图。`05_ontodia_unavailable.txt` 记录原站的连接错误；没有将错误页面伪装为成功结果。

教材：`Копия_Семинар_“Семантические_веб_технологии”.pdf`，PDF 第 249–250 页；第 248 页为 Ontodia 注册要求。

工具来源：[Protégé](https://protege.stanford.edu/software/)、[WebVOWL 项目及新入口](https://github.com/VisualDataWeb/WebVOWL)、[Reactodia 项目](https://github.com/reactodia/reactodia-workspace)。数据来源：[Riot Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon)，具体英雄来源 URL 保存在本体和标注表中。

## 8. 已有提交包

根目录的 `LoL_Ontology_Submission.zip` 与 `submission_manifest.json` 是整理前的提交快照，包内仍使用旧目录结构，并保留俄语报告副本。

重新打包前，先准备 `EXPERIMENT_RU.md`，再运行 `.venv\Scripts\python.exe package_submission.py`；新的提交包会递归包含分类后的输出目录。
