# Lab4 实现检查报告

检查日期：2026-11-06。范围：任务要求核对、已有实现、CIE RGB 输入、几何参数、真实 GUI 计算与导出、已有交付文件。本次只检查并保存复现，没有修复主实现。

## 黑白图是否违反要求

**黑白外观本身不违反要求。问题是当前 GUI 的两张参考图来自白球重算，未展示要求指定的 Lab3 原图。**

[Lab4 任务书](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/АКГ_лр4.docx>) C 项要求将 `image_A` 与“在实验 3 中为白光源生成的 image_1、image_2”比较。这里“白色”修饰光源。[Lab3 任务书](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab3/АКГ_лр3.docx>) 没有要求白光源下的彩色球必须变成灰色；灰度转换是单列的任务。

实际文件和测试说明：

- Lab3 `results/white/image_1.png`、`image_2.png` 显示绿色球；RGB 通道最大差为 126。
- Lab4 默认固定白球 `kd(λ)=1`，用 D65 照明。重算图接近中性，RGB 通道最大差为 1，属于正常的显示结果；并非读取了 Lab3 的 `_gray.png`。
- Lab4 主界面仅显示 `image_A`、`image_1 (recomputed)`、`image_2 (recomputed)`。两张重算图与真正 Lab3 原图的全图通道 MAE 均为 41.06955093，最大差为 136，不能视为原图。
- `reference_lab3` 和包内 `assets` 的原图都与 Lab3 原文件逐字节一致，资源没有丢失。
- **现有 `report/main.tex` 已单独引用两张真正 Lab3 原图，并解释条件差异，也有对比表。** 因而应评价为“GUI 对比不完整；白球受控对比和报告里的历史原图对比需要区分”，不能断言整个实验没有做 C 项。

根因：[experiment.py 第 39 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/experiment.py:39>) 重新计算参考场景；第 43 行从这些计算结果选三图。[gui.py 第 219 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/gui.py:219>) 显示这三张数组，没有载入原 Lab3 图片。[visualization.py 第 116 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/visualization.py:116>) 其实已有读取原图的 `lab3_figure`，但当前 GUI 没有调用。

建议：在 GUI 增加真正 Lab3 原图对比，保留现有白球受控对比并标明来源。不要为消除“黑白”而给白球人为加颜色。报告已经解释了绿色材质、照明公式和显示编码不同，应保留这些解释，不能把历史原图差异全部归因于光谱重建。

![对比图：上排为 Lab4 默认结果，下排前两张为真正 Lab3 原图](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/review_tests/artifacts/comparison_contact_sheet.png>)

## CIE RGB 输入检查

默认光源的绝对 CIE RGB 约为 `(0.2526108113, 0.3104552518, 0.3269916595)`。这里的三个数不等于显示 sRGB 的 0–255 编码，不能直接设置通用的 `[0,255]` 限制，也不能把所有负分量都当成非法。

| 输入或情形 | 实测结果 | 判断 |
|---|---|---|
| 默认 D65 | 回算最大误差约 `1.11e-16` | 正常 |
| 非负光谱产生的 CIE RGB `(-0.01104759449, 0.01266106066, 0.14169472353)` | 重建和真实 GUI 计算均成功 | 负 R 可以合法，当前程序没有一概拒绝 |
| 250 组固定种子的非负基谱组合 | 全部恢复，最大绝对 RGB 误差约 `3.18e-12`，样本本身包含大幅值 | 所选基谱范围内数值计算正常 |
| 空输入、文本、NaN、±Inf、`1e10000` | R/G/B 三个 GUI 输入框分别测试，均拒绝 | 正常 |
| 零向量、长度不为 3、错误嵌套形状 | 重建函数拒绝 | 符合当前函数契约；零光源没有实现为禁用选项 |
| CIE 三原色 `(1,0,0)` 等、520 nm 单采样谱对应颜色 | 报“当前 XYZ 基谱给出负光谱” | 固定基谱的范围限制，不等于颜色本身一定非法 |
| `(255,255,255)` | 作为绝对 CIE RGB 计算成功 | 数学上允许；不会自动按 sRGB/255 解码，使用者需理解输入含义 |
| 默认 RGB 乘 `1e-170` 或 `1e-200` | 被当成零向量拒绝 | 数值边界缺陷，见下文 |
| 默认 RGB 乘 `1e200`、`1e306`、`1e308` | 误差指标溢出，之后物理数组也溢出 | 缺少计算后有限性检查，见下文 |
| API 输入布尔数组或复数 ndarray | 布尔转为 0/1；复数丢弃虚部后继续 | 低优先级 API 输入类型问题，GUI 文本路径不可直接触发 |

上述负 R 示例来自 `spectrum_to_rgb(CMF @ [0.01,0.01,1]) * 0.001`，原谱明确非负。对原色和窄带谱的拒绝记录为 `LIMIT`。当前 README 已声明不裁剪负谱、不更换基谱，因此本次没有将这些拒绝记为算法错误，也不建议在未确认课程允许的情况下直接增加新算法。

### 修改 RGB 后的比较混入输入变化

位置：[experiment.py 第 31 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/experiment.py:31>)、第 39–43 行。

复现：只把第一光源的三个 CIE RGB 分量全部乘 2，几何、强度、第二光源不变。重建后 `image_A` 的绝对颜色与独立计算 `geometry_factors @ 当前输入RGB` 在三个控制点上最大误差仅 `3.55e-15`。这证明修改后的 RGB 被正确用于重建。

但是 `image_2` 仍来自原谱 D65 对应的 RGB。此时程序显示 A/2 的球面像素 MAE 约为 30.26854、最大差为 69。这个差异包含输入强度变化，不能作为重建误差。

