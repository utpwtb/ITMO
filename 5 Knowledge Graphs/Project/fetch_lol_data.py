#!/usr/bin/env python3
"""采集第一阶段 PPT 所需的 LoL 英雄与技能数据。仅使用 Python 标准库。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DDRAGON = "https://ddragon.leagueoflegends.com"
CDRAGON = "https://raw.communitydragon.org"
WEBSITE = "https://www.leagueoflegends.com"
LOG = logging.getLogger("lol_data")
Json = dict[str, Any]


class CollectionError(Exception):
    """可向命令行用户直接显示的采集错误。"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_bytes(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_bytes(body)
    temporary.replace(path)


def save_json(path: Path, value: Any) -> None:
    save_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def save_csv(path: Path, rows: list[Json], fields: list[str]) -> None:
    """UTF-8 BOM 便于 Windows Excel 正确显示俄语和中文。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                for key, value in row.items() if key in fields
            })
    temporary.replace(path)


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() in {"br", "p", "div", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def plain_text(value: str) -> str:
    parser = TextParser()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


class NextDataParser(HTMLParser):
    """读取官网 HTML 中随页面公开提供的数据，不调用内部 CMS 接口。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "script" and dict(attrs).get("id") == "__NEXT_DATA__":
            self.active = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)


def website_page(body: bytes) -> Json:
    parser = NextDataParser()
    parser.feed(body.decode("utf-8-sig"))
    try:
        return json.loads("".join(parser.parts))["props"]["pageProps"]["page"]
    except (ValueError, KeyError, TypeError) as exc:
        raise CollectionError("官网页面结构已变化：HTML 已保存，但无法提取 __NEXT_DATA__。") from exc


class HttpClient:
    """限速请求、超时重试、线程安全文件缓存以及来源清单。"""

    def __init__(self, root: Path, timeout: float, retries: int, delay: float, refresh: bool) -> None:
        self.root = root
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.refresh = refresh
        self.resources: dict[str, Json] = {}
        self.last_request = 0.0
        self.rate_lock = threading.Lock()
        self.paths_lock = threading.Lock()
        self.path_locks: dict[Path, Any] = {}

    def fetch(self, url: str, path: Path, *, is_json: bool = True, fresh: bool = False) -> Any:
        with self.paths_lock:
            lock = self.path_locks.setdefault(path, threading.Lock())
        with lock:
            return self._fetch(url, path, is_json=is_json, fresh=fresh)

    def _fetch(self, url: str, path: Path, *, is_json: bool, fresh: bool) -> Any:
        sidecar = path.with_name(path.name + ".meta.json")
        if not (self.refresh or fresh) and path.is_file() and sidecar.is_file():
            try:
                body = path.read_bytes()
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
                if meta["url"] == url and meta["sha256"] == hashlib.sha256(body).hexdigest():
                    value = json.loads(body) if is_json else body
                    self.resources[str(path.relative_to(self.root))] = {**meta, "cached": True}
                    return value
            except (OSError, ValueError, KeyError):
                LOG.warning("缓存损坏，重新下载 %s", path.name)

        for attempt in range(self.retries + 1):
            with self.rate_lock:
                wait = self.delay - (time.monotonic() - self.last_request)
                if wait > 0:
                    time.sleep(wait)
                self.last_request = time.monotonic()
            retry_after = None
            try:
                request = Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; LoL-KG-Collector/1.0; educational project)",
                    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
                })
                with urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                    value = json.loads(body) if is_json else body
                    meta = {
                        "url": url, "retrieved_at": utc_now(), "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(),
                        "etag": response.headers.get("ETag"),
                        "last_modified": response.headers.get("Last-Modified"),
                    }
                save_bytes(path, body)
                save_json(sidecar, meta)
                self.resources[str(path.relative_to(self.root))] = {**meta, "cached": False}
                return value
            except HTTPError as exc:
                error = f"HTTP {exc.code}: {url}"
                can_retry = exc.code in {408, 429, 500, 502, 503, 504}
                header = exc.headers.get("Retry-After")
                exc.close()
                if header:
                    try:
                        retry_after = float(header)
                    except ValueError:
                        try:
                            retry_after = (parsedate_to_datetime(header) - datetime.now(timezone.utc)).total_seconds()
                        except (ValueError, TypeError, OverflowError):
                            pass
            except (URLError, TimeoutError, OSError, ValueError, HTTPException) as exc:
                error = f"{type(exc).__name__}: {exc} ({url})"
                can_retry = True
            if not can_retry or attempt == self.retries:
                raise CollectionError(error)
            # 不超过 60 秒的阻塞等待。服务器要求更长等待时停止本次请求。
            if retry_after is not None and retry_after > 60:
                raise CollectionError(f"{error}; 服务器要求等待 {retry_after:.0f} 秒，请稍后重跑。")
            wait = max(0, retry_after) if retry_after is not None else min(2 ** attempt, 30)
            LOG.warning("%s；%.1f 秒后重试 (%d/%d)", error, wait, attempt + 1, self.retries)
            time.sleep(wait)
        raise CollectionError(f"无法获取 {url}")


