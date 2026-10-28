# 实验二：JSON、唯一性与接口契约

供 [主执行计划](lab2_execution_plan.md) 的 P1–P5 使用。只有 JSON 格式和“名称＋导演”组合唯一两项由用户说明已获教师批准；本文其余细节为保持实现一致而确定的工程约定。

## 1. 新增唯一性规则

定义业务键 `MovieKey(name, directorIdOrNull)`，使用具有两个独立字段的值对象，不用简单字符串拼接，以免分隔符造成碰撞。

| 项目 | 明确语义 |
|---|---|
| 适用范围 | 全系统所有电影，不按创建用户分区 |
| 电影名称 | 使用存储值精确比较，区分大小写、保留首尾空格；本次不额外引入 trim、大小写折叠或 Unicode 归一化 |
| 导演 | 指同一个 Person 对象，持久化后使用 Person.id；不按可能重名的 Person.name 判断 |
| 导入中的导演 | 根据实验一已有唯一 `passportID` 解析/复用 Person，然后用其 id 检查组合 |
| 空导演 | 实验一允许 director=null；同名且均无导演视为相同组合，只允许一条 |
| 自身更新 | 查重时排除被更新 Movie.id；保持原名称和导演可以成功 |
| 名称或导演变化 | 用更新后的完整组合重新查重；部分字段 PATCH 式输入也要合并已有值后检查 |
| 人物属性更新 | 改人物姓名/护照号不改变 Person.id，因此不改变已有电影的导演身份；原人物护照唯一规则继续生效 |
| 文件内重复 | 发现两个相同组合，整个文件失败，不跳过、不覆盖 |
| 与数据库重复 | 整批失败，不做 upsert 或“忽略重复” |

例子：`(A, person#1)` 与 `(A, person#2)` 可并存，即使两位导演同名；`(A, person#1)` 再次创建被拒绝；`(A, null)` 再次创建也被拒绝。`(a, person#1)` 与 `(A, person#1)` 在本契约下不同。

数据库查询必须显式处理空导演，例如分别使用 `m.director.id=:directorId` 和 `m.director IS NULL` 分支。校验比较语义与实际数据库字符串比较保持一致并加入大小写/空格测试；若目标数据库使用不确定性排序规则，以统一的精确比较实现为准。

该规则由业务层查询和异常实现。**不得**为它增加复合 UNIQUE、唯一索引、检查触发器、存储过程或 JPA `@UniqueConstraint`。普通非唯一查询索引可按实测需要添加。实验一已有的主键、人物护照号、用户名唯一约束不在禁止范围内。

使用数据库事务/锁保证业务检查与写入的并发原子性，和把新领域规则写成数据库唯一约束是不同事项；本计划采用前者。

## 2. JSON 文件结构

扩展名 `.json`，编码 UTF-8；顶层结构固定为：

```json
{
  "formatVersion": 1,
  "movies": [
    {
      "name": "Example",
      "coordinates": {"x": 100, "y": -20},
      "oscarsCount": 1,
      "budget": "1000000",
      "totalBoxOffice": 1500000.0,
      "mpaaRating": "PG_13",
      "director": null,
      "screenwriter": null,
      "operator": null,
      "length": 120,
      "goldenPalmCount": null,
      "usaBoxOffice": 500000,
      "tagline": "Example tagline",
      "genre": "COMEDY"
    }
  ]
}
```

完整双记录嵌套示例见 [import-valid.json](examples/import-valid.json)。运行测试时可加唯一 runId 后缀，原样重复导入应触发冲突。

结构规则：

- `formatVersion` 必须为整数 1；`movies` 必须为非空数组。顶层直接数组不属于本协议。
- 每个 Movie 的 Coordinates、Person、Location 都在该 Movie 记录中嵌套给出。导入不接受 `coordinatesId`、`directorId` 或单独的人物数组来替代嵌套字段。
- 所有层级拒绝未知字段及重复 JSON 属性名，防止同一字段的含义取决于解析器处理顺序。
- 服务器自动生成的 `id`、`version`、`creationDate` 及用户/操作归属字段不能由导入文件指定；出现时明确报错。
- 可空字段省略时视为 null；所有必需字段省略或为 null 都报错。字符串不被自动 trim。
- 默认文件上限 5 MiB、最多 1000 条 Movie；这是可配置的工程限额，不是教师额外要求。上线前结合运行环境确认数值，界面、服务器、说明和测试保持一致。
- 可兼容开头的 UTF-8 BOM；拒绝非 UTF-8 文本、注释、尾逗号及非标准数字。

