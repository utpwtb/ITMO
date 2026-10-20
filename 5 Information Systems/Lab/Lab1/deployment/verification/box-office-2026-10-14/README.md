# 学校服务器更新与测试数据重建（2026-10-14）

已在 /home/studs/s407960/is-lab1-4101 更新完整后端及前端，并提交票房关系数据库约束。

- 备份目录：/home/studs/s407960/is-lab1-4101/.runtime/box-office-20261014-172538
- 服务器备份：data-before.sql（旧领域数据及 revision）、source-before.tgz、movie-lab.previous.war。
- 原有 31 部电影、12 个人物、16 组坐标、12 个地点已清空；3 个账号保留。
- 新建 32 部电影、12 个人物、16 组坐标、12 个地点，共 72 个对象，均通过正常 API 入库。
- 没有重置 ID 序列；新电影 ID 为 44–75，具体映射以 manifest 为准。
- 所有电影满足 totalBoxOffice 为 null 或 usaBoxOffice <= totalBoxOffice。包含相等、严格小于、未知总票房等合法情况。
- 43 项服务器 Java 测试、25 项新数据检查通过；非法票房修改在 API 被拒绝且原记录不变，直接 SQL 同样被数据库约束拒绝。
- 线上浏览器：初始没有字段错误；输入 total=100、USA=200 后显示红字；改成相等或总票房留空后提示消失；控制台无错误。
- 新数据导入后保持初始状态，没有执行批量加奖、转移或删除，方便后续演示。

最新日常测试入口为 ../../../manual-test-data/README.md。下载原始文件保存在 new-test-data/，当中 manifest.base 是服务器内部 API 地址；日常测试目录的 manifest.base 已改为本地隧道访问地址。

五项特殊操作的独立初始预期：平均票房 25632844.5625；标语前缀找到 3 部；WESTERN 到 COMEDY 转移 13 个奖项，6 个目标各加 2，余数 1；时长大于 120 各加 2 更新 13 部；按票房 410100013 删除 2 部（ID 46、58）。修改数据后预期随之改变。

详细结果见 verification.json、build-test.log、seed.log 和 new-test-data/verification.json。截图为 server-inline-errors.jpg。旧版本地测试指南已归档为 previous-local-test-data.tgz。
