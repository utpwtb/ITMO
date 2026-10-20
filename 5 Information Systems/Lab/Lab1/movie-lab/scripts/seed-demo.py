#!/usr/bin/env python3
"""Create a persistent manual-test dataset through the normal API (no SQL/reset).

Credentials are read from the environment or an interactive password prompt.
The local manifest makes interrupted runs resumable without duplicating rows.
"""
import argparse
import datetime as dt
import getpass
import http.cookiejar
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


class Api:
    def __init__(self, base):
        self.base = base.rstrip('/') + '/api/'
        self.csrf = ''
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, path, method='GET', body=None):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(self.base + path, data=data, method=method,
            headers={'Content-Type': 'application/json', 'X-CSRF-Token': self.csrf})
        try:
            with self.opener.open(request, timeout=30) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            try:
                value = json.load(error)
            except ValueError:
                value = {'error': 'Non-JSON HTTP error'}
            return error.code, value

    def ok(self, path, method='GET', body=None):
        status, value = self.call(path, method, body)
        if not 200 <= status < 300:
            raise RuntimeError(f'{method} {path}: HTTP {status}: {value.get("error", value)}')
        return value

    def movies(self):
        rows, page = [], 0
        while True:
            data = self.ok(f'movies?page={page}&size=100&sort=id')
            rows.extend(data['items'])
            if len(rows) >= data['total']:
                return rows
            page += 1


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def fixtures(passport_prefix, box_office, label_prefix='[Л1]'):
    records = []
    for i in range(12):
        records.append(('locations', f'L{i+1:02}', {
            'name': f'[Л1] Место {i+1:02}',
            'x': '9223372036854775807' if i == 0 else str(i - 5),
            'y': [-12.5, 0, 55.75][i % 3]}))
    for i in range(16):
        records.append(('coordinates', f'C{i+1:02}', {
            'x': [826, 0, -1, -2147483648, 125, 500, 825, -50][i % 8],
            'y': [2147483647, -2147483648, 0, 45][i % 4]}))
    names = ['Алексей Орлов', 'Алексей Орлов', 'Анна Смирнова', 'Борис Иванов',
             'Вера Петрова', 'Глеб Соколов', 'Дарья Волкова', 'Елена Морозова',
             'Игорь Кузнецов', 'Без места', 'Каскад человека', 'Каскад места']
    colors = ['GREEN', 'BLACK', 'ORANGE', 'WHITE', 'BROWN']
    for i, name in enumerate(names):
        records.append(('people', f'P{i+1:02}', {
            'name': '[Л1] ' + name, 'passportID': f'{passport_prefix}-{i+1:02}',
            'birthday': ['1985-02-03T12:30:00+03:00[Europe/Moscow]',
                         '1990-06-15T09:00:00Z',
                         '1978-11-20T18:45:00+09:00[Asia/Tokyo]'][i % 3],
            'location': None if i == 9 else '@L' + f'{i+1:02}',
            'eyeColor': None if i == 9 else colors[i % 5],
            'hairColor': None if i == 9 else colors[(i+2) % 5],
            'height': None if i == 9 else 160.5 + i,
            'weight': None if i == 9 else 55.5 + i}))
    genres = ['WESTERN', 'COMEDY', 'TRAGEDY', 'HORROR']
    oscars = [[5, 4, 4, 2, 2, 2], [2, 3, 1, 2, 3, 1],
              [1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 7]]
    ratings = ['G', 'PG', 'PG_13', 'R', 'NC_17']

    def movie(name, index, **changes):
        value = {'name': name, 'coordinates': '@C' + f'{index % 12 + 1:02}',
                 'oscarsCount': 2, 'budget': str(1000000 + index * 100000),
                 'totalBoxOffice': None if index % 4 == 0 else 2500000.5 + index * 10000,
                 'mpaaRating': ratings[index % 5],
                 'director': '@P' + f'{index % 10 + 1:02}',
                 'screenwriter': None if index % 3 == 0 else '@P' + f'{(index+3) % 10 + 1:02}',
                 'operator': None if index % 4 == 0 else '@P' + f'{(index+5) % 10 + 1:02}',
                 'length': [119, 120, 121, 90, 150, 180][index % 6],
                 'goldenPalmCount': None if index % 2 == 0 else str(index % 4 + 1),
                 'usaBoxOffice': 100 + index * 100, 'tagline': f'[Л1] Приключение {index+1:02}',
                 'genre': None}
        value.update(changes)
        return value

    for i in range(24):
        name = f'[Л1] Фильм {i+1:02} {genres[i // 6]}'
        if i in (0, 1):
            name = '[Л1] Двойник'
        elif i == 2:
            name = '[Л1] Альфа'
        elif i == 3:
            name = '[Л1] альфа'
        elif i == 4:
            name = '[Л1] 中文电影'
        elif i == 5:
            name = "[Л1] O'Brien"
        values = movie(name, i, genre=genres[i // 6], oscarsCount=oscars[i // 6][i % 6])
        if i in (2, 14):
            values['usaBoxOffice'] = box_office
            if values['totalBoxOffice'] is not None:
                values['totalBoxOffice'] = max(values['totalBoxOffice'], box_office)
        if i in (0, 1, 2):
            values['tagline'] = f'[Л1] Префикс: {i+1}'
        elif i == 3:
            values['tagline'] = '[Л1] 100%_! буквально'
        elif i == 4:
            values['tagline'] = '[Л1] 100abc — не буквальный префикс'
        records.append(('movies', f'M{i+1:02}', values))
    extras = [
        ('Удаление координат A', {'coordinates': '@C13', 'length': 90}),
        ('Удаление координат B', {'coordinates': '@C13', 'length': 95}),
        ('Удаление человека A', {'coordinates': '@C14', 'director': '@P11', 'length': 100}),
        ('Удаление человека B', {'coordinates': '@C14', 'operator': '@P11', 'length': 105}),
        ('Удаление места A', {'coordinates': '@C15', 'screenwriter': '@P12', 'length': 110}),
        ('Удаление места B', {'coordinates': '@C15', 'director': '@P12', 'length': 115}),
        ('CRUD — можно менять и удалять', {'coordinates': '@C16', 'length': 120}),
        ('Пустой слоган и большой Long', {'coordinates': '@C16', 'length': 121,
             'budget': '9223372036854775807', 'goldenPalmCount': '9223372036854775807',
             'totalBoxOffice': None, 'director': None, 'screenwriter': None, 'operator': None,
             'tagline': '', 'genre': None})]
    for i, (name, changes) in enumerate(extras):
        # Cascades are deliberately isolated from the ordinary actors/places.
        changes = {'director': None, 'screenwriter': None, 'operator': None, **changes}
        records.append(('movies', f'M{i+25:02}', movie('[Л1] ' + name, i+24, **changes)))
    return [(kind, key, {field: value.replace('[Л1]', label_prefix) if isinstance(value, str) else value
                         for field, value in template.items()}) for kind, key, template in records]


def write_guide(output, manifest, after, forecasts):
    entries = manifest['records']

    def ref(key):
        return f'{key}（ID={entries[key]["id"]}）'

    rows = '\n'.join(f'| {key} | {entry["id"]} | {entry["initial"]["name"]} | '
                     f'{entry["initial"].get("genre") or "未指定"} | '
                     f'{entry["initial"]["length"]} | {entry["initial"]["oscarsCount"]} | '
                     f'{entry["initial"]["usaBoxOffice"]} |'
                     for key, entry in entries.items() if entry['kind'] == 'movies')
    auxiliary = '\n'.join(f'| {key} | {entry["kind"]} | {entry["id"]} |'
                          for key, entry in entries.items() if entry['kind'] != 'movies')
    target_results = '、'.join(f'ID {key} → {value}' for key, value in forecasts['redistribute']['target_oscars_after'].items())
    text = f'''# 实验 1 手动测试数据与操作指南

生成日期：{manifest['created_at'][:10]}。数据通过 `{manifest.get('public_base', manifest['base'])}` 的后端 API 添加，经过 ORM 校验、数据库约束和正常事务。本脚本没有直接写数据库。

新添加 **32 部电影、12 个人物、16 组坐标、12 个地点，共 72 个对象**。有名称的样例以 `[Л1]` 开头。M01、P01 等是本指南的样例代号，不是系统字段；实际 ID 见下表。

## 使用顺序

先测试查看、筛选、排序、分页和校验，再测试并发修改，最后测试特殊操作和级联删除。下列数字是导入完成时的快照；修改或删除之后，预期结果也会变化。

刷新页面后取消勾选 `Включить фильтр`，点击 `Применить`，电影页应显示当前共 **{len(after['movies'])} 条**。本次导入前的集合保存在 [before.json](before.json)，实际对象与关联见 [after.json](after.json)。

## 1. 查看、关联对象与基本 CRUD

| 要测试的功能 | 操作 | 预期结果 |
|---|---|---|
| 按 ID 查看、关联信息 | 打开 {ref('M01')} | 显示电影全部字段；坐标、导演及导演的地点可以在详情看到 |
| 多部电影复用关联对象 | 对照 M01 与 M13，以及 M01 与 M02 的导演 | M01/M13 复用 C01；P01/P02 同名但护照和 ID 不同，不能仅凭姓名认为是同一人 |
| 新增关联选择 | 添加电影，在坐标、人物选择框选择已有对象 | 不必重新创建关联对象，保存后详情引用所选 ID |
| 可选字段 | 打开 {ref('M32')}；查看 {ref('P10')} | M32 的人物、类型、总票房为空；P10 的地点、颜色、身高、体重为空 |
| 修改 | 修改 {ref('M31')} 的名称、时长或票房，再打开详情 | 新值保存，ID 不变，version 增加 |
| 删除电影 | 最后删除 {ref('M31')} | 电影消失，C16 仍存在，M32 仍存在 |
| 自动 ID 与日期 | 新建一部符合要求的电影 | ID、creationDate 自动产生；删除后 ID 不要求连续 |
| Long 精度 | 打开 {ref('M32')}、{ref('L01')} | M32 的预算和金棕榈数、L01 的 X 保留 `9223372036854775807`，没有四舍五入 |
| 时区保存 | 查看 P01、P02、P03 的生日 | 分别保留 Moscow、UTC、Tokyo 的 ISO 日期时间；具体文本见 after.json |

## 2. 精确筛选、排序和分页

筛选操作均须勾选 `Включить фильтр` 并点击 `Применить`。排序可单独使用。导演/编剧/摄影师筛选的是人物姓名，不是人物 ID。

| 字段（Колонка） | 输入（Точное значение） | 初始预期 |
|---|---|---|
| Название | `[Л1] Двойник` | 恰好两部：M01、M02 |
| Название | `[Л1] Двой` | 零部，普通筛选不是模糊搜索 |
| Название | `[Л1] Альфа` / `[Л1] альфа` | 分别仅 M03 / M04，区分大小写 |
| Название | `[Л1] 中文电影` / `[Л1] O'Brien` | 分别仅 M05 / M06，支持 Unicode 和引号 |
| Слоган | 留空且启用筛选 | M32，测试空字符串精确匹配 |
| Жанр | `WESTERN` / `COMEDY` / `TRAGEDY` / `HORROR` | 每种 6 部；另有 8 部类型未指定 |
| MPAA | `G` / `PG` / `PG_13` / `R` / `NC_17` | 均有样例，可逐个筛选 |
| Режиссёр | `[Л1] Алексей Орлов` | 显示导演为 P01 或 P02 的电影，两个人同名 |
| Сценарист / Оператор | 从详情复制相应人物的完整姓名 | 只显示对应角色姓名完全相同的电影 |

按 ID 升序/降序查看第一条和最后一条。也可逐一按七个字符串字段排序。名称相同的电影按 ID 升序稳定排列；空关联名称的先后位置由数据库排序规则决定。

每页选择 10：32 部样例足够测试 4 页（10/10/10/2）；每页 20：2 页（20/12）；每页 50：1 页。12 个人物/地点和 16 组坐标也可测试辅助对象的分页。若之后另加了数据，页面数量随总数变化。

## 3. 五项特殊操作

**平均数、按时长加奖和按类型转移都针对整个集合。后两项会修改数据；删除操作也会删除匹配的全部电影。每项下列预期按导入后的原始状态独立计算，不适合在做完其他修改后直接套用。**

| 操作 | 输入 | 初始预期 |
|---|---|---|
| 平均美国票房 | 点击平均数 | 总计 {forecasts['movie_count']} 部，平均值约 `{forecasts['average']:.10f}` |
| 标语前缀 | `[Л1] Префикс:` | 返回 M01、M02、M03 共 3 部 |
| 标语前缀的特殊字符 | `[Л1] 100%_!` | 仅 M04；`%`、`_`、`!` 被当作普通字符，不能匹配 M05 |
| 标语前缀留空 | 空字符串 | 返回全部电影，与空字符串“精确筛选”不同 |
| 转移奥斯卡 | WESTERN → COMEDY | 转移 {forecasts['redistribute']['transferred']} 个，目标 {forecasts['redistribute']['recipients']} 部，每部加 {forecasts['redistribute']['each']}，余数 {forecasts['redistribute']['remainder']}；来源每部保留 1 |
| 按时长加奖 | 时长阈值 120，奖励数 2 | 更新 {len(forecasts['award_ids'])} 部；119 和 120 分钟不变，121 分钟及以上的相应电影各加 2 |
| 按美国票房删除 | `{forecasts['delete_box_office_value']}` | 删除恰好 2 部：M03、M15；关联坐标/人物保留 |

转移后目标奥斯卡精确值：{target_results}。

完整预测（含按时长操作应更新的 ID）见 [expected-results.json](expected-results.json)。重复执行转移时，来源已仅剩 1，转移数量会变成 0；重复加奖则会再次增加，不是只执行一次。

## 4. 级联删除：三个相互独立的练习组

下面的对象只用于对应删除练习，普通样例不会引用它们。删除前打开关联电影并记录 ID。

| 删除对象 | 初始应同时删除 | 应保留 |
|---|---|---|
| 坐标 {ref('C13')} | {ref('M25')}、{ref('M26')} | 其余电影、人物、地点 |
| 人物 {ref('P11')} | {ref('M27')}、{ref('M28')}，覆盖导演和摄影师两种引用 | C14、L11 及其余样例 |
| 地点 {ref('L12')} | {ref('P12')}、{ref('M29')}、{ref('M30')}，覆盖编剧和导演引用 | C15 及其余样例 |

删除电影 M31 只删除该电影，不向上删除共享坐标 C16。这是当前系统实现的级联方向；原任务对方向没有精确定义。

## 5. 输入约束与错误提示

非法值不应作为有效样例保存。通过新增表单逐个尝试；每次只改一个字段，以便辨认具体错误。浏览器阻止提交也属于前端限制；后端错误应显示在对应对话框。

| 对象/字段 | 有效对照 | 无效测试 |
|---|---|---|
| Coordinates.x | C01=826；C03=-1；C04=-2147483648 | 827；小数；超出 int 范围 |
| Coordinates.y | 0、负数、int 极值 | 留空；小数；超出 int 范围 |
| Movie.name | 正常非空名称，可重复 | 留空 |
| Movie.coordinates / mpaaRating | 选择已有坐标/有效分级 | 未选择 |
| Movie.oscarsCount / budget / length / usaBoxOffice | 正整数 | 0、负数、留空；整数溢出 |
| totalBoxOffice / goldenPalmCount | 留空或正数 | 0、负数 |
| totalBoxOffice 与 usaBoxOffice | 总票房留空，或总票房 ≥ 美国票房；M03/M15 提供相等样例 | 填总票房 100、美国票房 200，应显示字段错误且不能保存 |
| Movie.tagline | M32 的空字符串是合法值 | `null` 非法，但普通表单无法直接输入 JSON null |
| Person.name / birthday | 完整姓名；ISO 带时区日期时间 | 空姓名；不带时区、格式错误或非法日期的生日 |
| Person.height / weight | 留空或正数 | 0、负数 |
| Person.passportID | 每人唯一；从 P01 复制护照做重复测试 | 与 P01 相同应得到重复护照错误 |
| Location.x / y | 0、负数合法，L01 的 X 是 long 极值 | 留空；X 超出 long 范围 |
| 特殊操作 | 两个不同类型；阈值≥0且奖励数>0 | 相同来源/目标类型；负阈值；奖励数0 |

界面没有提供修改 ID、creationDate 的输入，这是自动字段。枚举下拉框也会限制非法枚举。服务端仍必须检查绕过页面直接发送的非法请求。

## 6. 自动更新、并发与账号

用两个不同浏览器，或普通窗口与无痕窗口分别登录 student 和 ivan。普通标签页共享 Cookie，无法隔离两位用户。

1. 两边显示同一电影列表。在一边新建/修改 M31，另一边应在约一个轮询周期后自动更新。
2. 两边同时打开 M31 的编辑表单；A 先保存，B 再保存。B 应得到“对象已被其他用户修改”的冲突提示，旧输入仍保留，不能覆盖 A 的修改。
3. 两边打开列表，在 A 删除 M31，B 的列表应自动移除。
4. 在另一账号中查看、修改同一条样例，验证所有登录用户共用集合；创建者不会独占修改/删除权限。
5. 登出后保护接口应拒绝访问；错误密码不能登录；注册尝试重复用户名、过短密码、密码确认不一致。

以上需要实际交互，导入脚本没有替你执行双浏览器测试或注册新用户。脚本只完成 [verification.json](verification.json) 中明确列出的检查。

## 7. 恢复与重复导入

脚本：`movie-lab/scripts/seed-demo.py`。只用 Python 标准库；输入的是实验网页登录密码，**不是 SSH 密码**。它使用独立 Cookie，不会切换当前浏览器的账号。

在 `Lab1/movie-lab` 目录执行：

```sh
python scripts/seed-demo.py --base http://localhost:18082/movie-lab/ --user student --apply
```

默认保存到本目录。已有 manifest 时继续未完成的导入，已经登记的对象不重复创建、不覆盖用户修改；如果对象已被手动删除，脚本会报错停下，不会偷偷重建旧 ID。

需要重新建立完整的一套时，使用新的输出目录，例如 `--output ../manual-test-data-round2`。这会另外添加 72 个对象，不会清空之前的数据，平均数/全局特殊操作的结果也会变化。没有自动清库或清理命令。

脚本按记录分别提交，整个导入不是单个原子事务。断线时已成功提交的数据保留，manifest 会逐条保存进度；响应丢失导致“服务器已提交但本地未记录”时，应先核对集合再重跑。

## 电影样例与实际 ID

| 代号 | ID | 名称 | 类型 | 时长 | 初始奥斯卡 | 美国票房 |
|---|---|---|---|---:|---:|---:|
{rows}

## 辅助对象与实际 ID

| 代号 | 对象类型 | ID |
|---|---|---|
{auxiliary}
'''
    text = text.replace('[Л1]', manifest['label_prefix'])
    (output / 'README.md').write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://localhost:18082/movie-lab/')
    parser.add_argument('--public-base', help='Public browser URL used in the generated guide.')
    parser.add_argument('--user', default=os.environ.get('MOVIE_USER', 'student'))
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[2] / 'manual-test-data')
    parser.add_argument('--apply', action='store_true', help='Create rows; without this flag only inspect the plan.')
    parser.add_argument('--verify-only', action='store_true', help='Verify existing fixtures and regenerate their guide without creating rows.')
    args = parser.parse_args()
    password = os.environ.get('MOVIE_PASSWORD') or getpass.getpass('Application password (not SSH): ')
    api = Api(args.base)
    session = api.ok('auth', 'POST', {'username': args.user, 'password': password})
    api.csrf = session['csrf']
    before = {kind: api.ok(kind) for kind in ('locations', 'coordinates', 'people')}
    before['movies'] = api.movies()
    print('Current counts:', {kind: len(rows) for kind, rows in before.items()})
    manifest_path = args.output / 'manifest.json'
    if args.verify_only and not manifest_path.exists():
        raise RuntimeError('--verify-only requires an existing manifest.')
    if args.verify_only and args.apply:
        raise RuntimeError('Choose --apply or --verify-only, not both.')
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['base'] != args.base:
            raise RuntimeError('Manifest belongs to another server; use a different --output directory.')
    else:
        marker = 410100013
        occupied = {row['usaBoxOffice'] for row in before['movies']}
        while marker in occupied:
            marker += 1
        manifest = {'base': args.base, 'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'passport_prefix': 'L1DEMO-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S'),
                    'box_office_marker': marker, 'label_prefix': '[Л1]', 'records': {}}
        if args.public_base:
            manifest['public_base'] = args.public_base
        if any(row['name'].startswith('[Л1]') for row in before['movies']):
            manifest['label_prefix'] = '[Л1-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S') + ']'
    prefix = manifest['label_prefix']
    records = fixtures(manifest['passport_prefix'], manifest['box_office_marker'], prefix)
    print('Dataset: 12 locations, 16 coordinates, 12 people, 32 movies.')
    if not args.apply and not args.verify_only:
        print('Read-only plan. Pass --apply to insert the dataset.')
        return
    args.output.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        write_json(args.output / 'before.json', before)
        write_json(manifest_path, manifest)
    for kind, key, template in records:
        if args.verify_only:
            continue
        if key in manifest['records']:
            existing = api.ok(f'{kind}/{manifest["records"][key]["id"]}')
            if any(existing[field] != value for field, value in template.items()
                   if value is None or not isinstance(value, str) or not value.startswith('@')):
                # Numeric API fields may be serialized as strings. Do not overwrite a changed fixture.
                print(f'KEEP {key} #{existing["id"]} (already recorded; no overwrite)')
            continue
        body = {field: manifest['records'][value[1:]]['id']
                if isinstance(value, str) and value.startswith('@') else value
                for field, value in template.items()}
        created = api.ok(kind, 'POST', body)
        manifest['records'][key] = {'kind': kind, 'id': created['id'], 'initial': created}
        write_json(manifest_path, manifest)
        print(f'CREATED {key}: {kind} #{created["id"]}')
    after = {kind: api.ok(kind) for kind in ('locations', 'coordinates', 'people')}
    after['movies'] = api.movies()
    write_json(args.output / 'after.json', after)
    checks = []

    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
        write_json(args.output / 'verification.json', {'date': dt.datetime.now(dt.timezone.utc).isoformat(), 'checks': checks})
        print(('PASS ' if passed else 'FAIL ') + name)
        if not passed:
            raise RuntimeError(name)

    def query(**values):
        return api.ok('movies?' + urllib.parse.urlencode({'size': 100, **values}))

    check('All 72 fixtures persisted', all(
        any(str(row['id']) == str(entry['id']) for row in after[entry['kind']])
        for entry in manifest['records'].values()) and len(manifest['records']) == 72)
    actual_by_id = {kind: {str(row['id']): row for row in rows} for kind, rows in after.items()}
    payloads_match = True
    for kind, key, template in records:
        row = actual_by_id[kind][str(manifest['records'][key]['id'])]
        for field, value in template.items():
            if field == 'birthday':
                continue  # ZonedDateTime normalizes zero seconds; checked separately below.
            if isinstance(value, str) and value.startswith('@'):
                payloads_match &= str(row[field]['id']) == str(manifest['records'][value[1:]]['id'])
            else:
                payloads_match &= row.get(field) == value  # JSON-B omits null-valued properties.
    check('All fixture scalar values and foreign keys match the plan', payloads_match)
    check('Every movie respects USA box office <= known total box office', all(
        row.get('totalBoxOffice') is None or row['usaBoxOffice'] <= row['totalBoxOffice']
        for row in after['movies']))
    check('Fixtures include equal box offices and unknown total box office',
        any(row.get('totalBoxOffice') == row['usaBoxOffice'] for row in after['movies'])
        and any(row.get('totalBoxOffice') is None for row in after['movies']))
    check('Original time-zone identifiers survive persistence',
          actual_by_id['people'][str(manifest['records']['P01']['id'])]['birthday'].endswith('[Europe/Moscow]')
          and actual_by_id['people'][str(manifest['records']['P02']['id'])]['birthday'].endswith('Z')
          and actual_by_id['people'][str(manifest['records']['P03']['id'])]['birthday'].endswith('[Asia/Tokyo]'))
    page = api.ok('movies?size=10&page=1&sort=id')
    check('Second movie page contains ten rows', page['page'] == 1 and len(page['items']) == 10)
    check('Exact duplicate-name filter returns two rows', query(filter='name', value=prefix + ' Двойник')['total'] == 2)
    check('Partial name is not an exact match', query(filter='name', value=prefix + ' Двой')['total'] == 0)
    check('Upper/lowercase names are distinct', query(filter='name', value=prefix + ' Альфа')['total'] == 1
          and query(filter='name', value=prefix + ' альфа')['total'] == 1)
    matching = query(filter='tagline', value='')['items']
    check('Empty-string filter includes boundary movie', any(str(row['id']) == str(manifest['records']['M32']['id']) for row in matching))
    asc, desc = query(sort='id')['items'], query(sort='id', desc='true')['items']
    check('ID sorting reverses direction', [int(r['id']) for r in asc] == sorted(int(r['id']) for r in asc)
          and [int(r['id']) for r in desc] == sorted((int(r['id']) for r in desc), reverse=True)
          and asc[0]['id'] == after['movies'][0]['id'] and desc[0]['id'] == after['movies'][-1]['id'])
    check('Ordinary prefix returns three fixture movies', len(api.ok('operations/prefix?' + urllib.parse.urlencode({'value': prefix + ' Префикс:'}))) == 3)
    check('LIKE metacharacters are literal', len(api.ok('operations/prefix?' + urllib.parse.urlencode({'value': prefix + ' 100%_!'}))) == 1)
    check('Maximum long budget preserves precision', api.ok('movies/' + str(manifest['records']['M32']['id']))['budget'] == '9223372036854775807')
    average = api.ok('operations/average')['average']
    expected_average = sum(r['usaBoxOffice'] for r in after['movies']) / len(after['movies'])
    check('Average matches the entire live collection', abs(average - expected_average) < 0.000001)
    reference = api.ok('movies/' + str(manifest['records']['M01']['id']))
    check('Movie detail expands related entities', isinstance(reference['coordinates'], dict) and isinstance(reference['director'], dict)
          and isinstance(reference['director']['location'], dict))
    for field in ('genre', 'mpaaRating', 'director', 'screenwriter', 'operator'):
        sample_value = next(row.get(field) for row in after['movies'] if row.get(field) is not None)
        value = sample_value['name'] if isinstance(sample_value, dict) else sample_value
        expected_ids = {str(row['id']) for row in after['movies']
                        if (row.get(field, {}).get('name') if isinstance(row.get(field), dict) else row.get(field)) == value}
        filtered = query(filter=field, value=value)
        check(f'Exact {field} filter matches the known collection', filtered['total'] == len(expected_ids)
              and {str(row['id']) for row in filtered['items']} == expected_ids)
    same_names = query(filter='name', value=prefix + ' Двойник', sort='name')['items']
    check('Equal names have stable ID ordering', [int(row['id']) for row in same_names] == sorted(int(row['id']) for row in same_names))
    status, _ = api.call('coordinates', 'POST', {'x': 827, 'y': 1})
    check('Invalid coordinate is rejected', status == 400)
    status, _ = api.call('people', 'POST', {'name': '[Л1] Duplicate rejected',
        'birthday': '1990-01-01T00:00:00Z', 'passportID': manifest['records']['P01']['initial']['passportID']})
    check('Duplicate passport is rejected', status == 409)
    sample = manifest['records']['M31']['initial']
    status, _ = api.call('movies/' + str(sample['id']), 'PUT', {'version': sample['version'] + 999, 'name': 'Must not persist'})
    check('Stale version is rejected', status == 409)
    write_json(args.output / 'verification.json', {'date': dt.datetime.now(dt.timezone.utc).isoformat(), 'checks': checks})
    pool = sum(r['oscarsCount'] - 1 for r in after['movies'] if r.get('genre') == 'WESTERN')
    targets = [r for r in after['movies'] if r.get('genre') == 'COMEDY']
    forecasts = {'movie_count': len(after['movies']), 'average': expected_average,
        'delete_box_office_value': manifest['box_office_marker'],
        'delete_box_office_ids': [r['id'] for r in after['movies'] if r['usaBoxOffice'] == manifest['box_office_marker']],
        'award_length': 120, 'award_count': 2,
        'award_ids': [r['id'] for r in after['movies'] if r['length'] > 120],
        'redistribute': {'from': 'WESTERN', 'to': 'COMEDY', 'transferred': pool,
            'recipients': len(targets), 'each': pool // len(targets), 'remainder': pool % len(targets),
            'target_oscars_after': {str(r['id']): r['oscarsCount'] + pool // len(targets) + (i < pool % len(targets))
                                    for i, r in enumerate(targets)}}}
    write_json(args.output / 'expected-results.json', forecasts)
    write_guide(args.output, manifest, after, forecasts)
    print('Complete. No bulk awards, redistribution or deletion were executed.')


if __name__ == '__main__':
    main()
