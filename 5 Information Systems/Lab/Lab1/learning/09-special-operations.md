# 09 五项特殊操作：把需求写成可验证算法

源码：[MovieService](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/service/MovieService.java>) 与 [MovieResource](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/web/MovieResource.java>)。它们分别负责业务实现和 HTTP 暴露。

## 1. 为什么单独设业务操作

CRUD 修改的是某个对象；“给全部超过两小时的电影加奖项”是集合级规则。让浏览器循环发几十次更新，会产生中间状态、部分失败和复杂竞争。

本项目让客户端只提交参数，由服务端在一个事务中完成整组修改。参数检查和计算边界也统一放在服务端。

| 操作 | 方法名 | API（省略上下文路径） |
|---|---|---|
| 按美国票房删除 | `deleteByBoxOffice` | DELETE `/api/operations/box-office?value=100` |
| 平均美国票房 | `average` | GET `/api/operations/average` |
| 标语前缀 | `prefix` | GET `/api/operations/prefix?value=Hello` |
| 重新分奖 | `redistribute` | POST `/api/operations/redistribute?from=HORROR&to=COMEDY` |
| 时长额外奖励 | `award` | POST `/api/operations/award?length=120&count=3` |

## 2. 按票房删除

先要求参数大于 0，再查询 `m.usaBoxOffice=:v`，对每个受管理电影调用 remove，返回数量。不存在匹配记录时返回 0，这是正常结果。

它没有通过浏览器逐个删除，也没有调用自定义存储过程。若集合中的删除因数据库错误失败，事务应整体回滚。

## 3. 平均值和空集合

当前实现是 JPQL：

```sql
SELECT AVG(m.usaBoxOffice) FROM Movie m
```

例如票房 100、200，结果是 150.0。集合为空时返回 null，页面显示“нет данных”（无数据）。不能把“没有电影”解释成“平均值为零”。

资源方法使用可接受 null 的 `HashMap` 放入 `average`；`Map.of("average",null)` 会抛异常，所以这里不能随意互换。

需要准确描述实现边界：本项目没有自定义数据库函数/存储过程，但 AVG 仍会由 JPQL 翻译给数据库计算，并非 Java 循环算平均值。若教师把“不可直接使用数据库函数”严格解释为连聚合函数也不能用，应先澄清；另一种实现是读取数值后在服务层计算，当前代码不是那一种。

## 4. 前缀搜索为什么要转义

SQL LIKE 中 `%` 表示任意长度匹配，`_` 表示单字符匹配。用户如果输入 `%` 作为普通文本，就不应变成“找全部电影”。

当前选用 `!` 作为转义符，按顺序转换：

```text
! → !!
% → !%
_ → !_
最后在转换后的输入后附加一个 %，表示后面可以有任意字符。
```

例如用户输入 `Hi_%`，搜索模式为 `Hi!_!%%`，含义是以字面上的 `Hi_%` 开头。查询同时声明 `ESCAPE '!'`。

空字符串后面加 `%`，就是所有非 NULL 标语。题目要求 tagline 非 NULL，因此空前缀可以返回全部电影。

## 5. 重新分配奥斯卡：先处理需求矛盾

原题既要求来源电影把“全部奖项”转走，又要求每部电影奖项数大于 0。转空会破坏正数约束。

本项目按已经确认的规则：**每部来源电影保留 1 个，其余转给目标类型。** 文档和页面明确说明，这是需求解释，不是原题完全没有歧义。

设可转移总量为 S，目标电影数量为 n：

```text
S = Σ(来源电影奖项 - 1)
each = S / n       整数除法
rest = S % n       余数
```

按目标 ID 升序分配：前 rest 部多获得 1，其余获得 each。来源电影最后都设为 1。

| 对象 | 原奖项 | 转出/获得 | 最终 |
|---|---:|---:|---:|
| 来源 A | 5 | -4 | 1 |
| 来源 B | 4 | -3 | 1 |
| 目标 C（较小 ID） | 2 | +4 | 6 |
| 目标 D | 2 | +3 | 5 |

转移量为 7，总量前后都是 13。这里均匀的是新增奖项，目标电影的原有奖项可能不同，所以最终总数不一定近似相等。

## 6. 边界条件怎样处理

| 情况 | 当前处理 |
|---|---|
| 两种类型相同 | 拒绝，400 |
| 来源或目标为空 | 拒绝，400 |
| 来源都只有 1 个奖项 | 转移量为 0，允许操作 |
| 目标不是平均整除 | 按 ID 分配余数 |
| 任何目标超出 int 范围 | 抛业务错误，全部回滚 |

ID 排序让结果可重复。若只用数据库未指定顺序的查询，谁得到余数可能每次不同。

## 7. 给长电影额外奖励

条件是 `length > minLength`，不是 `>=`。门槛 120 时，120 分钟的电影不获奖，121 分钟的获奖。奖励 count 必须大于 0，门槛允许为 0。

项目关键表达式：

```java
checkedOscars((long) m.oscarsCount + count)
```

先把一个操作数转为 long，再做加法，避免 int 先溢出。之后检查结果能否放回 int。若写成 `(long)(m.oscarsCount + count)`，转换发生得太晚，错误结果已经产生。

## 8. 为什么先改了 A，B 溢出也没关系

两个对象的修改位于同一个 Database.write 事务。B 触发异常后，数据库回滚 A、B 和 revision 的本次变化。

这不依赖“循环最后才写 SQL”的假设；即便 ORM 提前同步了一部分 SQL，只要事务未提交，仍须按事务规则回滚。

## 检查题

1. 空集合平均值能否等同于 0？
2. 奖项转移是否让目标最终值完全相同？
3. 为什么 `(long)(a+b)` 不能保证避免 int 溢出？

参考答案：不能；当前算法均分新增部分，不抹平旧奖项；括号内 int 加法先发生，必须先提升操作数类型。