**这是比较设计与解释上的缺口，不是“重建函数忽略 RGB 输入”。** 如果 `image_2` 表示历史 Lab3 基准，它保留原颜色是合理的；应明确提示当前输入已偏离原始场景，并另提供“当前 RGB 直接渲染”作为同输入验证。若现有 `image_2 (recomputed)` 被用作当前输入的直接 RGB 基准，则必须让它使用当前输入。测试中这一项按“同输入受控比较”期望记 FAIL，不把它当作任务 C 要求历史原图跟着修改的依据。

### 大数溢出后仍返回成功结果

位置：[reconstruction.py 第 12 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/reconstruction.py:12>)、[experiment.py 第 45 行](</C:/develop/NOTE_UTP/StudyNote/5 Computer Graphics Algorithms/Lab/Lab4/lab4_spectrum/experiment.py:45>) 及第 57 行。

| 对默认 RGB 的倍数 | 结果 |
|---|---|
| `1e100` | 数组和误差指标有限，可正常显示 |
| `1e200` | 光谱、XYZ、RGB 数组仍有限，RMSE 的直接平方已溢出为 Inf |
| `1e306` | 光度亮度出现 Inf，RMSE 也溢出 |
| `1e308` | XYZ/RGB/辐亮度等含 Inf/NaN，显示增益为 0，A 输出全黑，函数仍返回 |

这些输入分量本身都是有限浮点数，GUI 的有限性检查挡不住。界面有机会显示“完成”却拿到无效结果。建议采用稳定的范数/RMSE 算法，并在主要计算、统计与编码之前检查有限性；无法表示时给出清晰的数值范围错误。此处不建议随意套用 sRGB 的 0–255 上限。没有把上述溢出结果写入原 `results`。

### 极小非零 RGB 被误判为零

`np.linalg.norm(rgb) == 0` 的平方求和发生下溢，导致约 `1e-171` 的非零颜色分量被拒绝。应使用不会平方下溢的非零判定或缩放后的范数。这是可重复的数值边界问题，日常默认参数不受影响。

### API 类型检查较宽松

`np.asarray(rgb, float)` 在检查前将 `[True,True,True]` 当成 `(1,1,1)`，将复数 ndarray 的虚部丢弃。复数测试同时捕获到 `Casting complex values to real discards the imaginary part` 警告。建议在转换前校验实数类型。当前 GUI 先解析文本浮点数，因此这一项主要影响直接调用 Python API 的输入。

## 其余问题

| 优先级与性质 | 证据 | 影响与建议 |
|---|---|---|
| 中，现存绘图接口失配 | `comparison_figure(run(...))` 抛 `KeyError: 'reference'`；`scene_figure(run(...))` 抛 `KeyError: 'geometry_rows'` | `visualization.py` 仍依赖旧数据结构；当前 GUI 未调用这两个函数，所以不影响已测主流程。调用前需统一数据契约，或清理旧接口 |
| 低，交付文件与说明不一致 | 现有 `results` 中没有 `absolute_data.npz`，README 却列为已附文件 | 当前 `save()` 能正常生成 NPZ，本轮独立测试成功。任务要求内存中的绝对光谱，未明确要求 NPZ 落盘，因此这是交付说明缺口，不能直接认定 A 项计算未实现 |
| 低，启动和报告路径过期 | README 引用的 `run_lab4.cmd`、`overleaf/main.tex`、`lab4_overleaf.zip` 均不存在；报告引用的 `lab4.py`、`test_lab4.py` 也不存在 | 主入口实际是 `lab4_spectrum/__main__.py`，报告在 `report/main.tex`；`__main__.py` 无参数解析，文档中的 `--no-gui` 不会开启无窗口模式，应更新说明 |
| 环境问题 | `.venv/pyvenv.cfg` 指向的 Python 3.13 路径失效，自带解释器无法启动 | 该虚拟环境不能直接使用；本次使用可用的独立 Python 3.12 运行时及本目录测试依赖，没有修改 `.venv`。这是本机环境问题，不归因于渲染算法 |

## 已通过的主要检查

- 默认 D65 的 RGB 保持、默认三图同像素、既有 600×600 PNG 可以按当前实现复现。
- 200×200、600×600、800×800 场景实际计算；800×800 光谱立方体形状正确。
- 独立解析计算确认朗伯项和毫米到米的转换，前极点单光源系数为 `12.697125653868659`，与程序一致。
- 光谱图像为 float64，波长积分与辐亮度一致，`683Y` 与光度亮度一致；三个控制点均可见。
- 屏幕/分辨率越界、负/零半径、零视线、球在视野外、观察者/光源在球内、空光源列表、光源强度上下界、零发光轴等检查。
- GUI 光源增删、RGB 修改、合法负 R、非法输入弹错后恢复控件、真实后台线程和事件轮询、41 行光谱表、导出。
- 独立导出包含 PNG、CSV、JSON、NPZ，41 个波长记录完整，NPZ 读回与内存光谱一致。

## 测试结果与隔离

100 项记录：**83 PASS、11 FAIL、2 ERROR、4 LIMIT**，外加其中一个检查执行了 250 组固定随机样本。FAIL 多项对应同一根因；比较设计期望、说明文件缺口和低优先级 API 检查均已单独说明，不能按状态数量判断独立 bug 数。

- [完整结果与逐项证据](artifacts/audit_results.json)
- [运行日志](artifacts/run.log)
- [主文件 SHA-256 清单](artifacts/production_hashes.json)
- [独立测试脚本](audit_lab4.py) 和 [运行入口](run_tests.ps1)

主代码、数据、既有结果、报告及原图快照在测试前后哈希完全一致。所有新增脚本、依赖、缓存、导出文件与记录均位于 `review_tests`；没有修改主要实现，也没有改动 Lab3。
