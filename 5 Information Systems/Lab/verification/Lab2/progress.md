# 实验二进度与最终交接

更新：2026-10-28（Europe/Moscow）。原实施记录另存 progress-history.md；计划和历史开发失败不当作通过证据。

| 阶段 | 状态 | 实际交付与证据 |
|---|---|---|
| P0 | 完成 | 保存原Git状态与基线源码；核实Helios/DB；Lab1无重复组合。原测试PU缺失失败已保留，未清理/回退工作区 |
| P1 | 完成 | 严格UTF-8/重复属性/字段白名单解析，精确Long、嵌套对象；合法/非法fixtures和俄语格式说明 |
| P2 | 完成 | USER/ADMIN、ImportOperation、重复安全003迁移；复制32电影/3账号迁移两次无损；权限检查与角色持久化 |
| P3 | 完成 | 统一事务内保存/校验；MovieKey精准名称+Person.id/null；原版本逻辑保留；实际锁超时验证 |
| P4 | 完成 | multipart文件上传；T1/T2/T3独立事务；SUCCESS与领域对象同提交；失败与commit明确回滚测试通过 |
| P5 | 完成 | 俄语导入/分页历史、原始File+CSRF、独立历史轮询；双会话同步、旧表单冲突。按用户新指令移除中文和顶部编号 |
| P6 | 完成 | Helios clean verify140项全部通过；最终RC JMeter13变体各20轮/1640请求通过；17项HTTP候选和正式版均通过；末条length=0追加真实HTTP验证 |
| P7 | 完成 | 同WAR/快照对照。RC0重试/0异常；SERIALIZABLE517重试/4异常，未执行轮次明确标记。最终显式READ COMMITTED+锁+版本 |
| P8 | 完成收尾 | 俄语TeX/PDF、类图/包图DOT+PNG/SVG/PDF、README/JMeter说明/答辩主题、ACCEPTANCE与部署索引；最终PDF渲染和交付完整性记录在相应文件 |

正式服务：/home/studs/s407960/is-lab2-4101，127.0.0.1:40797，正式lab2_4101_表。原全套验证WAR SHA256 cf386061ed67f25abac1f84cf13b61fdcb4a988dddbfe3363c81e670365d0576。

真实重启验收PID44732；05:00观察到退出，原因未从应用日志确定。用户继续后以同WAR恢复为PID49365，再次确认领域数据、角色、历史状态/计数与API表目标正确。

用户四项界面批注已完成：俄语自定义文件控件；删除事务句、历史范围句及刷新按钮；保留两秒自动轮询并修复分页对已删除按钮的依赖。Helios重新Maven package及部署PID65452，当前WAR为867545d9dbbf8d18e9d224e3b29b0c7387ab49458b9f8ed44d7421cbec3f87f4；所有非上述四个UI条目的内容与原WAR相同。真实浏览器文件上传操作10、独立会话自动出现操作11（revision8→8）、管理员双向分页通过。本次未重跑完整JUnit/JMeter。首次过早就绪探测503、回退及修正后通过均记录于ui-review/。最新部署信息见DEPLOYMENT.md。

原始服务器归档57MiB已下载，10868项文件哈希及WAR核对一致；原证据server/不可混入新结论。resume/为续作补充，操作9以独立runId验证末条错误无领域增加/revision变化。私有凭据/测试密码/快照不进入交付。

尚未执行：网络在commit确认瞬间中断的端到端注入；满额1000记录性能压测；多实例归属恢复协议。其余边界、SERIALIZABLE失败和历史试跑说明见ACCEPTANCE/isolation-analysis，不伪报通过。

未进行git reset/clean/staging/commit，保留原目录移动和其他已有变更。后续若服务被外部终止，按README重启并重建SSH隧道；不需要重新生成或清理真实Lab1数据。
