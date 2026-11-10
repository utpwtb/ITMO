# RDF 三元组、标识与最小查询 / RDF-триплеты, идентификаторы и простой запрос

> 课程：知识图谱 / Графы знаний；阶段B知识点样稿，尚未并入 L02。
> 来源：Lecture2 第23–34页；研讨课第47–51、54–60、80–85、87页；查询导读参考 Lecture3 第5–14页。页码均为 PDF 页序。
> 先修：[[L01 - 知识图谱导论#2. 实体、谓词与事实 / Сущность, предикат и факт|实体、谓词与事实]]。
> 示例验证：Python 3.12.14、RDFLib 7.6.0 已实际解析并查询；[验证说明](../examples/README.md)、[实际输出](../examples/verification-output.json)。只查询显式事实，未启用 RDFS/OWL 推理。
> 样稿认可：待确认。解释以中文为主；俄文定义在材料确有原文时保留，其余俄文标题为术语译写。

## 为什么要规定三元组

“《知识图谱入门》的作者是林岚”对人很自然，对程序却存在三个问题：书和作者如何唯一识别，“作者”关系的方向是什么，以及姓名字符串是否就是人本身。RDF（Resource Description Framework，资源描述框架）用统一图模型表达这样的断言；Turtle 负责把模型写成可读文本；SPARQL 负责从图中匹配答案。这三者分别是模型、序列化语法、查询语言。

本文始终使用 [[_meta/统一案例设定]] v0.1 的虚构教学数据。先看一个严格三元组，再看怎样把数条三元组组合成可运行的小图。

## RDF 三元组

来源：[Lecture2 · 第23–28、32页](../../Lecture/Lecture2.pdf#page=23)；[研讨课 · 第49–51、54页](../../Lecture/Копия_Семинар_“Семантические_веб_технологии”.pdf#page=49)。

**研讨课第49页原文：**

> «Высказывание о ресурсе представляется в виде триплета.»
>
> «субъект – описываемый ресурс»
> «предикат – свойство ресурса»
> «объект – значение свойства»

中文：关于资源的陈述表示为三元组；主语是被描述的资源，谓词是资源的属性，宾语是该属性的值。

Lecture2 第23页的图片中另有**英文** Definition 2.1.1，不能误写成俄文原定义。按其标准三元组部分整理为：

$$
(s,p,o)\in(U\cup B)\times U\times(U\cup B\cup L).
$$

| 符号 | 含义 | 可用位置 |
|---|---|---|
| $U$ | 命名标识的集合；原图用 URI，本样稿按 RDF 1.1 使用 IRI | 主语、谓词、宾语 |
| $B$ | 空白节点的集合，与 $U,L$ 不相交 | 主语、宾语 |
| $L$ | 字面量的集合 | 只能在宾语位置 |
| $\cup$ | 集合并：允许来自任一集合 | 例如主语可为 IRI 或空白节点 |
| $\times$ | 笛卡尔积：按三个位置依次选值形成有序三元组 | 不表示矩阵乘法 |

原图还提到 generalized RDF triple，可放宽谓词位置；**本课程这份可运行样稿遵循标准 RDF 1.1，不使用该放宽形式。** 补充核实依据：[W3C RDF 1.1 §3.1](https://www.w3.org/TR/rdf11-concepts/#section-triples)，访问日期2026-11-04。

例如：

```turtle
<https://example.org/kg-course/library/Work001>
    <https://example.org/kg-course/library/authoredBy>
    <https://example.org/kg-course/library/Author001> .
```

这是一条三元组，跨三行只是排版。主语是作品，谓词是“其作者为”，宾语是作者资源。末尾的英文句点结束语句。谓词必须是 IRI，不能换成字符串 `"作者"`。

RDF 图是三元组的**集合**；完全相同的三元组写两次，不会得到两份不同事实。文件里的书写先后不决定图中事实顺序；查询结果是否排序是另一个问题。研讨课第50–51页从分开的大学关系合成一张图，就是通过共享资源把断言连起来。

## URI、IRI 与字面量

来源：[Lecture2 · 第29–31页](../../Lecture/Lecture2.pdf#page=29)；[研讨课 · 第47–48、55–60页](../../Lecture/Копия_Семинар_“Семантические_веб_технологии”.pdf#page=47)。

### 命名标识指向资源

URI 的正确英文全称是 **Uniform Resource Identifier**（统一资源标识符）；研讨课第48页标题写成 “Unified”，此处纠正。IRI（Internationalized Resource Identifier）支持更广的 Unicode 字符；本例只用 ASCII IRI，避免初学时把标识转义与图语义混在一起。RDF 1.1 的术语依据是 [W3C §3.2 IRIs](https://www.w3.org/TR/rdf11-concepts/#section-IRIs)，访问日期2026-11-04。

`lib:Author001` 是**作者的标识**，`"林岚"@zh` 是**作者的中文标签值**。标识可被许多作品共享，也可继续拥有职业、作品等属性；姓名值本身不能承担稳定的身份管理。

IRI 看起来像网址，不代表它一定是某个可打开的网页。教材用 URL、URN、文档片段标识和303重定向说明资源及描述文档的区分：可把一所大学作为被描述对象，把网页作为介绍它的文档，二者身份不同。本例的 `https://example.org/...` 只用于虚构教学标识，不要求有网站。

Lecture2 第29页展示同一大学在不同图中有不同标识。**相同标签不能自动合并，不同标识也不能自动证明现实对象不同**；跨源对齐需要额外判断。

### 字面量表达值

**研讨课第59页原文：**「Литерал … - строка символов в кодировке Unicode.」中文：字面量包含 Unicode 字符串形式的表达。原页随后区分普通文本、带语言标签的文本、数值或日期等类型化值；RDF 1.1 还需把词法形式与数据类型一起考虑。

| 写法 | 应怎样读 | 关键区别 |
|---|---|---|
| `lib:Author001` | 一个作者资源的 IRI 缩写 | 可继续作为主语描述 |
| `"林岚"@zh` | 中文姓名文本 | `@zh` 是语言标签，不是资源 ID |
| `"林岚"` | 普通字符串 | RDF 1.1 中对应 xsd:string，不能自动视为带中文标签的同一 RDF 项 |
| `"2024"^^xsd:gYear` | 年份2024 | `^^` 后为数据类型 IRI，不是语言 |
| `"1900-03-26"^^xsd:date` | 日期1900年3月26日 | 词法写法必须符合日期类型 |

研讨课第60页的 `"Chat"@en` 与 `"Chat"@fr` 说明同样文字在不同语言中可以不同，RDF 项也不同。`lib:language "zh"` 则是版本的出版语言属性；它和某个标签上的 `@zh` 分别描述不同事情。

### 空白节点不是缺失值

Lecture2 第31页介绍 blank node（неименованный / анонимный узел，空白节点）。它表示未用全局 IRI 命名的资源，可以当主语或宾语；它不是 SQL NULL，也不是“这里还没有填姓名”。本样稿的稳定作者、作品等全部使用命名 IRI；空白节点的嵌套写法、集合和公理用途留到 L02 正式讲解。

## 最小 Turtle 数据

来源：[Lecture2 · 第33–34页](../../Lecture/Lecture2.pdf#page=33)；[研讨课 · 第80–85、87页](../../Lecture/Копия_Семинар_“Семантические_веб_технологии”.pdf#page=80)。下例为**教学改编**，完整可运行文件是 [rdf-sample.ttl](../examples/rdf-sample.ttl)。

```turtle
@prefix lib: <https://example.org/kg-course/library/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

lib:Work001 a lib:Work ;
    lib:title "知识图谱入门"@zh ;
    lib:authoredBy lib:Author001, lib:Author002 ;
    lib:about lib:Subject001 .
lib:Author001 a lib:Author ; rdfs:label "林岚"@zh .
lib:Author002 a lib:Author ; rdfs:label "梅雨"@zh .
lib:Subject001 a lib:Subject ; rdfs:label "知识图谱"@zh .
```

| 新语法 | 作用 | 本例展开后的意思 |
|---|---|---|
| `@prefix lib: <.../> .` | 规定缩写前缀与命名空间字符串 | `lib:Work001` 展开为命名空间加 `Work001` |
| `<...>` | 写出完整 IRI | 去掉尖括号后才是标识字符串本身 |
| `a` | 谓词位置的 rdf:type 缩写 | `Work001 rdf:type Work`：这个实例属于作品类 |
| `;` | 同一主语下继续写下一个谓词和宾语 | 后面几行仍在描述 Work001 |
| `,` | 同一主语、同一谓词下追加宾语 | 分别产生“作者是Author001”和“作者是Author002”两条事实 |
| `.` | 结束当前三元组语句或缩写组 | 后续可以改写另一个主语 |
| `"..."@zh` | 带中文语言标签的字符串 | 机器可以区分不同语言标签 |

`a` 与 `rdf:type` 等价，不会因为用了缩写就创建另一种关系；使用 `a` 无需额外声明 `rdf:` 前缀。如果直接写 `rdf:type`，则应声明对应的 `rdf:` 命名空间。`lib:` 与 `rdfs:` 是两个不同前缀，各有自己的完整 IRI；前缀名本身可以换，展开后的 IRI 保持相同即可。

**手算三元组数量：** Work001 有类型1条、标题1条、作者2条、主题1条，共5条；两位作者各2条，共4条；主题2条。合计 $5+4+2=11$ 条。前缀声明不是三元组，空行也不增加事实。实际解析结果也是11条。

> [!note] 讲义勘误与规范化
> Lecture2 第34页的 Turtle 片段未显式声明 `rdf:`，采用弯引号，并将 `"26.03.1900"` 标为 `xsd:date`。若独立保存为可运行文件，应补全前缀、使用代码引号 `"`，日期改为 `"1900-03-26"^^xsd:date`。依据为 [Turtle 语法](https://www.w3.org/TR/turtle/#sec-grammar-grammar) 与 [XSD date 词法规范](https://www.w3.org/TR/xmlschema11-2/#date)，访问日期2026-11-04。同理，研讨课第84页说“省略重复对象”，实际示例和后句表达的是**省略重复主语**；分号保留主语、逗号保留主语和谓词。

## 简单查询与结果

来源：[Lecture3 · 第5–14页](../../Lecture/Lecture3.pdf#page=5)，尤其第6–8页变量与基本图模式、第9–11页匹配、第12–14页结构与SELECT。这里只作导读；完整查询内容归 L03。

任务：列出 Work001 的作者资源及姓名。所需数据就是上面的11条；不需要连接网络或读取完整图书馆文件。

```sparql
PREFIX lib: <https://example.org/kg-course/library/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?author ?name WHERE {
  lib:Work001 lib:authoredBy ?author .
  ?author rdfs:label ?name .
}
ORDER BY ?author
```

| 语法 | 意义 |
|---|---|
| `PREFIX` | 查询中的 IRI 缩写声明；这里不是 Turtle 的 `@prefix`，行末不加句点 |
| `?author`、`?name` | 待绑定变量；变量名不声明 Python/SQL 数据类型 |
| `SELECT ?author ?name` | 只输出这两列；变量间不用逗号 |
| `WHERE { ... }` | 指定需要同时匹配的图模式 |
| 第一条模式 | 找出所有与 Work001 通过 authoredBy 相连的对象 |
| 第二条模式 | 用第一条得到的同一个作者资源找到标签 |
| `ORDER BY ?author` | 按作者 IRI 排序；不能误读为按中文姓名排序 |

**匹配步骤：** 第一条得到 Author001 和 Author002。将 Author001 代入第二条，得到 `"林岚"@zh`；将 Author002 代入，得到 `"梅雨"@zh`。同一个 `?author` 将两条模式连接起来，类似 SQL 中通过作者 ID 连接，而非仅凭标签相同连接。

| author（为便读缩写为lib:） | name（保留RDF项形式） |
|---|---|
| lib:Author001 | `"林岚"@zh` |
| lib:Author002 | `"梅雨"@zh` |

以上既是预期结果，也是实际结果；验证脚本打印字符串时会省去语言标签显示，但图中的标签仍保留 `@zh`。本数据每位作者只有一个标签；如果后来新增多语言标签，同一作者可能产生多行，届时要明确语言筛选。没有 `ORDER BY` 时不能依赖返回顺序。查询语义补充依据：[SPARQL 1.1 简单查询](https://www.w3.org/TR/sparql11-query/#WritingSimpleQueries)、[排序](https://www.w3.org/TR/sparql11-query/#modOrderBy)，访问日期2026-11-04。

> [!note] 查询不自动等于推理
> Lecture3 第11页提示，上位类结果需要推理或相应处理才能出现。这里只做显式图匹配：RDFLib 已解析 Turtle，不表示已经启用 RDFS/OWL 推理器。Lecture3 第12–13页图中 `PREFIX` 后带句点的写法也未沿用，运行文件遵循 SPARQL 语法。

## 实际运行与复现

数据：[rdf-sample.ttl](../examples/rdf-sample.ttl)；查询：[authors.rq](../examples/authors.rq)；验证脚本：[verify_examples.py](../examples/verify_examples.py)。

下面演示理解核心 API 所需的最小 Python。**此处工作目录应为 Notes/examples**；使用 `Path` 的完整复现脚本可从任意工作目录启动。

```python
from pathlib import Path
from rdflib import Graph

graph = Graph()
graph.parse("rdf-sample.ttl", format="turtle")
query = Path("authors.rq").read_text(encoding="utf-8")
print(len(graph))
for author, name in graph.query(query):
    print(str(author), str(name))
```

`Graph()` 新建内存图；`parse` 读取语法并建立三元组；`format="turtle"` 明确输入格式；`query` 执行 SPARQL 并返回每行绑定；`str` 只选择打印形式，不会修改原图。第一个输出为 `11`，随后两行分别是完整 Author001 IRI 与林岚、完整 Author002 IRI 与梅雨。

2026-11-04 的实际运行：Python 3.12.14 / RDFLib 7.6.0 / pyparsing 3.3.3，完整验证脚本输出 `status: PASS`。验证范围包括11条子集、44条完整数据、子集包含关系、作者查询、共同作者查询、单条Python教学规则和L01向量减法。详细命令及环境见 [README](../examples/README.md)。没有运行在线端点或 OWL 推理器。

## 自测

1. `lib:Work001 lib:title "知识图谱入门"@zh` 与 `lib:Work001 lib:authoredBy lib:Author001` 的宾语各是什么类型？
2. 为什么不能把 `"林岚"@zh` 放在标准 RDF 三元组的主语位置？应怎样表达林岚写了一部作品？
3. 删除 `?author rdfs:label ?name` 这条模式以后，查询还会自动知道作者姓名吗？
4. 用分号、逗号压缩后的 Turtle 还是11条事实吗？交换语句顺序会改变结果集合吗？

> [!question]- 第1题参考答案
> 前者是带语言标签的字面量，后者是 IRI 标识的资源。两者都能当宾语，但只有后者能在后续三元组中作为主语描述同一个作者。

> [!question]- 第2题参考答案
> 标准 RDF 1.1 主语必须为 IRI 或空白节点。先用 Author001 标识人，再用 `Work001 authoredBy Author001` 表示作者关系，并另写 `Author001 rdfs:label "林岚"@zh`。不能靠姓名字符串替代资源身份。

> [!question]- 第3题参考答案
> 不会。第一条只能绑定作者资源；没有其他绑定 `?name` 的模式时，姓名变量不被绑定。系统不会因为 IRI 对人可读就自动查到姓名。

> [!question]- 第4题参考答案
> 是。缩写不改变展开后的三元组；相同前缀定义下调整事实语句顺序不改变图。查询结果的顺序由排序条件决定，不能依赖 Turtle 书写顺序。

## 知识关联与术语

从 [[L01 - 知识图谱导论#5. 符号表示与向量表示 / Символьное и векторное представление|符号表示]] 到本例，新增的是标准项类型、标识和语法；完整类层级、公理、OWL与开放世界将在 L02 继续。样稿认可后再整理进入 L02，当前不宣称 L02 已完成。

| Русский | 中文 | English | 主要位置 |
|---|---|---|---|
| ресурс | 资源 | resource | URI、IRI 与字面量 |
| субъект | 主语 | subject | RDF 三元组 |
| предикат | 谓词 | predicate | RDF 三元组 |
| объект | 宾语 | object | RDF 三元组 |
| триплет | 三元组 | triple | RDF 三元组 |
| литерал | 字面量 | literal | 字面量表达值 |
| анонимный узел | 空白节点、匿名节点 | blank node | 空白节点不是缺失值 |
| сериализация | 序列化 | serialization | 最小 Turtle 数据 |
| префикс | 前缀 | prefix | 最小 Turtle 数据 |
| базовый шаблон графа | 基本图模式 | Basic Graph Pattern / BGP | 简单查询与结果 |

返回 [[00 - 课程索引]]；案例变更只在 [[_meta/统一案例设定]] 中登记。
