# 用户界面设计课程材料

课程材料集中存放于本目录，产品代码位于 `C:/Users/CHL/.zcode/workspace/default/ai-knowledge-agent`。

| 作业 | 目录 | 内容 |
|---|---|---|
| 作业 1 | [Task/Task1](Task/Task1/) | 演示文稿及历史生成材料 |
| 作业 2 | [Task/Task2](Task/Task2/) | 用户场景报告、LaTeX 源码、源码包及校对记录 |
| 作业 3 | [Task/Task3](Task/Task3/) | 信息架构报告、独立结构图、PNG、LaTeX 源码及校对记录 |
| 可编辑正文和脚本 | [sources](sources/) | 两份俄文 Markdown 正文和 Python 生成脚本 |

- 作业 2 提交版：`Task/Task2/AI_Knowledge_Agent_User_Scenarios_RU.pdf`。
- 作业 3 提交版：`Task/Task3/AI_Knowledge_Agent_Information_Architecture_RU.pdf`。
- 独立结构图：`Task/Task3/AI_Knowledge_Agent_Information_Architecture_Scheme_RU.pdf`。
- 作业 3 中俄双语讲稿：[讲稿](Task/Task3/AI_Knowledge_Agent_Task3_Speech_RU_ZH.md)，俄语讲解约 4 分 10 秒。
- 两份报告的 LaTeX 主文件分别是 `Task/Task2/report/main.tex` 和 `Task/Task3/report/main.tex`。

编辑正文后，在任意目录运行对应的 `sources/render_*.py` 脚本，再进入相应报告目录用 XeLaTeX 编译两次。详细说明见各报告的 `README.md`。
提交版 PDF 是已检查的版本；重新编译后，如需替换提交版，应检查 `report/main.pdf` 后再复制到上一级的对应 PDF。

原有 `Task/Task1/AI_Knowledge_Agent_RU_5min.pptx` 保留。项目目录迁来的四个版本位于 `Task/Task1/presentation/`，没有覆盖原有文件。演示文稿的历史生成脚本、素材及预览存于 `Task/Task1/.pptx-build-ru/`；历史检查记录中的旧路径仅作溯源。

`migration-manifest.json` 记录迁移前后路径和 SHA-256，供核对文件。Yandex Disk 上传尚未执行。