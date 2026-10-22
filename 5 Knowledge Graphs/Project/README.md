# 第一阶段：LoL 英雄与技能数据采集

老师面前的代码与数据展示可使用 [中俄对照稿](<C:/develop/NOTE_UTP/StudyNote/5 Knowledge Graphs/Project/presentation_zh_ru.md>)，俄语正文按 B2 难度编写，预计 7 分钟以内；另有 [俄语纯稿](<C:/develop/NOTE_UTP/StudyNote/5 Knowledge Graphs/Project/presentation_ru.txt>) 供朗读练习。脚本的注释、命令行提示和导出清单说明已改为俄语。

`fetch_lol_data.py` 按本目录第一阶段 PPT 第 3、4 页实现采集，Python 3.10+，只使用标准库，**无需安装依赖、无需 Riot API Key**。

本次已实际采集并校验 `16.20.1 / ru_RU`：173 个英雄、865 条主要技能，CommunityDragon 和官网各覆盖 173 个英雄，错误为 0。结果位于 `data/16.20.1/ru_RU/all/`，523 个来源文件的摘要已核验；10 项离线检查通过。技能机制仍需按下文核验表人工标注。

## 快速运行

在本目录打开 PowerShell：

```powershell
# 采集所有英雄。首次解析最新版本并锁定，默认俄语。
py -3.11 fetch_lol_data.py

# 同时采集 PPT 提到的两个补充来源。
py -3.11 fetch_lol_data.py --community-dragon --official-pages

# 先用三个英雄试跑，附带图标下载。
py -3.11 fetch_lol_data.py --champions Lux Morgana Karma --community-dragon --official-pages --download-images
```

本机已验证 `py -3.11` 可用；默认 `py -3` 指向失效的 Python 3.13 安装。换电脑后按实际安装版本调整，或使用可用的 `python` 命令。默认输出到脚本旁的 `data/`，不受当前终端目录影响。

其他常用参数：

```powershell
# 明确指定研究版本；该版本也写入锁文件。
py -3.11 fetch_lol_data.py --version 16.20.1

# 中文数据，便于阅读；正式项目按 PPT 使用 ru_RU。
py -3.11 fetch_lol_data.py --locale zh_CN --champions Lux

# 主动切换到当前最新版本；不同版本分目录存储。
py -3.11 fetch_lol_data.py --version latest

# 更新已下载的来源，核验表中的人工编辑保留。
py -3.11 fetch_lol_data.py --refresh --community-dragon --official-pages

py -3.11 fetch_lol_data.py --help
```

## 数据来源与 API

| 来源 | 请求地址 | 用途 |
| --- | --- | --- |
| Data Dragon 版本 | `https://ddragon.leagueoflegends.com/api/versions.json` | 首次确定版本，保存 `version-lock.json` |
| Data Dragon 语言 | `https://ddragon.leagueoflegends.com/cdn/languages.json` | 校验 `ru_RU` 等语言代码 |
| Data Dragon 英雄列表 | `https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion.json` | 全部英雄 ID、名称和分类 |
| Data Dragon 英雄详情 | `https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion/{id}.json` | 基础属性、被动、Q/W/E/R、描述和图标文件名 |
| CommunityDragon 构建信息 | `https://raw.communitydragon.org/{patch}/content-metadata.json` | 核对 `major.minor` 补丁，记录客户端内容构建号 |
| CommunityDragon 英雄详情 | `https://raw.communitydragon.org/{patch}/plugins/rcp-be-lol-game-data/global/{language}/v1/champions/{key}.json` | 客户端分类、技能等补充数据 |
| 官网英雄页面 | `https://www.leagueoflegends.com/ru-ru/champions/` 中的实际详情链接 | 人工核对术语、分类与技能描述 |

`version` 形如 `16.20.1`，对应 CommunityDragon `patch` 为 `16.20`。俄语在 CommunityDragon 中写作 `ru_ru`，英语 `en_US` 使用 `default`。脚本检查补丁和英雄数字 ID，不会自动混入 `latest` 或退回其他语言。

官网抓取使用公开 HTML 及其中的 `__NEXT_DATA__` 数据，不依赖未公开的 CMS API。页面结构变化时保留 HTML 并报告失败。官网没有固定历史版本保证，因此采集结果单独保存，只用于核对。CommunityDragon 同补丁仍可能存在构建或热修差异，也单独保存，不自动覆盖主来源。