def resolve_version(client: HttpClient, requested: str | None) -> str:
    lock_path = client.root / "version-lock.json"
    if requested is None and lock_path.exists():
        version = json.loads(lock_path.read_text(encoding="utf-8"))["ddragon_version"]
        if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise CollectionError("version-lock.json 中的版本无效。")
        return version
    if requested and requested != "latest" and not re.fullmatch(r"\d+\.\d+\.\d+", requested):
        raise CollectionError("--version 应为完整版本（例如 16.20.1）或 latest。")
    versions = client.fetch(f"{DDRAGON}/api/versions.json", client.root / "catalog/versions.json", fresh=True)
    if not isinstance(versions, list) or not versions:
        raise CollectionError("Data Dragon 版本列表为空或格式异常。")
    version = versions[0] if requested in {None, "latest"} else requested
    if version not in versions:
        raise CollectionError(f"Data Dragon 不存在版本 {version}。")
    save_json(lock_path, {"ddragon_version": version, "locked_at": utc_now()})
    return version


def check_ddragon(payload: Json, version: str, champion_id: str | None = None) -> Json:
    if payload.get("version") != version or not isinstance(payload.get("data"), dict):
        raise CollectionError(f"Data Dragon 响应版本或结构不符，要求版本 {version}。")
    if champion_id is None:
        if not payload["data"]:
            raise CollectionError("Data Dragon 英雄列表为空。")
        return payload["data"]
    champion = payload["data"].get(champion_id)
    if not isinstance(champion, dict) or champion.get("id") != champion_id:
        raise CollectionError(f"英雄详情 ID 不匹配：{champion_id}。")
    if not champion.get("passive") or not champion.get("spells"):
        raise CollectionError(f"英雄详情缺少技能：{champion_id}。")
    return champion


def select_champions(roster: Json, requested: list[str] | None) -> list[str]:
    if not requested:
        return sorted(roster)
    lookup: dict[str, str] = {}
    for champion_id, champion in roster.items():
        for token in (champion_id, str(champion["key"]), champion["name"]):
            lookup[token.casefold()] = champion_id
    result = set()
    for value in requested:
        champion_id = lookup.get(value.casefold())
        if champion_id is None:
            raise CollectionError(f"找不到英雄 {value!r}。请使用英文 ID、数字 key 或当前语言名称。")
        result.add(champion_id)
    return sorted(result)


