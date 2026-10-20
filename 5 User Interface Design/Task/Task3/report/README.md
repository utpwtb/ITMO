# 作业 3：信息架构报告

本目录包含完整的俄文 LaTeX 报告，主文件为 `main.tex`。封面、正文、结构图和字体均在目录内。

使用 XeLaTeX 连续编译两次，或在 Codex 中打开整个报告目录：

```sh
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

本课程根目录为 `C:/develop/NOTE_UTP/StudyNote/5 User Interface Design`。
可编辑正文为 `sources/information-architecture-ru.md`；运行 `sources/render_information_architecture.py` 可更新正文和结构图，然后重新编译报告。
两个报告生成脚本放在同一 `sources/` 目录，信息架构脚本会导入用户场景脚本中的文本转换函数。
生成脚本使用 Python 与 reportlab，图中文字使用 Windows 自带的 Times New Roman 字体。`fonts/OFL.txt` 为报告字体许可证。
提交版 PDF、独立结构图、PNG 和源码压缩包位于上一级目录 `Task/Task3/`。此源码包可以独立编译，不依赖项目仓库。

报告按当前已实现功能编写，四个主栏目为工作台、历史、知识图谱和设置。结构图与中俄讲稿保持一致。Yandex Disk 上传尚未执行。
