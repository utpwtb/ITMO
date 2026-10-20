"""离线验证：版本隔离、数据保真、恢复采集和人工标注保护。"""

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import fetch_lol_data as app


def sample_champion():
    return {
        "id": "Lux", "key": "99", "name": "Люкс", "tags": ["Mage", "Support"],
        "stats": {"hp": 580}, "image": {"full": "Lux.png"},
        "passive": {"name": "Иллюминация", "description": "<b>Свет</b><br>Урон"},
        "spells": [{"id": "LuxQ", "name": "Q", "description": "Обездвиживает врагов.",
                    "tooltip": "<status>Контроль</status> {{ rootduration }} сек.",
                    "cooldown": [10], "cost": [50], "range": [1175]}],
    }


class FakeResponse(io.BytesIO):
    def __init__(self, body=b'{"ok": true}'):
        super().__init__(body)
        self.headers = {"ETag": "example"}


class CollectorTests(unittest.TestCase):
    def test_localized_text_and_unresolved_values_are_preserved(self):
        champion, abilities = app.normalize_champion(sample_champion(), "16.20.1", "ru_RU", "https://source")
        self.assertEqual(champion["champion_key"], 99)
        self.assertEqual(champion["classes"], ["Mage", "Support"])
        self.assertEqual(abilities[0]["description_text"], "Свет Урон")
        self.assertEqual(abilities[1]["unresolved_placeholders"], ["rootduration"])
        self.assertIn("{{ rootduration }}", abilities[1]["tooltip_text"])
        self.assertEqual([a["ability_id"] for a in abilities], ["Lux:P", "Lux:Q"])

    def test_wrong_source_version_is_rejected(self):
        with self.assertRaises(app.CollectionError):
            app.check_ddragon({"version": "16.19.1", "data": {"Lux": sample_champion()}}, "16.20.1", "Lux")

    def test_selection_accepts_name_id_and_key_but_rejects_typos(self):
        roster = {"Lux": sample_champion()}
        self.assertEqual(app.select_champions(roster, ["lux", "99", "Люкс"]), ["Lux"])
        with self.assertRaises(app.CollectionError):
            app.select_champions(roster, ["Lxu"])

    def test_locked_version_does_not_drift_to_latest(self):
        with tempfile.TemporaryDirectory() as folder:
            client = app.HttpClient(Path(folder), 1, 0, 0, False)
            app.save_json(client.root / "version-lock.json", {"ddragon_version": "16.19.1"})
            with patch.object(client, "fetch") as fetch:
                self.assertEqual(app.resolve_version(client, None), "16.19.1")
                fetch.assert_not_called()

    def test_cache_hash_and_url_checked_and_corruption_refetched(self):
        with tempfile.TemporaryDirectory() as folder:
            client = app.HttpClient(Path(folder), 1, 0, 0, False)
            target = client.root / "raw.json"
            with patch.object(app, "urlopen", return_value=FakeResponse()) as request:
                self.assertEqual(client.fetch("https://example.test/a", target), {"ok": True})
                self.assertEqual(client.fetch("https://example.test/a", target), {"ok": True})
                self.assertEqual(request.call_count, 1)
            target.write_bytes(b'{"ok": false}')
            with patch.object(app, "urlopen", return_value=FakeResponse()) as request:
                self.assertEqual(client.fetch("https://example.test/a", target), {"ok": True})
                request.assert_called_once()
            with patch.object(app, "urlopen", return_value=FakeResponse()) as request:
                client.fetch("https://example.test/b", target)
                request.assert_called_once()

    def test_transient_failure_retries_but_404_does_not(self):
        with tempfile.TemporaryDirectory() as folder:
            client = app.HttpClient(Path(folder), 1, 2, 0, False)
            with patch.object(app, "urlopen", side_effect=[URLError("offline"), FakeResponse()]) as request:
                with patch.object(app.time, "sleep"):
                    self.assertEqual(client.fetch("https://example.test/a", client.root / "a.json"), {"ok": True})
                self.assertEqual(request.call_count, 2)
            error = HTTPError("https://example.test/missing", 404, "missing", {}, None)
            with patch.object(app, "urlopen", side_effect=error) as request:
                with self.assertRaises(app.CollectionError):
                    client.fetch("https://example.test/missing", client.root / "missing.json")
                request.assert_called_once()

    def test_parallel_requests_for_same_file_share_one_validated_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            client = app.HttpClient(Path(folder), 1, 0, 0, False)
            with patch.object(app, "urlopen", return_value=FakeResponse()) as request:
                with app.ThreadPoolExecutor(max_workers=4) as pool:
                    values = list(pool.map(lambda _: client.fetch("https://example.test/a", client.root / "a.json"), range(8)))
                self.assertEqual(values, [{"ok": True}] * 8)
                request.assert_called_once()

    def test_resume_keeps_manual_annotations_and_adds_missing_abilities(self):
        champion, abilities = app.normalize_champion(sample_champion(), "16.20.1", "ru_RU", "https://source")
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            app.export_dataset(output, [champion], abilities[:1])
            review = output / "mechanics_review.csv"
            with review.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                fields = reader.fieldnames
                rows = list(reader)
            rows[0]["review_status"] = "verified"
            rows[0]["notes"] = "保留人工核验"
            rows.append({**rows[0], "mechanic": "second mechanic"})
            app.save_csv(review, rows, fields)
            app.export_dataset(output, [champion], abilities)
            with review.open(encoding="utf-8-sig", newline="") as stream:
                result = list(csv.DictReader(stream))
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["notes"], "保留人工核验")
            self.assertEqual(result[0]["review_status"], "verified")
            self.assertEqual(result[-1]["ability_id"], "Lux:Q")
            self.assertEqual(result[-1]["review_status"], "pending")

    def test_website_links_use_real_localized_names_not_ddragon_slugs(self):
        page = {"blades": [{"items": [{"title": "Вуконг", "action": {"payload": {
            "url": "/ru-ru/champions/wukong/"}}}]}]}
        self.assertEqual(app.website_links(page, "ru_RU")["вуконг"],
                         "https://www.leagueoflegends.com/ru-ru/champions/wukong/")
        encoded = json.dumps({"props": {"pageProps": {"page": page}}})
        self.assertEqual(app.website_page(f'<script id="__NEXT_DATA__">{encoded}</script>'.encode()), page)
        with self.assertRaises(app.CollectionError):
            app.website_page(b"<html>No next data</html>")

    def test_cdragon_patch_mismatch_rejected_before_champion_request(self):
        with tempfile.TemporaryDirectory() as folder:
            client = app.HttpClient(Path(folder), 1, 0, 0, False)
            with patch.object(client, "fetch", return_value={"version": "16.19.123"}) as fetch:
                with self.assertRaises(app.CollectionError):
                    app.collect_cdragon(client, client.root, {"champion_key": 99}, "16.20.1", "ru_RU")
                fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
