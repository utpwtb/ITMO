# 第二阶段：数据库设计与 PostgreSQL 实现

业务基准为当前俄语第一阶段报告 `../stage1/body.tex`。最新 ER 图使用 **10 个业务实体**，美容师与沙龙服务直接以 M:N 关系表示；照片仍是复合多值属性。关系模型增加 M:N 中间表、两张照片属性明细表和邀请技术表，共 **14 张物理表**。

## 交付内容

| 要求 | 对应成果 |
|---|---|
| 1. ER 模型，≥10 实体、M:N | `report/conceptual_model.json`；`diagrams/integrated/er_model.svg` 完整总图 |
| 2. 教师确认、关系模型 | `TEACHER_REVIEW.md` 为待确认记录；俄语报告包含关系模型、字段类型、键和范式分析 |
| 3. PostgreSQL 实现 | `sql/01_tables.sql`：14 表及两项扩展；实际在 PostgreSQL 17.4 验证 |
| 4. DDL 与触发器完整性 | PK/FK/UQ/CHECK/GiST EXCLUDE；`sql/03_integrity.sql`；32 个自定义触发器 |
| 5. 创建、删除、测试数据 | `00_create_database.sql`、`99_drop_database.sql`、`02_seed.sql`、`install.sql`；PowerShell 包装脚本 |
| 6. 关键函数、过程 | `sql/04_routines.sql`：22 个业务 API，以及内部辅助函数；覆盖 П1–П12 |
| 7. 索引及依据 | `sql/05_indexes.sql`；报告中的逐项理由及五个真实 EXPLAIN ANALYZE 计划 |
| 8. 报告 | 11 页精炼报告 `output/pdf/stage2_report.pdf`；LaTeX 源 `report/stage2_report.tex`；完整源码包 `output/stage2_report_sources.zip` |

教师尚未实际批准，报告和确认记录均如实标注。你需要带模型与教师讨论，并填写真实的确认结果。

## 模型对应关系

核心实体：用户、地区、沙龙、服务类型、沙龙服务、服务师、工作区间、预约、评价、审核决定。“服务师—服务”作为 M:N 关系表达，关系模型保留其实现表。

- `master_service` 的联合主键是 `(master_id, salon_service_id)`，实现 M:N。预约用联合外键引用已存在的服务能力组合，且师傅和服务必须属于同一门店。
- `salon_photo(salon_id, file_path)` 与 `master_photo(master_id, file_path)` 是多值属性的元素关系，不计为概念照片实体。
- `moderation_decision` 的目标为用户、沙龙、服务师或评价，恰好一项非空。审核照片时额外保存 `photo_path`，通过联合外键指向该父对象的具体照片。
- `master_invitation` 保存令牌哈希、有效期、使用和撤销时间。它支持第一阶段已有的一次性邀请，不用于凑概念实体数量。
- 每名师傅的姓名来自用户。评价作者和具体对象通过不可变预约推导。空闲时段与独立评分通过查询计算。

## 启动方式

在 `stage2` 目录执行，使用你自己的 PostgreSQL 连接信息。首次安装需要新建数据库，或教师已为你分配的空数据库；安装者需要创建 schema 和 `btree_gist`、`pgcrypto` 扩展的权限。

```powershell
.\scripts\CreateDatabase.ps1 -HostName localhost -Port 5432 `
  -DatabaseUser postgres -DatabaseName beauty_course -WithDemoData
