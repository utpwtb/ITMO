# Lab4 独立审查与输入测试

2026-11-06 检查已有 `lab4_spectrum`，重点检查 CIE RGB 输入和 Lab3 对比图。未修改主实现、既有结果或报告。

结论及问题优先级见 [检查报告](REPORT.md)，完整机器结果见 [audit_results.json](artifacts/audit_results.json)，执行记录见 [run.log](artifacts/run.log)。

本轮有 100 项检查：83 PASS、11 FAIL、2 ERROR、4 LIMIT。FAIL 中含同一问题的多个复现和明确标注的比较设计期望，不能理解成 11 个独立程序错误。250 组固定随机种子的已知可重建光谱另包含在一个检查项中。LIMIT 表示固定三基谱方法的适用范围，不计作错误。

在当前机器上运行：

```powershell
& 'C:\develop\NOTE_UTP\StudyNote\5 Computer Graphics Algorithms\Lab\Lab4\review_tests\run_tests.ps1'
```

也可指定已安装项目 `requirements.txt` 的 Python 3.12+：

```powershell
& 'C:\develop\NOTE_UTP\StudyNote\5 Computer Graphics Algorithms\Lab\Lab4\review_tests\run_tests.ps1' -PythonExecutable 'C:\path\to\python.exe'
```

发现 FAIL/ERROR 时脚本退出码为 1，这是审查发现问题的信号。直接运行 `audit_lab4.py` 亦可，路径按脚本位置解析，无需更改工作目录。

- `audit_lab4.py`：CIE RGB、几何与强度边界、真实 Tk 控件与后台计算、导出、既有文件检查。
- `repro_comparison.py`：只复现默认 600×600 对比图与真正 Lab3 PNG 不同，预期断言失败。
- `artifacts/`：提取的任务正文、机器结果、图像拼图、200×200 导出样本、文件哈希和日志。
- `_deps/`：仅供本轮测试使用的依赖，不修改项目 `.venv` 或全局 Python。
- `_tcl/`、`_mplconfig/`：测试运行时使用的 Tcl 库副本和 Matplotlib 缓存。

GUI 测试使用真实 Tk 窗口、变量、控件、Matplotlib 画布、后台线程和事件循环；窗口隐藏运行，仅替换了弹窗和目录选择器，避免人工交互。没有用假渲染器替换计算。它验证了功能调用，不包含人工拖动、DPI 缩放或屏幕布局验收。

所有写入均在本目录。脚本对主代码、数据、既有结果、报告、Lab3 原图快照执行前后 SHA-256 核对，结果一致。
