"""Minimal arXiv API client: search, and store a reproducible local corpus.

Why a local corpus
------------------
A literature claim that cannot be re-checked later is not evidence.  Every hit is
written to docs/literature/arxiv/<slug>.json with its arXiv id, version, date and
abstract, so the review can be re-derived offline and so a later reader can see
exactly which papers a statement was based on.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "docs" / "literature" / "arxiv"


def _text(node, path, default=""):
    found = node.find(path, NS)
    return (found.text or default).strip() if found is not None else default


def search(query: str, max_results: int = 25, sort: str = "relevance") -> list[dict]:
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": sort,
        "sortOrder": "descending",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "ECDR-literature-review/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        xml = resp.read()

    root = ET.fromstring(xml)
    out = []
    for entry in root.findall("a:entry", NS):
        raw_id = _text(entry, "a:id")
        short = raw_id.rsplit("/", 1)[-1]
        out.append({
            "id": short,
            "title": " ".join(_text(entry, "a:title").split()),
            "abstract": " ".join(_text(entry, "a:summary").split()),
            "published": _text(entry, "a:published")[:10],
            "updated": _text(entry, "a:updated")[:10],
            "authors": [(_text(a, "a:name")) for a in entry.findall("a:author", NS)],
            "primary_category": (entry.find("arxiv:primary_category", NS).get("term")
                                 if entry.find("arxiv:primary_category", NS) is not None else ""),
            "categories": [c.get("term") for c in entry.findall("a:category", NS)],
            "url": f"https://arxiv.org/abs/{short}",
            "pdf": f"https://arxiv.org/pdf/{short}",
            "comment": _text(entry, "arxiv:comment"),
        })
    return out


def slugify(text: str) -> str:
    keep = [c if c.isalnum() or c in "-_." else "-" for c in text]
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")[:80]


def run_batch(queries: dict[str, str], max_results: int = 25, delay: float = 3.2) -> dict:
    CORPUS.mkdir(parents=True, exist_ok=True)
    index = {}
    for slug, query in queries.items():
        try:
            hits = search(query, max_results=max_results)
        except Exception as exc:  # noqa: BLE001 - report and continue the batch
            print(f"  [fail] {slug}: {exc}")
            continue
        (CORPUS / f"{slug}.json").write_text(
            json.dumps({"query": query, "hits": hits}, indent=1, ensure_ascii=False), encoding="utf-8")
        index[slug] = {"query": query, "n": len(hits), "top": [h["id"] for h in hits[:5]]}
        print(f"  [ok]   {slug}: {len(hits)} hits   top: {', '.join(h['id'] for h in hits[:3])}")
        time.sleep(delay)
    (CORPUS / "_index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    return index


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for h in search(" ".join(sys.argv[1:]), max_results=10):
            print(f"{h['id']}  {h['published']}  {h['title']}")