```

纯 `psql` 方式也可在 Linux/helios 使用 SQL 文件：

```bash
psql -h HOST -U USER -d postgres -v db_name=beauty_course -f sql/00_create_database.sql
psql -h HOST -U USER -d beauty_course -v with_demo_data=true -f sql/install.sql
```

若使用教师提供的现有空数据库，跳过创建，只运行 `install.sql`。省略 `with_demo_data=true` 会建立不含测试数据的工作 schema。

历史测试数据在“表和 DDL 约束已建立、业务触发器尚未安装”时导入，整个安装在同一事务中。这样可以载入过去的已完成记录，而正常 API 始终禁止新建过去的预约；没有暴露绕过业务检查的运行开关。`02_seed.sql` 不是对已运行的工作库追加历史的脚本，只适用于全新演示安装。

默认数据库名为 `beauty_course`。删除脚本仅删除显式指定的项目库，不使用 FORCE，不终止其他会话：

```powershell
.\scripts\DropDatabase.ps1 -DatabaseUser postgres -DatabaseName beauty_course
```

## API 权限与并发

现有的可信后端数据库角色可以通过以下脚本取得业务 API 的 EXECUTE 权限：

```bash
psql -h HOST -U OWNER -d beauty_course -v backend_role=EXISTING_SERVER_ROLE -f sql/06_grant_backend.sql
```

API 使用 SECURITY DEFINER 和固定 search_path；后端角色不取得直接表访问权或内部 helper 的调用权。`p_actor` / `p_client` 来自**后端已经认证的会话**，不能接受浏览器任意指定的用户 ID，也不能把后端数据库凭据交给终端用户。浏览器会话管理属于后续应用实现。

写事务要求 READ COMMITTED。统一事务 advisory lock 对教学版本的写操作排序；GiST 排斥约束同时保护重叠预约。此实现便于验证工作时间、目录、账号、评价、照片配额和令牌的竞态，但会串行化平台写入。报告明确说明这一吞吐限制，未宣称满足第一阶段的 20 并发 SLA。

时间为单一 `Europe/Moscow` 时区的本地 timestamp。业务“当前时间”使用该时区的服务器时间，未依赖客户端自行指定的时区。

照片表只校验文件元数据。实际图片字节检查、EXIF 删除、安全文件名与文件持久化由后续文件服务完成。演示路径不是实际图片文件。

## 实际验证

**79 项检查通过**，包含四组双会话并发测试。测试数据：100 家沙龙、500 个常规师傅及 1 个待激活师傅、50,005 条预约、80,000 个工作区间、12,000 条评价。数据使用 `example.test` 邮箱并相对于安装日期生成。

```powershell
.\scripts\TestDatabase.ps1
```

测试 runner 仅使用项目标记的 `.tools/pg-stage2-data` 临时集群，以独立端口监听 `127.0.0.1`；不连接系统已有的 PostgreSQL 服务。结束后停止临时服务，保留数据目录。此自动测试 runner 是 Windows 本地工具。

证据保存在 `verification/`：

- `test_results.json`：79 个检查的名称与结果。
- `seed_counts.json`：初始填充行数，区别于并发测试提交后的少量新增记录。
- `schema_metadata.json`：实际创建的字段、约束、触发器、索引和例程。
- `explain_plans.json`：五个真实的 EXPLAIN ANALYZE + BUFFERS JSON 计划，没有强行关闭顺序扫描。
- `../diagrams/integrated/geometry_checks.json`：当前两张总图的完整性、正交连线和跨线桥检查。`diagram_geometry.json` 对应早期分图，仅供历史参考。

数据库共 43 个索引：23 个由 PK/UQ/排斥约束建立，19 个面向查询，1 个保证每名师傅只有一个未使用且未撤销的邀请。

## 报告与图的编辑

当前报告正文精简为 11 页，采用两张完整总图。ER 图使用 A3 图页，逻辑模型使用 A2 图页；其余为 A4 正文。数据逻辑图将键放在左侧独立列加粗，右侧数据类型加粗，并删除底部说明。SQL 采用 listings 语法高亮，无需 shell-escape。

`report/stage2_report.tex` 引用 `report/figures/er_model_a3.pdf` 与 `logical_model_a2.pdf` 两个矢量图文件。源码 ZIP 已打包这三个必要文件；解压后使用 XeLaTeX 编译两次。独立图有 SVG、PNG、draw.io 和坐标 JSON，位于 `diagrams/integrated/`。

`scripts/build_report.py` 与 `scripts/build_compact_report.py` 均生成当前精炼版本。它们使用 Python 的 Pillow、reportlab、pypdf 及系统字体，从已验证的数据和元数据生成图与报告。`scripts/CompileReport.ps1` 使用项目现有的 Tectonic。

```powershell
python .\scripts\build_report.py
.\scripts\CompileReport.ps1
```

已验证本地实现，尚未声明部署到 helios。第一阶段中文旧译稿中的实体改动尚未同步，第二阶段以当前俄语版本为准。
