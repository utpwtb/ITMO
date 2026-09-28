# 08 查询、分页、精确过滤与级联删除

源码入口：[MovieService.java](<C:/develop/NOTE_UTP/StudyNote/5 Information Systems/Lab/Lab1/movie-lab/src/main/java/ru/itmo/movie/service/MovieService.java>)。重点读 `page`、`get`、`all`、`delete` 和两个删除人员的辅助方法。

## 1. JPQL 与 SQL 的层次

```sql
SELECT m FROM Movie m WHERE m.name = :value
```

这是 JPQL 示例，不是直接交给 PostgreSQL 的原始 SQL。`Movie` 是实体名，`m.name` 是实体字段。EclipseLink 根据映射生成访问 `movie` 表的 SQL。

`TypedQuery<Movie>` 表示查询返回 Movie 对象，`TypedQuery<Long>` 可以表示 COUNT 返回的计数。你仍在表达数据库查询，但使用实体模型中的名字。

`em.find(Movie.class,id)` 则是按主键查找的直接 API；找不到会得到 null，项目的 `required()` 将其变为 404 业务错误。

## 2. 为什么精确过滤用等号

题目要求完整匹配。输入 `Alpha` 只匹配名字恰好为 `Alpha` 的电影，不匹配 `Alphabet`，也没有自动忽略大小写。

主表过滤条件使用 `= :value`。特殊操作中的“以某前缀开头”是另一种功能，使用 LIKE；不能混在一起。

前端额外用一个复选框决定是否启用过滤，这是因为两种情况必须区分：

- 没启用：不发送 value，不限制结果。
- 启用但输入为空：发送空字符串，过滤真正的空字符串，例如允许为空字符串的 tagline。

## 3. 参数绑定解决什么

项目调用 `q.setParameter("value", v)`，使用户输入作为数据值处理，而不是直接拼成查询结构。

但排序列名一般不能当成普通值参数，因此代码从固定 `COLUMNS` 映射取表达式。例如前端 `director` 映射为 `d.name`。不在表内的列名被拒绝，避免任意查询片段进入 JPQL。

要同时保护**值参数**和**查询结构**，不能只看到用了 `setParameter` 就认定所有字符串拼接都安全。

## 4. LEFT JOIN 为什么会影响“没导演”的电影

电影的 director、screenwriter、operator 都可能为空。若排序时写了会排除空关联的连接方式，某些电影可能意外消失。

当前代码显式使用：

```sql
LEFT JOIN m.director d
LEFT JOIN m.screenwriter s
LEFT JOIN m.operator o
```

左连接保留电影这侧，即使关联人物不存在。按 `d.name` 排序不会仅因为导演为空就删掉电影；但若再加 `WHERE d.name=:value`，空导演电影自然不满足该过滤条件。

这是“连接保留行”与“条件筛选行”两个步骤的区别。

## 5. 分页为什么查两次

一次查询总数，另一次查询当前页。

```text
total = COUNT(满足过滤的电影)
offset = page × size
本页 = 跳过 offset 条后最多读取 size 条
```

项目使用 `setFirstResult()` 与 `setMaxResults()`。page 从 0 开始，size 允许 1～100。如果删除后当前页超出范围，`safePage` 会把它调整回最后有效页。

排序还加 ID 作为第二排序条件。否则两部同名电影之间顺序不确定，翻页时可能出现不稳定的结果。

当前分页是 offset 分页；并发插入时仍可能使跨请求翻页的位置变化。COUNT 和取页也没有放在显式的同一读取快照事务里。因此不能说“任何并发下分页都是严格不变的快照”。对本实验的浏览更新场景，后续轮询会再获取最新内容。

电影分页在服务器完成；辅助对象列表则是服务端返回完整列表后由前端切页。学习时不要把两个路径混为一谈。

## 6. 删除为什么不直接调用 remove 就结束

删除还需要检查对象存在、检查旧 version、按依赖关系删除、更新 revision 并提交。

删除位置对象的实际路径：

```text
找到 Location
→ 比较 version
→ 查找引用该地点的所有 Person
→ 删除引用每个人的 Movie
→ 删除 Person
→ 删除 Location
→ Database.write 更新 revision 并提交
```

引用同一个人三个不同角色的电影应只删除一次。查询用 OR 表达三种角色条件，返回电影实体集合；并不是把三组结果简单相加。

服务层没有配置并依赖 `CascadeType.REMOVE` 来自动完成这条链，而是显式查询并 remove。数据库另有 ON DELETE CASCADE 作为引用完整性保障。JPA 级联配置与数据库外键级联是不同机制。

## 7. 删除数量包含哪些对象

`delete()` 返回被本次服务逻辑删除的对象数，可能包括电影和辅助对象。例如一个地点关联一个人员，该人员关联一部电影，返回值可以是 3，而不是只统计电影。

`deleteByBoxOffice()` 是另一种业务操作，它只删除满足票房条件的电影，所以返回的是匹配电影数量。

## 实验观察

在你自己的练习数据库创建一个人员，让两部电影共享它。删除一部电影，另一部与人员应保留；再删除人员，剩余引用它的电影应被级联删除。先预测结果，再执行并查看数据库。

## 检查题

1. 参数化 value 后，sort 还需要白名单吗？
2. LEFT JOIN 后加人员名称等值过滤，能保留空人员吗？
3. 删除电影是否应删除它的导演？

参考答案：需要，列名属于查询结构；不会保留，因为过滤条件不成立；当前模型中导演是共享独立对象，因此不随单部电影删除。