## 3. 字段及数值精度

### Movie

| 字段 | JSON 表示及约束 |
|---|---|
| `name` | 必需 string，至少一个字符；沿用实验一原规则 |
| `coordinates` | 必需嵌套 Coordinates 对象 |
| `oscarsCount` | 必需 32 位整数，>0 |
| `budget` | 必需 64 位整数，>0；推荐十进制整数字符串 |
| `totalBoxOffice` | 可空有限 double，存在时 >0 |
| `mpaaRating` | 必需：G、PG、PG_13、R、NC_17 之一 |
| `director` / `screenwriter` / `operator` | 可空 Person；非空时必须提供完整人物数据，不能只给姓名或 ID |
| `length` | 必需 32 位整数，>0 |
| `goldenPalmCount` | 可空 64 位整数，存在时 >0；推荐十进制整数字符串 |
| `usaBoxOffice` | 必需 32 位整数，>0；totalBoxOffice 非空时必须 ≤ totalBoxOffice |
| `tagline` | 必需 string，可为空字符串（原约束是非 null） |
| `genre` | 可空；非空为 WESTERN、COMEDY、TRAGEDY、HORROR 之一 |

`usaBoxOffice ≤ totalBoxOffice` 是当前实验一代码已有规则，导入继续遵守，不将它描述为本次新增唯一性规则。

### 嵌套对象

| 对象 | 字段与约束 |
|---|---|
| Coordinates | `x`、`y` 均为必需 32 位整数；x ≤ 826，允许负数 |
| Person | `name` 必需且非空；`birthday` 必需、可解析为 ZonedDateTime 的带偏移量/时区字符串；`passportID` 必需 string 且遵守原唯一规则 |
| Person | `eyeColor`、`hairColor` 可空；否则为 GREEN、BLACK、ORANGE、WHITE、BROWN |
| Person | `height`、`weight` 可空；存在时为有限 float 且 >0，转换后也必须有效 |
| Person | `location` 可空，非空时是完整 Location 对象 |
| Location | `x` 必需 64 位整数，可负；`y` 必需有限 double，可负；`name` 必需 string，可为空 |

passportID 原规则只有非 null 和唯一，不额外把“非空/非空白”宣称为实验一要求。导入校验与原领域模型一致。

数值处理统一要求：

1. 32 位整数使用 JSON integer，拒绝小数、boolean 和超范围值。
2. Java Long 字段允许 JSON integer 或匹配十进制整数格式的字符串；转换必须精确、检测范围 `[-9223372036854775808, 9223372036854775807]`，再应用正数等字段约束。
3. JSON integer 解析通过 JSON-P/BigDecimal 等精确数值通道完成，不先转换成 Double；不得截断小数或溢出回绕。
4. double/float 字段使用 JSON number，拒绝 NaN、Infinity 和解析/转换导致的非有限值；检查 float 正值在转换后是否下溢为 0。
5. 浏览器直接上传 File，不先 `JSON.parse` 再 `JSON.stringify`，避免大整数被改写。客户端预览不是服务器校验的替代品。

## 4. 嵌套对象的创建与复用

导入是“批量创建电影”，不隐式编辑已有辅助对象。

1. 每个电影的 Coordinates 新建；坐标数值相同也不强制去重。可空人物为空时不创建 Person。
2. 非空 Person 用 passportID 查找。无对应对象则创建，非空 Location 一起创建。
3. 同一 passportID 在一个文件的多条电影/多个角色中出现时，其完整输入必须一致。比较解析后的字段值，忽略生成字段；Location 比较其字段而非数据库 ID。birthday 使用解析后的 `ZonedDateTime.equals`，包括时区身份，不只比较时间戳；等价的秒数书写格式不会造成差异。浮点字段比较转换到目标 Java 类型后的值，字符串精确比较，省略的可空字段与 null 等价。
4. 已存在 Person 且输入字段一致则复用；任一字段不同则报 `PERSON_DATA_CONFLICT`，整批失败。不能借导入覆盖已有导演姓名、生日或地址。
5. 先校验人物与嵌套位置，再按 location → person/coordinates → movie 的依赖顺序持久化。即便 IDENTITY 使 INSERT 提前执行，所有领域写入仍在同一事务中。
6. 文件内人物缓存仅在本次导入中使用；最终数据库人物查找及电影组合检查在写锁内进行，处理与普通 CRUD 并发的情况。

