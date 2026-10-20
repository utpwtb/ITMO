# 作业 2：用户场景报告

本目录包含完整的俄文 LaTeX 报告，主文件为 `main.tex`。封面、正文、流程图和字体均在目录内。

使用 XeLaTeX 连续编译两次，或在 Codex 中打开整个报告目录：

```sh
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

本课程根目录为 `C:/develop/NOTE_UTP/StudyNote/5 User Interface Design`。
可编辑正文为 `sources/user-scenarios-ru.md`；运行 `sources/render_user_scenarios.py` 可更新正文和流程图，然后重新编译报告。
生成脚本使用 Python 与 reportlab，图中文字使用 Windows 自带的 Times New Roman 字体。`fonts/OFL.txt` 为报告字体许可证。
提交版 PDF 和源码压缩包位于上一级目录 `Task/Task2/`。此源码包可以独立编译，不依赖项目仓库。