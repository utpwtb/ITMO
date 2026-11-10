# 示例与验证 / Примеры и проверка

> 数据全部虚构，案例v0.1；最近验证：2026-11-04。

## 文件和预期结果

| 文件 | 用途 | 结果 |
|---|---|---|
| library-v0.1.ttl | 完整实例快照 | 44条显式三元组，13个实例 |
| rdf-sample.ttl | RDF入门子集 | 11条；每条均存在于完整快照 |
| authors.rq | Work001作者 | Author001/林岚、Author002/梅雨，按IRI排序 |
| common-authors.rq | Work001与Work002共同作者 | Author001/林岚 |
| verify_examples.py | 实际解析、查询、规则和减法核对 | PASS；2条copyAbout派生关系；差向量[0.13,0.15,0.53] |
| verification-output.json | 本轮运行原始输出 | Python 3.12.14、RDFLib 7.6.0 |

## 普通 Python 环境复现

在已安装 Python 的环境中，安装固定依赖后运行。`python` 应替换成实际可用解释器；Windows 的 Microsoft Store 别名不一定是可用解释器。

```powershell
python -m pip install -r 'C:\develop\NOTE_UTP\StudyNote\5 Knowledge Graphs\Notes\examples\requirements.txt'
python 'C:\develop\NOTE_UTP\StudyNote\5 Knowledge Graphs\Notes\examples\verify_examples.py'
```

脚本以自身所在位置读取数据，无需切换工作目录；所有查询在内存中本地运行，不访问在线服务。`requirements.txt` 固定本次使用的 RDFLib 7.6.0 与其解析依赖 pyparsing 3.3.3。

## 本轮实际环境与命令

环境提供了 Python 3.12.14，初始没有 RDFLib。已将依赖安装到课程的临时目录 `tmp/pdfs/deps`，没有写入系统 Python，也不将依赖文件夹当成笔记交付内容。

```powershell
$env:PYTHONPATH='C:\develop\NOTE_UTP\StudyNote\5 Knowledge Graphs\tmp\pdfs\deps'
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\CHL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\develop\NOTE_UTP\StudyNote\5 Knowledge Graphs\Notes\examples\verify_examples.py'
```

结果记录在 [verification-output.json](verification-output.json)，状态 `PASS`。单条 `copyAbout` 规则由脚本显式实现，没有启用RDFS/OWL推理，没有做SHACL校验，也不把派生结果写回v0.1快照。未来构建OWL例子必须另外注明本体、规则范围与推理器。
