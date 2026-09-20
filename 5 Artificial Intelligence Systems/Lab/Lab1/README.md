# 实验一：Prolog 知识库与 OWL 本体

主题：虚构 RPG 世界的角色与任务匹配。包含实验一的两个部分；实验二的对话式推荐程序不在本次范围内。

## 交付文件

- `report/main.tex`、`report/title.tex`、`report/1.tex`：按提供的 LaTeX 格式和课程模板六个章节撰写的俄语报告。
- `report/main.pdf`：编译后的报告。
- `knowledge.pl`：24 条一元事实、15 条二元事实、7 条规则，俄语注释。
- `game_ontology.owl`：用于 Protégé 的原始 OWL/SWRL 本体。
- `results/game_inferred.owl`：经过 Pellet 推理并显式保存继承类型及推导关系的版本。
- `run_prolog.mjs`：15 个真实 SWI-Prolog 查询与预期结果校验。
- `build_ontology.py`：从 Prolog 读取事实，建立本体、运行 Pellet、执行 9 个 SPARQL 查询，并与 Prolog 比较 7 组结果。
- `results/prolog_results.json`、`results/ontology_results.json`：实际运行的结果。
- `queries.sparql`：9 个独立查询，每次选择其中一条执行，不是一个整体查询。

## 运行

在 Lab1 目录执行，需要 Node.js、Python 和 Java（验证环境使用 Java 17）：

```powershell
npm ci
python -m pip install -r requirements.txt
node run_prolog.mjs
python build_ontology.py
```

`swipl-wasm` 是 SWI-Prolog 官方 WebAssembly 运行时，执行的是 `knowledge.pl` 中的真实 Prolog 规则，不是用 JavaScript 模拟规则。`package-lock.json` 固定依赖版本。Python 脚本也支持此目录下 `.deps` 中的依赖。

安装桌面 SWI-Prolog 后，也可以直接运行：

```powershell
swipl -s knowledge.pl
```

在 Prolog 提示符中输入：

```prolog
ready_for(X,Q).
guildmate(X,Y).
combatant(X), safe_character(X).
```

输入分号查看下一个解。`ready_for(X,Q)` 的结果是 `aria–ruins`、`celia–tower`、`finn–forest`。

## Protégé 演示

1. File → Open 打开 `game_ontology.owl`。
2. Classes 查看 Character 子类；Object properties 查看 Domain/Range；Individuals 查看原始事实。
3. 四个派生类通过 OWL 定义，三个关系通过 SWRL 规则定义。关系推理需要支持这些规则的 reasoner，例如 Pellet；不能把普通 RDF 查询当作 OWL 推理。
4. 可单独打开 `results/game_inferred.owl`，直接检查 `aria readyFor ruins` 等已验证关系。该文件同时保存从类继承得到的类型，便于普通 SPARQL 查询。
5. DL Query 示例：`Character and (readyFor value ruins)`；`Combatant and SafeCharacter`。前者应选出 Aria，后者应选出 Aria、Celia。
6. 如需课堂截图，在自己的 Protégé 窗口截取类树、属性和查询结果。报告内已包含模型关系图，但没有伪造 Protégé 界面截图。本次已完成自动 Pellet 检查，未进行桌面 Protégé UI 操作。

注意：本体没有给基础类增加俄语显示标签，查询中可直接使用报告里的英文实体名。

## 重要语义

- `safe_character` 表示当前记录中不受诅咒，不表示实际战斗安全。
- Prolog 的 `\+ cursed(X)` 是否定即失败；OWL 中缺少事实不能当成否定。为了比较当前快照，对其余五名角色显式声明 `not Cursed`。
- 新增角色时，需要重新判断这种补充声明；两个系统并非对任何扩展数据都等价。
- `AllDifferent` 对应 Prolog 原子名称的区分；角色可以兼具多个职业，因此职业类不设互斥。
- `sword` 等表示武器种类，不是一件唯一的实物。

## 编译俄语报告

封面已填写：Чэнь Хаолинь，P3316，407960，教师 Болдырева Елена Александровна。学生信息在 `report/title.tex`，教师在 `report/main.tex` 的 `TeacherName` 中。

```powershell
cd report
xelatex main.tex
xelatex main.tex
```

也可执行 `tectonic main.tex`。沿用示例的 CMU Serif、CMU Typewriter Text 字体，字体及许可证已附在 `report/fonts`，无需系统安装。将整个 `report` 文件夹上传到 Overleaf，选择 XeLaTeX，并将 `main.tex` 设为主文件即可。`report.tex` 仅作为兼容入口，引用 `main.tex`。

## 课程来源

- [实验任务](https://sunnysubmarines.notion.site/AI-System-a559a46cddc44363bdf27b77e10b7d85)
- [模块一报告模板](https://sunnysubmarines.notion.site/1-ea9a418d514b4baa8f7b4fc4c3ee176e)

模板结构：Введение；Анализ требований；Изучение основных концепций и инструментов；Реализация системы искусственного интеллекта；Оценка и интерпретация результатов；Заключение。报告保留六章，并说明实验二属于后续工作。