def normalize_champion(champion: Json, version: str, locale: str, source_url: str) -> tuple[Json, list[Json]]:
    champion_id = champion["id"]
    image = champion.get("image", {}).get("full")
    record = {
        "champion_id": champion_id, "champion_key": int(champion["key"]),
        "name": champion["name"], "title": champion.get("title", ""),
        "classes": champion.get("tags", []), "stats": champion.get("stats", {}),
        "info": champion.get("info", {}), "resource_type": champion.get("partype", ""),
        "lore": plain_text(champion.get("lore", "")),
        "ally_tips": champion.get("allytips", []), "enemy_tips": champion.get("enemytips", []),
        "icon_url": f"{DDRAGON}/cdn/{version}/img/champion/{image}" if image else None,
        "version": version, "locale": locale, "source_url": source_url,
    }
    abilities = []
    for index, skill in enumerate([champion["passive"], *champion["spells"]]):
        # Data Dragon 的四个 spells 按 Q/W/E/R 排列。变身及子技能仍保留在原始 JSON 中。
        slot = ("P", "Q", "W", "E", "R")[index] if index < 5 else f"EXTRA_{index}"
        description = skill.get("description", "")
        tooltip = skill.get("tooltip", "")
        icon = skill.get("image", {}).get("full")
        group = "passive" if slot == "P" else "spell"
        abilities.append({
            "ability_id": f"{champion_id}:{slot}", "champion_id": champion_id,
            "champion_name": champion["name"], "slot": slot, "kind": "passive" if index == 0 else "active",
            "name": skill.get("name", ""), "spell_id": skill.get("id"),
            "description_html": description, "description_text": plain_text(description),
            "tooltip_html": tooltip, "tooltip_text": plain_text(tooltip),
            "unresolved_placeholders": sorted(set(re.findall(r"\{\{\s*(.*?)\s*\}\}", description + " " + tooltip))),
            "max_rank": skill.get("maxrank"), "cooldown": skill.get("cooldown"),
            "cost": skill.get("cost"), "range": skill.get("range"),
            "resource": skill.get("resource"), "effect": skill.get("effect"),
            "effect_burn": skill.get("effectBurn"), "vars": skill.get("vars"),
            "icon_url": f"{DDRAGON}/cdn/{version}/img/{group}/{icon}" if icon else None,
            "version": version, "locale": locale, "source_url": source_url,
        })
    return record, abilities


def collect_cdragon(client: HttpClient, raw: Path, champion: Json, version: str, locale: str,
                    metadata: Json | None = None) -> Json:
    patch = ".".join(version.split(".")[:2])
    base = f"{CDRAGON}/{patch}"
    if metadata is None:
        metadata = client.fetch(f"{base}/content-metadata.json", raw / "communitydragon/content-metadata.json")
    actual = metadata.get("version", "")
    if not actual.startswith(patch + "."):
        raise CollectionError(f"CommunityDragon 版本不符：{actual!r}，要求 {patch}。")
    # en_US 在 CDragon 中使用 default；其余语言严格请求本地化数据，不静默回退到英语。
    language = "default" if locale == "en_US" else locale.lower()
    url = f"{base}/plugins/rcp-be-lol-game-data/global/{language}/v1/champions/{champion['champion_key']}.json"
    data = client.fetch(url, raw / f"communitydragon/{champion['champion_id']}.json")
    if str(data.get("id")) != str(champion["champion_key"]):
        raise CollectionError(f"CommunityDragon 英雄 ID 不符：{champion['champion_id']}。")
    return {
        "champion_id": champion["champion_id"], "patch": patch, "client_content_version": actual,
        "locale": locale, "source_url": url,
        "roles": data.get("roles", []), "tactical_info": data.get("tacticalInfo", {}),
        "playstyle_info": data.get("playstyleInfo", {}), "champion_tag_info": data.get("championTagInfo", {}),
        "passive": data.get("passive"), "spells": data.get("spells", []),
    }


def website_links(page: Json, locale: str) -> Json:
    prefix = f"/{locale.replace('_', '-').lower()}/champions/"
    links = {}
    for blade in page.get("blades", []):
        for item in blade.get("items", []):
            url = urljoin(WEBSITE, item.get("action", {}).get("payload", {}).get("url", ""))
            parsed = urlparse(url)
            if parsed.netloc == "www.leagueoflegends.com" and parsed.path.startswith(prefix):
                links[item.get("title", "").casefold()] = url
    if not links:
        raise CollectionError("官网列表未找到英雄链接，可能需要更新页面解析器。")
    return links