接口说明已核对：[Riot Data Dragon 文档](https://developer.riotgames.com/docs/lol#data-dragon)、[CommunityDragon 资源说明](https://github.com/CommunityDragon/Docs/blob/master/assets.md)、[官方俄语英雄列表](https://www.leagueoflegends.com/ru-ru/champions/)。

## 输出内容

```text
data/
  version-lock.json
  catalog/                         # 版本、语言列表与请求元数据
  16.20.1/
    ru_RU/
      raw/
        ddragon/                   # 列表及每个英雄的原始 JSON
        communitydragon/           # 可选，原始客户端 JSON 与构建信息
        official/                  # 可选，官网原始 HTML
      images/                      # 可选，英雄与技能图标
      all/                         # 全量导出；子集写入 subset-<hash>/
        champions.json
        champions.csv
        abilities.json
        abilities.csv
        champion_classes.csv
        mechanics_review.csv
        communitydragon.json
        official_pages.json
        manifest.json
        errors.json
```

| 文件 | 内容 |
| --- | --- |
| `champions.json/csv` | 英雄 ID、数字 key、俄语名称、称号、分类、基础属性、资源类型、图标 URL、版本和来源 |
| `abilities.json/csv` | 被动与 Q/W/E/R、技能名称、描述、tooltip、冷却、消耗、距离、图标 URL、版本和来源 |
| `champion_classes.csv` | 一行一个“英雄—分类”关系，方便后续构建知识图谱 |
| `mechanics_review.csv` | 每个技能的原文与空白机制、作用对象、触发条件、核验状态，供人工标注 |
| `communitydragon.json` | 同补丁补充数据，与主来源分开 |
| `official_pages.json` | 当前官网分类与技能描述，与主来源分开 |
| `manifest.json` | 版本、语言、采集选项、数量、完整性、每个原始文件 URL/时间/SHA-256、错误 |
| `errors.json` | 失败来源和英雄，便于重跑与排查 |

JSON 保留原始 HTML 描述并增加纯文本。CSV 使用 UTF-8 BOM，Excel 可直接打开；数组和字典以 JSON 字符串保存。完整原始响应保留在 `raw/`，无需担心规范化导出遗漏字段。

## 后续知识图谱使用注意

- `classes` 是 Data Dragon 的 `tags`，如 `Mage`、`Support`，表示英雄分类，不能直接当成上路、打野等分路。
- PPT 要求从描述提取机制并人工核验。因此脚本提供原文和核验表，**没有把关键词命中自动当成已验证的“护盾/禁锢”等关系**。`mechanic`、`target`、`condition` 需要结合描述填写，例如护盾保护自身还是友军、控制是否有命中或蓄力条件。
- `mechanics_review.csv` 重跑和 `--refresh` 都会保留已有人工编辑，仅为新获取的技能追加待核验行。建议每个技能的每种机制单独一行，需要多机制时复制对应行。
- tooltip 中的 `{{ ... }}` 变量可能缺少可解析值。脚本原样保留，并列出 `unresolved_placeholders`，不会猜测伤害、护盾量或持续时间。`effect` 数组也不是已标注的技能机制。
- Data Dragon 主要给出 P/Q/W/E/R。变身、组合和子技能可能需要 CommunityDragon 补充与人工整理，不能将五条记录理解为所有独立机制已覆盖。
- `icon_url` 始终导出。加 `--download-images` 才下载图标，不批量下载皮肤和技能视频。

## 缓存、失败与复现

每个原始文件附带 `.meta.json`，记录 URL、抓取时间和摘要。重跑会校验后复用缓存；损坏缓存会重新下载。网络错误、429、部分 5xx 会按退避策略重试，普通 403/404 会直接记录错误，不会静默改用其他版本。

默认同时处理 4 个英雄，但所有线程共用请求间隔限制。可用 `--workers 1` 改为串行，或用 `--delay 0.5` 降低请求频率。`--workers` 范围为 1–8。

退出码 `0` 表示本次请求的采集项全部成功；`1` 表示失败或部分失败，已获取的数据仍会导出；`130` 表示手动中断。中断后原始文件仍可用于下次续跑。`manifest.json` 的 `complete` 和 `counts` 可用于检查完整性。

全量与指定英雄子集的规范化导出分目录保存，避免试跑覆盖全量结果。没有请求的补充来源在该次导出中为空，不会沿用上一次的结果。后续不带 `--version` 会复用锁文件，只有主动传入版本或 `latest` 才更新默认版本。

离线检查可运行 `py -3.11 -m unittest -v test_fetch_lol_data.py`，不会向外网发送请求。