样例在空测试数据库中的预期新增：2 Movie、2 Coordinates、1 Person、1 Location；历史 `addedCount=2`，因为统计的是主对象 Movie。

## 5. REST 与历史模型

### 上传

`POST /api/imports`，`multipart/form-data`，文件字段名固定为 `file`，file part 的媒体类型为 `application/json`。使用当前 Session Cookie 和 `X-CSRF-Token`。

浏览器自动生成 multipart boundary；JMeter 使用 HTTP Request 的文件上传配置。服务器接收字节后解析 JSON；不能把客户端本机文件路径作为服务器文件路径打开。

建议响应：

```json
{
  "operationId": "42",
  "status": "SUCCESS",
  "addedCount": 2
}
```

```json
{
  "operationId": "43",
  "status": "FAILED",
  "code": "DUPLICATE_MOVIE",
  "error": "第 2 条电影的名称与导演组合已存在",
  "recordNumber": 2,
  "path": "movies[1].director"
}
```

文件总体错误可以没有 recordNumber/path；操作 ID 作为 JSON string 返回以沿用项目大整数策略。已有客户端读取的 `error` 文本字段继续保留。

| HTTP 状态 | 场景 |
|---|---|
| 201 | 整批成功提交 |
| 400 | JSON 结构、类型、字段或领域数值错误，缺少文件 |
| 401 / 403 | 未登录 / CSRF 或权限不允许 |
| 409 | 重复电影组合、人物数据冲突、旧版本更新/删除冲突 |
| 404 | 对象不存在或无权查看指定历史记录（不泄露记录存在性） |
| 413 | 超过上传字节限额 |
| 415 | 不支持的上传媒体类型 |
| 503 | 明确的临时数据库不可用或锁等待超时等，可重试的服务故障 |
| 500 | 未分类的内部故障；错误详情进入服务器日志 |

当前 ErrorMapper 将所有 PersistenceException 一概映射为 409；本次需区分已知冲突、明确回滚的临时故障和结果不明的连接异常。不能把内部故障当成业务拒绝而在测试中标绿。

### 历史

新增 `ImportOperation` 最少字段：

| 字段 | 规则 |
|---|---|
| id | 数据库生成主键 |
| userId | 认证账号 ID；不可采用客户端传入值 |
| status | RUNNING、SUCCESS、FAILED |
| addedCount | 可空整数；仅 SUCCESS 设为实际提交的 Movie 数量；其他状态为 null |
| startedAt / finishedAt | 服务器时间；终态设置结束时间 |
| filename | 展示用原文件名，进行长度限制和输出转义 |
| errorCode / errorMessage | 失败原因摘要，不包含凭据、内部 SQL 或堆栈 |

`GET /api/imports?page=0&size=10`：稳定按 startedAt/id 降序分页。返回 items、total、page、size；普通用户只查询自己的记录，管理员查询全部。身份过滤要同时用于 items 和 total。

`GET /api/imports/{id}`：用于查看详情和核实提交结果，同样执行所有权/管理员检查。

接受了通过认证、CSRF、文件存在和大小检查的上传后，即创建 RUNNING 历史，再做 JSON 解析，因此 JSON 语法或业务校验失败也有 FAILED 记录。未认证、无文件、超限或请求尚未被服务器接受的情况没有历史，作为接口契约明确记录。

SUCCESS 与电影写入一起提交；FAILED 在确认业务事务回滚后用另一事务保存。若提交结果不明，先核实状态，不贸然设为 FAILED。历史存储故障不把导入改成部分成功，诊断信息记录 operationId 以便恢复。

历史界面只有 SUCCESS 显示新增数量；RUNNING/FAILED 显示“—”，避免用 0 混淆“失败”与“成功但空文件”。空 movies 数组按结构错误处理。

## 6. 必须保持的事务不变量

- 一个导入对应一个操作 ID；内部事务重试复用此操作 ID，不重复创建历史。
- 所有 Movie 及本次新建的辅助对象在同一业务事务中提交或回滚。
- 成功历史与业务数据同一提交；失败历史不随着业务数据回滚而消失。
- 本次失败不会修改/删除原有复用对象。
- 一次成功批量导入使电影 revision 增加一次；失败及历史元数据更新不增加电影 revision。
- 文件大小限制、批量 flush 或缓存清理不改变事务原子性；不能按条/按批次 commit。
- 正常接口中的重试只针对已经确认回滚的可重试事务；HTTP 请求是否已提交未知时，让客户端查历史，不能盲目自动重传。