def collect_official(client: HttpClient, raw: Path, champion: Json, url: str) -> Json:
    body = client.fetch(url, raw / f"official/{champion['champion_id']}.html", is_json=False)
    page = website_page(body)
    result = {
        "champion_id": champion["champion_id"], "source_url": url,
        "locale": page.get("locale"), "version_status": "unversioned_current_website",
        "name": None, "roles": [], "abilities": [],
    }
    for blade in page.get("blades", []):
        if blade.get("type") == "characterMasthead":
            result["name"] = blade.get("title")
            result["roles"] = blade.get("role", {}).get("roles", [])
        if blade.get("fragmentId") == "abilities":
            for group in blade.get("groups", []):
                content = group.get("content", {})
                description = content.get("description", {}).get("body", "")
                result["abilities"].append({
                    "name": content.get("title"), "slot_label": content.get("subtitle"),
                    "description_html": description, "description_text": plain_text(description),
                    "icon_url": group.get("thumbnail", {}).get("url"),
                })
    if not result["name"] or not result["abilities"]:
        raise CollectionError(f"官网详情结构变化：{champion['champion_id']}，原始 HTML 已保存。")
    return result


def export_dataset(output: Path, champions: list[Json], abilities: list[Json]) -> None:
    save_json(output / "champions.json", champions)
    save_json(output / "abilities.json", abilities)
    champion_fields = ["champion_id", "champion_key", "name", "title", "classes", "resource_type", "icon_url", "version", "locale", "source_url"]
    stat_names = sorted({key for champion in champions for key in champion["stats"]})
    save_csv(output / "champions.csv", [{**c, **c["stats"]} for c in champions], champion_fields + stat_names)
    save_csv(output / "abilities.csv", abilities, [
        "ability_id", "champion_id", "champion_name", "slot", "kind", "name", "spell_id",
        "description_text", "tooltip_text", "unresolved_placeholders", "cooldown", "cost", "range",
        "icon_url", "version", "locale", "source_url",
    ])
    relations = [
        {"champion_id": c["champion_id"], "class": tag, "version": c["version"], "source_url": c["source_url"]}
        for c in champions for tag in c["classes"]
    ]
    save_csv(output / "champion_classes.csv", relations, ["champion_id", "class", "version", "source_url"])
    # 保留已有人工编辑，只为本次新获取的技能追加待核验行。
    review = output / "mechanics_review.csv"
    fields = [
        "ability_id", "champion_id", "champion_name", "slot", "name", "evidence_text",
        "mechanic", "target", "condition", "review_status", "reviewer", "notes", "source_url", "version", "locale",
    ]
    rows: list[Json] = []
    if review.exists():
        with review.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = list(dict.fromkeys([*(reader.fieldnames or []), *fields]))
            rows = list(reader)
    existing = {row.get("ability_id") for row in rows}
    additions = [{
            **a, "evidence_text": a["description_text"], "mechanic": "", "target": "",
            "condition": "", "review_status": "pending", "reviewer": "", "notes": "",
        } for a in abilities if a["ability_id"] not in existing]
    if additions or not review.exists():
        save_csv(review, rows + additions, fields)


def run(args: argparse.Namespace) -> int:
    root = args.output.expanduser().resolve()
    client = HttpClient(root, args.timeout, args.retries, args.delay, args.refresh)
    version = resolve_version(client, args.version)
    languages = client.fetch(f"{DDRAGON}/cdn/languages.json", root / "catalog/languages.json")
    if args.locale not in languages:
        raise CollectionError(f"不支持的语言 {args.locale}。可用语言：{', '.join(languages)}")
    locale_dir = root / version / args.locale
    raw = locale_dir / "raw"
    base = f"{DDRAGON}/cdn/{version}/data/{args.locale}"
    roster = check_ddragon(client.fetch(f"{base}/champion.json", raw / "ddragon/champion.json"), version)
    selected = select_champions(roster, args.champions)
    selection = "all" if len(selected) == len(roster) else "subset-" + hashlib.sha256(
        ",".join(selected).encode("utf-8")).hexdigest()[:12]
    output = locale_dir / selection
    output.mkdir(parents=True, exist_ok=True)
    LOG.info("固定版本 %s，语言 %s，共 %d 个英雄", version, args.locale, len(selected))
    errors: list[Json] = []
    champions: list[Json] = []
    abilities: list[Json] = []
    cdragon: list[Json] = []
    official: list[Json] = []
    links = {}
    cdragon_metadata = None

    def record_error(source: str, champion_id: str | None, exc: Exception) -> None:
        errors.append({"source": source, "champion_id": champion_id, "error": str(exc)})
        LOG.error("%s %s: %s", source, champion_id or "", exc)

    if args.community_dragon:
        try:
            patch = ".".join(version.split(".")[:2])
            cdragon_metadata = client.fetch(f"{CDRAGON}/{patch}/content-metadata.json",
                                           raw / "communitydragon/content-metadata.json")
            if not str(cdragon_metadata.get("version", "")).startswith(patch + "."):
                raise CollectionError(f"CommunityDragon 构建信息与补丁 {patch} 不匹配。")
        except CollectionError as exc:
            record_error("communitydragon_metadata", None, exc)
            cdragon_metadata = None

    if args.official_pages:
        try:
            url = f"{WEBSITE}/{args.locale.replace('_', '-').lower()}/champions/"
            page = website_page(client.fetch(url, raw / "official/index.html", is_json=False))
            links = website_links(page, args.locale)
        except CollectionError as exc:
            record_error("official_index", None, exc)

    def collect_one(entry: tuple[int, str]) -> tuple:
        index, champion_id = entry
        local_errors: list[Json] = []
        supplement = None
        official_page = None

        def failed(source: str, exc: Exception) -> None:
            local_errors.append({"source": source, "champion_id": champion_id, "error": str(exc)})
            LOG.error("%s %s: %s", source, champion_id, exc)

        LOG.info("[%d/%d] %s", index, len(selected), champion_id)
        try:
            url = f"{base}/champion/{champion_id}.json"
            data = check_ddragon(client.fetch(url, raw / f"ddragon/champions/{champion_id}.json"), version, champion_id)
            champion, skills = normalize_champion(data, version, args.locale, url)
        except CollectionError as exc:
            failed("ddragon", exc)
            return None, [], None, None, local_errors

        if args.community_dragon and cdragon_metadata is not None:
            try:
                supplement = collect_cdragon(client, raw, champion, version, args.locale, cdragon_metadata)
            except CollectionError as exc:
                failed("communitydragon", exc)

        if args.official_pages and links:
            try:
                # 按列表中的本地化名称匹配，避免 MonkeyKing/Wukong 等 ID 与网址差异。
                url = links.get(champion["name"].casefold())
                if not url:
                    raise CollectionError("官网列表没有同名英雄，需人工核对名称或历史版本差异。")
                official_page = collect_official(client, raw, champion, url)
            except CollectionError as exc:
                failed("official", exc)

        if args.download_images:
            for item in [champion, *skills]:
                url = item.get("icon_url")
                if url:
                    try:
                        client.fetch(url, locale_dir / "images" / "/".join(urlparse(url).path.split("/")[-2:]), is_json=False)
                    except CollectionError as exc:
                        failed("image", exc)
        return champion, skills, supplement, official_page, local_errors

    pool = ThreadPoolExecutor(max_workers=args.workers)
    try:
        for champion, skills, supplement, official_page, local_errors in pool.map(collect_one, enumerate(selected, 1)):
            if champion is not None:
                champions.append(champion)
                abilities.extend(skills)
            if supplement is not None:
                cdragon.append(supplement)
            if official_page is not None:
                official.append(official_page)
            errors.extend(local_errors)
    finally:
        # Ctrl+C 或意外异常时取消排队任务，只等待已经开始的请求结束。
        pool.shutdown(wait=True, cancel_futures=True)

    export_dataset(output, champions, abilities)
    # 每次运行单独记录补充来源，未请求的来源不沿用旧导出结果。
    save_json(output / "communitydragon.json", cdragon)
    save_json(output / "official_pages.json", official)
    save_json(output / "errors.json", errors)
    save_json(output / "manifest.json", {
        "schema_version": 1, "finished_at": utc_now(), "ddragon_version": version,
        "communitydragon_patch": ".".join(version.split(".")[:2]) if args.community_dragon else None,
        "locale": args.locale, "requested_champions": selected,
        "counts": {"champions": len(champions), "abilities": len(abilities),
                   "communitydragon": len(cdragon), "official_pages": len(official), "errors": len(errors)},
        "options": {"community_dragon": args.community_dragon, "official_pages": args.official_pages,
                    "download_images": args.download_images, "workers": args.workers},
        "complete": not errors,
        "notes": [
            "Data Dragon tags 表示英雄分类，不是上路/打野等分路。",
            "官网为无历史版本保证的当前页面，仅用于核对，不自动覆盖固定版本数据。",
            "CommunityDragon 仅核对同一 major.minor 补丁及英雄 ID，不保证与 Data Dragon 构建完全相同。",
            "技能机制和对象/条件需人工核验；tooltip 的 {{...}} 变量保留，不猜测数值。",
            "Data Dragon 只提供主要 P/Q/W/E/R；变身、子技能可能需要补充来源或人工整理。",
            "mechanics_review.csv 保留人工编辑，仅追加新获取技能的待核验行。",
        ],
        "resources": [{"path": path, **meta} for path, meta in sorted(client.resources.items())],
        "errors": errors,
    })
    LOG.info("已保存 %d 个英雄、%d 个技能；输出目录：%s", len(champions), len(abilities), output)
    if errors:
        LOG.warning("有 %d 项失败，详见 errors.json。重跑相同命令可复用已下载内容。", len(errors))
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "data", help="数据根目录")
    parser.add_argument("--version", help="Data Dragon 版本；首次自动选最新并锁定，以后沿用锁定版本；latest 可更新锁")
    parser.add_argument("--locale", default="ru_RU", help="数据语言，PPT 要求俄语")
    parser.add_argument("--champions", nargs="+", help="仅采集指定英雄，可用英文 ID、数字 key 或本地化名称")
    parser.add_argument("--community-dragon", action="store_true", help="采集同补丁 CommunityDragon 补充 JSON")
    parser.add_argument("--official-pages", action="store_true", help="采集当前官网 HTML、分类与技能描述供人工核对")
    parser.add_argument("--download-images", action="store_true", help="下载英雄和 P/Q/W/E/R 图标；默认仅保存 URL")
    parser.add_argument("--refresh", action="store_true", help="重新下载原始数据，不覆盖人工机制核验表")
    parser.add_argument("--workers", type=int, default=4, help="同时采集的英雄数量（1-8）")
    parser.add_argument("--timeout", type=float, default=25, help="每次网络请求超时秒数")
    parser.add_argument("--retries", type=int, default=2, help="失败后的最大重试次数")
    parser.add_argument("--delay", type=float, default=0.15, help="两次网络请求的最短间隔秒数")
    args = parser.parse_args()
    if args.timeout <= 0 or args.retries < 0 or args.delay < 0:
        parser.error("timeout 必须大于 0，retries 和 delay 必须大于等于 0。")
    if not 1 <= args.workers <= 8:
        parser.error("workers 必须为 1 到 8。")
    if not re.fullmatch(r"[a-z]{2}_[A-Z]{2}", args.locale):
        parser.error("locale 格式应为 ru_RU、zh_CN 或 en_US。")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        return run(args)
    except (CollectionError, OSError, ValueError, KeyError, TypeError) as exc:
        LOG.error("采集终止：%s", exc)
        return 1
    except KeyboardInterrupt:
        LOG.warning("采集已中断。已下载的原始文件保留，重跑可继续。")
        return 130


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
